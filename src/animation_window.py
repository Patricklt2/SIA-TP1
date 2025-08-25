import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares
from src.run_sokoban.search_algorithms.bfs import bfs
from src.run_sokoban.search_algorithms.dfs import dfs
from src.run_sokoban.search_algorithms.iddfs import iddfs
from src.run_sokoban.search_algorithms.astar import astar
from src.run_sokoban.search_algorithms.ggs import ggs
from src.run_sokoban.search_algorithms.heuristics import manhattan_heuristic, heuristic_boxes_out, player_boxes

class AnimationWindow:
    def __init__(self, master, sokoban_map, solution_moves):
        self.master = master
        master.title("Sokoban Animation")
        
        self.sokoban_map = sokoban_map
        self.solution_moves = solution_moves
        self.current_step = 0
        self.animation_speed = tk.IntVar(value=500)  # ms between moves
        
        # Create animation canvas
        self.canvas = tk.Canvas(master, width=600, height=400, bg='white')
        self.canvas.pack(pady=10)
        
        # Create controls
        control_frame = tk.Frame(master)
        control_frame.pack(pady=5)
        
        self.play_button = tk.Button(control_frame, text="Play", command=self.play_animation)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(control_frame, text="Pause", command=self.pause_animation)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_animation)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.step_button = tk.Button(control_frame, text="Step", command=self.step_animation)
        self.step_button.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = tk.Frame(master)
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        tk.Scale(speed_frame, from_=50, to=1000, orient=tk.HORIZONTAL, 
                variable=self.animation_speed, showvalue=True).pack(side=tk.LEFT)
        
        # Step counter
        self.step_label = tk.Label(master, text=f"Step: 0/{len(self.solution_moves)}")
        self.step_label.pack()
        
        # Initialize animation
        self.animation_id = None
        # Convert frozenset to set for mutable operations
        boxes_set = set(self.sokoban_map.boxes)
        self.current_state = SokobanState(self.sokoban_map.player, boxes_set)
        self.draw_map()
    
    def draw_map(self):
        self.canvas.delete("all")
        
        walls, floors, goals = self.sokoban_map.walls, self.sokoban_map.floors, self.sokoban_map.goals
        boxes, player = self.current_state.boxes, self.current_state.player
        
        # Calculate cell size based on map dimensions
        min_r = min(r for r, c in floors | walls)
        max_r = max(r for r, c in floors | walls)
        min_c = min(c for r, c in floors | walls)
        max_c = max(c for r, c in floors | walls)
        
        rows = max_r - min_r + 1
        cols = max_c - min_c + 1
        
        cell_size = min(400 // rows, 600 // cols, 40)
        
        # Calculate offset to center the map
        offset_x = (600 - cols * cell_size) // 2
        offset_y = (400 - rows * cell_size) // 2
        
        # Draw the map
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                pos = (r, c)
                x1 = offset_x + (c - min_c) * cell_size
                y1 = offset_y + (r - min_r) * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Draw floor
                if pos in floors:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='lightgray')
                
                # Draw walls
                if pos in walls:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='gray', outline='black')
                
                # Draw goals
                if pos in goals:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill='lightgreen', outline='green')
                
                # Draw boxes
                if pos in boxes:
                    color = 'red' if pos in goals else 'orange'
                    self.canvas.create_rectangle(x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill=color, outline='brown')
                
                # Draw player
                if pos == player:
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill='blue', outline='darkblue')
    
    def play_animation(self):
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
        
        if self.current_step < len(self.solution_moves):
            self.step_animation()
            self.animation_id = self.master.after(self.animation_speed.get(), self.play_animation)
    
    def pause_animation(self):
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None
    
    def reset_animation(self):
        self.pause_animation()
        self.current_step = 0
        # Convert frozenset to set for mutable operations
        boxes_set = set(self.sokoban_map.boxes)
        self.current_state = SokobanState(self.sokoban_map.player, boxes_set)
        self.draw_map()
        self.step_label.config(text=f"Step: 0/{len(self.solution_moves)}")
    
    def step_animation(self):
        if self.current_step < len(self.solution_moves):
            move = self.solution_moves[self.current_step]
            self.apply_move(move)
            self.current_step += 1
            self.step_label.config(text=f"Step: {self.current_step}/{len(self.solution_moves)}")
            self.draw_map()
    
    def apply_move(self, move):
        # Convert move direction to coordinate changes
        direction_map = {
            'Up': (-1, 0),
            'Down': (1, 0),
            'Left': (0, -1),
            'Right': (0, 1)
        }
        
        if move in direction_map:
            dr, dc = direction_map[move]
            new_player_pos = (self.current_state.player[0] + dr, self.current_state.player[1] + dc)
            
            # Check if the move pushes a box
            if new_player_pos in self.current_state.boxes:
                new_box_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
                # Update box position - convert to set, modify, then convert back if needed
                boxes_set = set(self.current_state.boxes)
                boxes_set.remove(new_player_pos)
                boxes_set.add(new_box_pos)
                self.current_state.boxes = boxes_set
            
            # Update player position
            self.current_state.player = new_player_pos