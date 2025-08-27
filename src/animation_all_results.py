import os
import tkinter as tk
from tkinter import ttk
import argparse
import csv
import ast
from pathlib import Path
from src.run_sokoban.sokoban import parse_map, SokobanState, precompute_dead_squares, Box

class MultiAlgorithmAnimation:
    def __init__(self, master, sokoban_map, algorithm_results, mode):
        self.master = master
        master.title(f"Comparación Simultánea de Algoritmos - Sokoban ({mode})")
        
        self.sokoban_map = sokoban_map
        self.algorithm_results = algorithm_results
        self.mode = mode
        self.current_step = 0
        self.animation_speed = tk.IntVar(value=300)
        self.is_playing = False
        self.animation_id = None
        
        # Configurar la interfaz
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
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de control
        btn_style = {"font": ("Arial", 10), "width": 10}
        
        self.play_btn = tk.Button(control_frame, text="▶ Play", command=self.play_animation, **btn_style)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(control_frame, text="⏸ Pause", command=self.pause_animation, **btn_style)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(control_frame, text="⏮ Reset", command=self.reset_animation, **btn_style)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_btn = tk.Button(control_frame, text="⏭ Step", command=self.step_animation, **btn_style)
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        # Control de velocidad
        speed_frame = tk.Frame(control_frame)
        speed_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(speed_frame, text="Velocidad:", font=("Arial", 9)).pack()
        tk.Scale(speed_frame, from_=100, to=1000, orient=tk.HORIZONTAL, 
                variable=self.animation_speed, showvalue=True, length=150).pack()
        
        # Contador de pasos
        self.step_label = tk.Label(control_frame, text="Paso: 0", font=("Arial", 10, "bold"))
        self.step_label.pack(side=tk.LEFT, padx=20)
        
        # Frame para canvas con scroll
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        # Frame scrollable
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del mouse
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Configurar grid para las animaciones
        self.canvas_frames = {}
        
        # Crear frames para cada algoritmo
        algorithms = [a for a in self.algorithm_results.keys() if self.algorithm_results[a].get('solution')]
        num_algorithms = len(algorithms)
        num_columns = min(3, num_algorithms)
        
        for i, algo_name in enumerate(algorithms):
            result = self.algorithm_results[algo_name]
            
            # Frame para este algoritmo
            algo_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, borderwidth=1)
            row = i // num_columns
            col = i % num_columns
            algo_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Título del algoritmo
            title_text = f"{algo_name}"
            if result.get('heuristic') and result['heuristic'] != 'N/A':
                title_text += f" ({result['heuristic']})"
            title_text += f" - {len(result['solution'])} movimientos"
            
            title_label = tk.Label(algo_frame, text=title_text, font=("Arial", 10, "bold"), bg='#e0e0ff')
            title_label.pack(pady=5, fill=tk.X)
            
            # Canvas para la animación
            canvas = tk.Canvas(algo_frame, width=300, height=250, bg='white', highlightthickness=1)
            canvas.pack(pady=5)
            
            # Información del algoritmo
            info_text = f"Costo: {result.get('cost', 'N/A')} | "
            info_text += f"Nodos: {result.get('nodes_expanded', 'N/A'):,}\n"
            info_text += f"Tiempo: {result.get('time', 'N/A'):.3f}s | "
            info_text += f"Frontera: {result.get('max_frontier', 'N/A')}"
            
            info_label = tk.Label(algo_frame, text=info_text, font=("Arial", 8), justify=tk.LEFT)
            info_label.pack()
            
            # Estado de la animación
            status_label = tk.Label(algo_frame, text="Listo", font=("Arial", 8))
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
        player = state.player
        boxes = {box.pos for box in state.boxes}
        
        # Calcular dimensiones
        min_r = min(r for r, c in floors | walls)
        max_r = max(r for r, c in floors | walls)
        min_c = min(c for r, c in floors | walls)
        max_c = max(c for r, c in floors | walls)
        
        rows = max_r - min_r + 1
        cols = max_c - min_c + 1
        
        cell_size = min(250 // rows, 300 // cols, 25)
        
        # Calcular offset para centrar
        offset_x = (300 - cols * cell_size) // 2
        offset_y = (250 - rows * cell_size) // 2
        
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
                    canvas.create_rectangle(x1, y1, x2, y2, fill='#404040', outline='black')
                
                # Dibujar metas
                if pos in goals:
                    canvas.create_oval(x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill='#90ee90', outline='green')
                
                # Dibujar cajas
                if pos in boxes:
                    color = '#ff6b6b' if pos in goals else '#ffa500'
                    canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill=color, outline='#8b4513')
                
                # Dibujar jugador (solo si no está en push_mode)
                if pos == player and self.mode != "push_mode":
                    canvas.create_oval(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill='#4169e1', outline='#00008b')
    
    def draw_all_maps(self):
        """Dibujar todos los mapas"""
        for algo_name, anim_data in self.animation_states.items():
            if algo_name in self.canvas_frames:
                self.draw_map(self.canvas_frames[algo_name]['canvas'], anim_data['state'])
                progress = f"{anim_data['current_step']}/{len(anim_data['solution'])}"
                self.canvas_frames[algo_name]['status_label'].config(text=f"Paso: {progress}")
    
    def play_animation(self):
        """Reproducir todas las animaciones"""
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
        
        self.is_playing = True
        self.play_btn.config(text="▶ Reproduciendo...", state=tk.DISABLED)
        self.animate_step()
    
    def pause_animation(self):
        """Pausar todas las animaciones"""
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None
        self.is_playing = False
        self.play_btn.config(text="▶ Play", state=tk.NORMAL)
    
    def reset_animation(self):
        """Reiniciar todas las animaciones"""
        self.pause_animation()
        self.current_step = 0
        
        for algo_name, anim_data in self.animation_states.items():
            boxes_set = set(self.sokoban_map.boxes)
            anim_data['state'] = SokobanState(self.sokoban_map.player, boxes_set)
            anim_data['current_step'] = 0
        
        self.draw_all_maps()
        self.step_label.config(text="Paso: 0")
    
    def step_animation(self):
        """Avanzar un paso en todas las animaciones"""
        self.pause_animation()
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
                self.play_btn.config(text="▶ Play", state=tk.NORMAL)
    
    def apply_step_to_all(self):
        """Aplicar un paso a todas las animaciones"""
        self.current_step += 1
        
        for algo_name, anim_data in self.animation_states.items():
            if anim_data['current_step'] < len(anim_data['solution']):
                move = anim_data['solution'][anim_data['current_step']]
                self.apply_move(anim_data['state'], move)
                anim_data['current_step'] += 1
        
        self.step_label.config(text=f"Paso: {self.current_step}")
    
    def apply_move(self, state, move):
        """Aplicar movimiento a un estado"""
        action, box_id = move
        direction_map = {
            'Up': (-1, 0),
            'Down': (1, 0),
            'Left': (0, -1),
            'Right': (0, 1)
        }

        if action not in direction_map:
            return

        dr, dc = direction_map[action]
        new_player_pos = (state.player[0] + dr, state.player[1] + dc)

        boxes_set = set(state.boxes)

        if box_id is not None:
            box_to_move = next(b for b in boxes_set if b.id == box_id)
            new_box_pos = (box_to_move.pos[0] + dr, box_to_move.pos[1] + dc)
            boxes_set.remove(box_to_move)
            boxes_set.add(Box(box_to_move.id, new_box_pos))
            
        state.boxes = boxes_set
        state.player = new_player_pos

