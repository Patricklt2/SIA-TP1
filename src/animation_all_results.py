import os
import tkinter as tk
from tkinter import ttk
import argparse
import csv
from pathlib import Path
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares, Box

class MultiAnimationWindow:
    def __init__(self, master, sokoban_map, algorithm_results):
        self.master = master
        master.title("Comparación Simultánea de Algoritmos - Sokoban")
        
        self.sokoban_map = sokoban_map
        self.algorithm_results = algorithm_results
        self.current_step = 0
        self.animation_speed = tk.IntVar(value=500)
        self.is_playing = False
        self.animation_id = None
        
        # Configurar la ventana principal
        self.setup_ui()
        
        # Inicializar estados de animación
        self.animation_states = {}
        for algo_name, result in algorithm_results.items():
            if result.get('solution'):
                boxes_set = set(self.sokoban_map.boxes)
                self.animation_states[algo_name] = {
                    'state': SokobanState(self.sokoban_map.player, boxes_set),
                    'solution': result['solution'],
                    'current_step': 0,
                    'info': result
                }
        
        self.draw_all_maps()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario con todas las animaciones visibles"""
        # Frame principal
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de controles en la parte superior
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10, fill=tk.X)
        
        # Botones de control
        self.play_button = tk.Button(control_frame, text="▶ Play All", command=self.play_all_animations, font=("Arial", 12))
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(control_frame, text="⏸ Pause All", command=self.pause_all_animations, font=("Arial", 12))
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(control_frame, text="⏮ Reset All", command=self.reset_all_animations, font=("Arial", 12))
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.step_button = tk.Button(control_frame, text="⏭ Step All", command=self.step_all_animations, font=("Arial", 12))
        self.step_button.pack(side=tk.LEFT, padx=5)
        
        # Control de velocidad
        speed_frame = tk.Frame(control_frame)
        speed_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(speed_frame, text="Speed:", font=("Arial", 10)).pack()
        tk.Scale(speed_frame, from_=50, to=2000, orient=tk.HORIZONTAL, 
                variable=self.animation_speed, showvalue=True, length=150).pack()
        
        # Contador de pasos
        self.step_label = tk.Label(control_frame, text="Step: 0", font=("Arial", 12, "bold"))
        self.step_label.pack(side=tk.LEFT, padx=20)
        
        # Frame para el canvas con scroll
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        # Frame scrollable dentro del canvas
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empacar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar el mouse wheel para scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Configurar grid para las animaciones
        self.canvas_frames = {}
        
        # Determinar layout del grid (3 columnas)
        algorithms = [a for a in self.algorithm_results.keys() if self.algorithm_results[a].get('solution')]
        num_algorithms = len(algorithms)
        num_columns = min(3, num_algorithms) or 1
        
        # Crear frames para cada algoritmo
        for i, algo_name in enumerate(algorithms):
            result = self.algorithm_results[algo_name]
            
            # Frame para este algoritmo
            algo_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, borderwidth=2, bg='lightgray')
            row = i // num_columns
            col = i % num_columns
            algo_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Configurar peso del grid para expansión
            self.scrollable_frame.rowconfigure(row, weight=1)
            self.scrollable_frame.columnconfigure(col, weight=1)
            
            # Título del algoritmo
            title_text = f"{algo_name}"
            if result.get('heuristic') and result['heuristic'] != 'N/A':
                title_text += f" ({result['heuristic']})"
            title_text += f" - {len(result['solution'])} moves"
            
            title_label = tk.Label(algo_frame, text=title_text, font=("Arial", 10, "bold"), bg='lightblue')
            title_label.pack(pady=5, fill=tk.X)
            
            # Canvas para la animación (con fondo visible)
            canvas = tk.Canvas(algo_frame, width=280, height=220, bg='lightyellow', highlightthickness=1, highlightbackground="black")
            canvas.pack(pady=5)
            
            # Información del algoritmo
            info_text = f"Cost: {result.get('cost', 'N/A')} | "
            info_text += f"Nodes: {result.get('nodes_expanded', 'N/A'):,}\n"
            info_text += f"Time: {result.get('time', 'N/A'):.3f}s | "
            info_text += f"Frontier: {result.get('max_frontier', 'N/A')}"
            
            info_label = tk.Label(algo_frame, text=info_text, font=("Arial", 8), bg='lightgray')
            info_label.pack()
            
            # Estado de la animación
            status_label = tk.Label(algo_frame, text="Ready", font=("Arial", 8), bg='lightgray')
            status_label.pack()
            
            self.canvas_frames[algo_name] = {
                'canvas': canvas,
                'info_label': info_label,
                'status_label': status_label,
                'frame': algo_frame
            }
    
    def draw_map(self, canvas, state):
        """Dibujar un mapa en el canvas especificado"""
        canvas.delete("all")
        
        walls, floors, goals = self.sokoban_map.walls, self.sokoban_map.floors, self.sokoban_map.goals
        box_positions = {box.pos for box in state.boxes}
        player = state.player
        
        # Calcular dimensiones
        min_r = min(r for r, c in floors | walls)
        max_r = max(r for r, c in floors | walls)
        min_c = min(c for r, c in floors | walls)
        max_c = max(c for r, c in floors | walls)
        
        rows = max_r - min_r + 1
        cols = max_c - min_c + 1
        
        if rows == 0 or cols == 0:
            return
            
        cell_size = min(220 // rows, 280 // cols, 20)
        
        # Calcular offset para centrar
        offset_x = (280 - cols * cell_size) // 2
        offset_y = (220 - rows * cell_size) // 2
        
        # Dibujar el mapa
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                pos = (r, c)
                x1 = offset_x + (c - min_c) * cell_size
                y1 = offset_y + (r - min_r) * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Dibujar piso
                if pos in floors:
                    canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='lightgray')
                
                # Dibujar paredes
                if pos in walls:
                    canvas.create_rectangle(x1, y1, x2, y2, fill='gray', outline='black')
                
                # Dibujar metas
                if pos in goals:
                    canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill='lightgreen', outline='green')
                
                # Dibujar cajas
                if pos in box_positions:
                    color = 'red' if pos in goals else 'orange'
                    canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline='brown')
                
                # Dibujar jugador
                if pos == player:
                    canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill='blue', outline='darkblue')
    
    def draw_all_maps(self):
        """Dibujar todos los mapas"""
        for algo_name, anim_data in self.animation_states.items():
            if algo_name in self.canvas_frames:
                self.draw_map(self.canvas_frames[algo_name]['canvas'], anim_data['state'])
                # Actualizar estado
                progress = f"{anim_data['current_step']}/{len(anim_data['solution'])}"
                self.canvas_frames[algo_name]['status_label'].config(text=f"Step: {progress}")
    
    def play_all_animations(self):
        """Reproducir todas las animaciones"""
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
        
        self.is_playing = True
        self.play_button.config(text="▶ Playing...", state=tk.DISABLED)
        self.animate_step()
    
    def pause_all_animations(self):
        """Pausar todas las animaciones"""
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None
        self.is_playing = False
        self.play_button.config(text="▶ Play All", state=tk.NORMAL)
    
    def reset_all_animations(self):
        """Reiniciar todas las animaciones"""
        self.pause_all_animations()
        self.current_step = 0
        
        for algo_name, anim_data in self.animation_states.items():
            boxes_set = set(self.sokoban_map.boxes)
            anim_data['state'] = SokobanState(self.sokoban_map.player, boxes_set)
            anim_data['current_step'] = 0
        
        self.draw_all_maps()
        self.step_label.config(text="Step: 0")
    
    def step_all_animations(self):
        """Avanzar un paso en todas las animaciones"""
        self.pause_all_animations()
        self.apply_step_to_all()
        self.draw_all_maps()
    
    def animate_step(self):
        """Animación paso a paso"""
        if self.is_playing:
            self.apply_step_to_all()
            self.draw_all_maps()
            
            # Verificar si todas las animaciones terminaron
            all_finished = all(
                anim_data['current_step'] >= len(anim_data['solution']) 
                for anim_data in self.animation_states.values()
            )
            
            if not all_finished:
                self.animation_id = self.master.after(self.animation_speed.get(), self.animate_step)
            else:
                self.is_playing = False
                self.play_button.config(text="▶ Play All", state=tk.NORMAL)
    
    def apply_step_to_all(self):
        """Aplicar un paso a todas las animaciones"""
        self.current_step += 1
        
        for algo_name, anim_data in self.animation_states.items():
            if anim_data['current_step'] < len(anim_data['solution']):
                move = anim_data['solution'][anim_data['current_step']]
                self.apply_move(anim_data['state'], move)
                anim_data['current_step'] += 1
        
        self.step_label.config(text=f"Step: {self.current_step}")
    
    def apply_move(self, state, move):
        """Aplicar movimiento a un estado"""
        direction_map = {
            'Up': (-1, 0),
            'Down': (1, 0),
            'Left': (0, -1),
            'Right': (0, 1)
        }
    
        if move in direction_map:
            dr, dc = direction_map[move]
            new_player_pos = (state.player[0] + dr, state.player[1] + dc)
            
            # Verificar si empuja una caja
            box_to_move = None
            for box in state.boxes:
                if box.pos == new_player_pos:
                    box_to_move = box
                    break
            
            if box_to_move:
                new_box_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
                boxes_set = set(state.boxes)
                boxes_set.remove(box_to_move)
                # Create a new Box object with the same ID but new position
                boxes_set.add(Box(box_to_move.id, new_box_pos))
                state.boxes = boxes_set
            
            # Actualizar posición del jugador
            state.player = new_player_pos

def parse_solution_string(solution_str):
    """Parsear la cadena de solución en una lista de movimientos"""
    if not solution_str:
        return []
    return solution_str.split()

def load_results_from_csv(csv_file, level_name):
    """Cargar resultados desde un archivo CSV"""
    results = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] == level_name and row['success'] == 'Éxito':
                    # Crear nombre único para el algoritmo
                    algo_name = row['algorithm']
                    if row['heuristic'] != 'N/A':
                        algo_name += f"_{row['heuristic']}"
                    
                    results[algo_name] = {
                        'algorithm': row['algorithm'],
                        'heuristic': row['heuristic'],
                        'cost': int(row['cost']) if row['cost'] else None,
                        'nodes_expanded': int(row['nodes_expanded']) if row['nodes_expanded'] else None,
                        'max_frontier': int(row['max_frontier']) if row['max_frontier'] else None,
                        'time': float(row['time']) if row['time'] else None,
                        'solution_length': int(row['solution_length']) if row['solution_length'] else None,
                        'solution': parse_solution_string(row['solution'])
                    }
        
        return results
        
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return {}

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Visualización simultánea de algoritmos desde CSV")
    parser.add_argument("csv_file", help="Ruta del archivo CSV con resultados")
    parser.add_argument("level_name", help="Nombre del nivel a visualizar (ej: level_1)")
    parser.add_argument("map_file", help="Ruta del archivo de mapa correspondiente")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: El archivo CSV {args.csv_file} no existe")
        return
    
    if not os.path.exists(args.map_file):
        print(f"Error: El archivo de mapa {args.map_file} no existe")
        return
    
    print(f"Cargando resultados para {args.level_name}...")
    results = load_results_from_csv(args.csv_file, args.level_name)
    
    if not results:
        print(f"No se encontraron resultados exitosos para {args.level_name}")
        return
    
    print(f"Encontrados {len(results)} algoritmos con solución:")
    for algo_name in results.keys():
        print(f"  - {algo_name}")
    
    print("Cargando mapa...")
    try:
        sokoban_map = parse_map(args.map_file)
    except Exception as e:
        print(f"Error al cargar el mapa: {e}")
        return
    
    # Crear ventana principal
    root = tk.Tk()
    root.title(f"Comparación de Algoritmos - {args.level_name}")
    root.geometry("1400x900")
    
    # Crear ventana de animación múltiple
    app = MultiAnimationWindow(root, sokoban_map, results)
    
    root.mainloop()

if __name__ == "__main__":
    main()