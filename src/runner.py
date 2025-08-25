import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares
from src.run_sokoban.search_algorithms.bfs import bfs
from src.run_sokoban.search_algorithms.dfs import dfs
from src.run_sokoban.search_algorithms.iddfs import iddfs
from src.run_sokoban.search_algorithms.astar import astar
from src.run_sokoban.search_algorithms.ggs import ggs
from src.run_sokoban.search_algorithms.heuristics import manhattan_heuristic, heuristic_boxes_out, player_boxes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SokobanGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sokoban Solver")

        self.algo_map = {
            "BFS": lambda s: bfs(s, self.sokoban_map.goals, self.sokoban_map, self.dead_squares),
            "DFS": lambda s: dfs(s, self.sokoban_map.goals, self.sokoban_map, self.dead_squares),
            "IDDFS": lambda s: iddfs(s, self.sokoban_map, self.dead_squares, 1000),
            "A*": lambda s: astar(s, self.sokoban_map, self.get_heuristic(), self.dead_squares),
            "GGS": lambda s: ggs(s, self.sokoban_map, self.get_heuristic(), self.dead_squares)
        }

        self.map_text = tk.Text(master, width=40, height=20, font=("Courier", 14))
        self.map_text.grid(row=0, column=0, columnspan=4)

        self.select_button = tk.Button(master, text="Select Map", command=self.select_map)
        self.select_button.grid(row=1, column=0)

        self.run_all_button = tk.Button(master, text="Run All Algorithms", command=self.run_all_algorithms)
        self.run_all_button.grid(row=1, column=1)

        self.run_selected_button = tk.Button(master, text="Run Selected Algorithm", command=self.run_selected_algorithm)
        self.run_selected_button.grid(row=1, column=2)

        self.algo_var = tk.StringVar(value="A*")
        self.algo_menu = ttk.Combobox(master, textvariable=self.algo_var, values=["BFS", "DFS", "IDDFS", "A*", "GGS"])
        self.algo_menu.grid(row=1, column=3)

        self.heuristic_var = tk.StringVar(value="manhattan_heuristic")
        self.heuristic_menu = ttk.Combobox(master, textvariable=self.heuristic_var,
                                           values=["manhattan_heuristic", "heuristic_boxes_out", "player_boxes"])
        self.heuristic_menu.grid(row=2, column=3)

        self.results_text = tk.Text(master, width=80, height=20)
        self.results_text.grid(row=3, column=0, columnspan=4)

        self.sokoban_map = None
        self.dead_squares = None
        self.initial_state = None

    def display_map(self):
        self.map_text.delete("1.0", tk.END)

        w = int(self.map_text['width'])
        h = int(self.map_text['height'])
        walls, floors, goals, boxes, player = self.sokoban_map.walls, self.sokoban_map.floors, self.sokoban_map.goals, self.sokoban_map.boxes, self.sokoban_map.player

        min_r = min(r for r, c in floors | walls)
        max_r = max(r for r, c in floors | walls)
        min_c = min(c for r, c in floors | walls)
        max_c = max(c for r, c in floors | walls)

        top_pad = max((h - (max_r - min_r + 1)) // 2, 0)
        left_pad = max((w - (max_c - min_c + 1)) // 2, 0)

        self.map_text.tag_configure("wall", foreground="gray")
        self.map_text.tag_configure("player", foreground="blue")
        self.map_text.tag_configure("box", foreground="orange")
        self.map_text.tag_configure("goal", foreground="green")
        self.map_text.tag_configure("box_on_goal", foreground="red")

        lines = [" " * w] * top_pad
        for r in range(min_r, max_r + 1):
            line = " " * left_pad
            for c in range(min_c, max_c + 1):
                pos = (r, c)
                if pos in walls: line += "#"
                elif pos == player: line += "@"
                elif pos in boxes: line += "*" if pos in goals else "$"
                elif pos in goals: line += "."
                else: line += " "
            lines.append(line.ljust(w))
        full_text = "\n".join(lines) + "\n"
        self.map_text.insert(tk.END, full_text)

        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                tag = {"#":"wall","@":"player","$":"box",".":"goal","*":"box_on_goal"}.get(char)
                if tag: self.map_text.tag_add(tag, f"{r+1}.{c}", f"{r+1}.{c+1}")

    def select_map(self):
        filepath = filedialog.askopenfilename(initialdir=os.path.join(BASE_DIR, "maps"),
                                              filetypes=[("Text files", "*.txt")])
        if not filepath:
            return
        self.sokoban_map = parse_map(filepath)
        self.dead_squares = precompute_dead_squares(self.sokoban_map)
        self.initial_state = SokobanState(self.sokoban_map.player, self.sokoban_map.boxes)
        self.display_map()

    def get_heuristic(self):
        if self.heuristic_var.get() == "manhattan_heuristic":
            return manhattan_heuristic
        elif self.heuristic_var.get() == "heuristic_boxes_out":
            return heuristic_boxes_out
        elif self.heuristic_var.get() == "player_boxes":
            return player_boxes
        else:
            return manhattan_heuristic

    def run_algorithm(self, name, algo):
        result = algo(self.initial_state)
        self.results_text.insert(tk.END, f"=== {name} ===\n")
        self.results_text.insert(tk.END, f"Result: {result['result']}\n")
        self.results_text.insert(tk.END, f"Solution cost: {result['cost']}\n")
        self.results_text.insert(tk.END, f"Nodes expanded: {result['nodes_expanded']}\n")
        self.results_text.insert(tk.END, f"Max frontier size: {result['max_frontier']}\n")
        self.results_text.insert(tk.END, f"Time: {result['time']:.4f} s\n")
        self.results_text.insert(tk.END, f"Moves: {' '.join(result['solution'])}\n\n")

    def run_all_algorithms(self):
        self.results_text.delete("1.0", tk.END)
        for name, algo in self.algo_map.items():
            self.run_algorithm(name, algo)

    def run_selected_algorithm(self):
        if not self.initial_state:
            messagebox.showwarning("No map selected", "Please select a map first.")
            return
        self.results_text.delete("1.0", tk.END)
        name = self.algo_var.get()
        self.run_algorithm(name, self.algo_map[name])
        self.run_algorithm(name, algo_map[name])

if __name__ == "__main__":
    root = tk.Tk()
    app = SokobanGUI(root)
    root.mainloop()