def parse_solution_string(solution_str):
    """Parsear la cadena de solución en una lista de movimientos"""
    try:
        # Intentar evaluar como lista de Python
        return ast.literal_eval(solution_str)
    except:
        # Si falla, intentar otros formatos
        if not solution_str or solution_str == '[]':
            return []
        
        # Formato con paréntesis: "(Up, 1)" o "Up(1)"
        moves = []
        cleaned_str = solution_str.strip('[]').replace('"', '').replace("'", "")
        
        for item in cleaned_str.split('),'):
            item = item.strip().strip('()')
            if '(' in item and ')' in item:
                # Formato: "Up(1)"
                action = item.split('(')[0].strip()
                box_id = int(item.split('(')[1].split(')')[0].strip())
                moves.append((action, box_id))
            elif ',' in item:
                # Formato: "Up, 1"
                parts = item.split(',')
                action = parts[0].strip()
                box_id = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() != 'None' else None
                moves.append((action, box_id))
            else:
                # Formato simple: "Up"
                moves.append((item.strip(), None))
        
        return moves

def load_results_from_csv(csv_file, level_name):
    """Cargar resultados desde un archivo CSV"""
    results = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['level'] == level_name and row['success'] in ['Éxito', 'True', 'Success']:
                    # Crear nombre único para el algoritmo
                    algo_name = row['algorithm']
                    if row['heuristic'] != 'N/A':
                        algo_name += f"_{row['heuristic']}"
                    
                    results[algo_name] = {
                        'algorithm': row['algorithm'],
                        'heuristic': row['heuristic'],
                        'cost': int(row['cost']) if row['cost'] and row['cost'] != 'None' else None,
                        'nodes_expanded': int(row['nodes_expanded']) if row['nodes_expanded'] and row['nodes_expanded'] != 'None' else None,
                        'max_frontier': int(row['max_frontier']) if row['max_frontier'] and row['max_frontier'] != 'None' else None,
                        'time': float(row['time']) if row['time'] and row['time'] != 'None' else None,
                        'solution_length': int(row['solution_length']) if row['solution_length'] and row['solution_length'] != 'None' else None,
                        'solution': parse_solution_string(row['solution'])
                    }
        
        return results
        
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        return {}

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Visualización simultánea de algoritmos de Sokoban")
    parser.add_argument("level_name", help="Nombre del nivel (ej: level_1)")
    parser.add_argument("mode", choices=["player", "push"], help="Modo de visualización (player o push)")
    
    args = parser.parse_args()
    
    # Construir rutas de archivos
    mode_str = "player_mode" if args.mode == "player" else "push_mode"
    csv_file = f"src/results/{args.level_name}_{args.mode}_results.csv"
    map_file = f"src/maps/{args.level_name}.txt"
    
    # Verificar que los archivos existan
    if not os.path.exists(csv_file):
        print(f"Error: No se encontró el archivo CSV {csv_file}")
        return
    
    if not os.path.exists(map_file):
        print(f"Error: No se encontró el archivo de mapa {map_file}")
        return
    
    print(f"Cargando resultados para {args.level_name}...")
    results = load_results_from_csv(csv_file, args.level_name)
    
    if not results:
        print(f"No se encontraron resultados exitosos para {args.level_name}")
        return
    
    print(f"Encontrados {len(results)} algoritmos con solución:")
    for algo_name in results.keys():
        print(f"  - {algo_name}")
    
    print("Cargando mapa...")
    try:
        sokoban_map = parse_map(map_file)
    except Exception as e:
        print(f"Error al cargar el mapa: {e}")
        return
    
    # Crear ventana principal
    root = tk.Tk()
    root.title(f"Comparación de Algoritmos - {args.level_name} ({mode_str})")
    root.geometry("1200x800")
    
    # Crear ventana de animación múltiple
    app = MultiAlgorithmAnimation(root, sokoban_map, results, mode_str)
    
    root.mainloop()

if __name__ == "__main__":
    main()