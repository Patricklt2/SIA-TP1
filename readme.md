# Sokoban Solver - Instrucciones de Uso

## Instalación de Dependencias

**Instalar Tkinter (si falta):**

**En macOS:**
```
brew install python-tk
```

**En Linux (Debian/Ubuntu):**
```
sudo apt update
sudo apt install python3-tk
```

**Instalar pandas y matplotlib para generar los graficos:**
```
pip install pandas matplotlib
```

## Ejecución del Programa

**Ejecutar la interfaz gráfica principal:**
```
python -m src.runner
```
```
python3 -m src.runner
```

## Generar Resultados para un Nivel

**Guardar soluciones de un nivel específico:**
```
python -m src.level_results level_1 [push|player]
```
- push → guarda los resultados en modo push.
- player → guarda los resultados en modo player.

**Esto ejecutará:**
- BFS, DFS, IDDFS
- A* con 3 heurísticas diferentes
- GGS con 3 heurísticas diferentes
- Guardará los resultados en src/results/level_1_push_results.csv o src/results/level_1_player_results.csv


## Visualización de Animaciones Simultáneas

**Ver comparación de todos los métodos en un nivel:**
```
python -m src.animation_all_results level_1 [push|player]
```
- Debe estar en la carpeta src/results el archivo: level_1_push_results.csv o level_1_player_results.csv


## Visualización de Graficos

**Ver comparación de Metodos Informados:**
```
python -m src.graphs_informados level_1
```
- Debe estar en la src/carpeta results el archivo: level_1_player_results.csv


**Ver comparación de Metodos No Informados:**
```
python -m src.graphs_no_informados level_1
```
- Debe estar en la carpeta src/results el archivo: level_1_player_results.csv


**Ver comparación de modo player y modo push**
```
python -m src.graphs_modes level_6
```
- Debe estar en la carpeta src/results el archivo: level_1_player_results.csv y level_1_push_results.csv
