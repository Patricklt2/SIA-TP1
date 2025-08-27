# Sokoban Solver - Instrucciones de Uso

## Ejecución del Programa

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
push → guarda los resultados en modo push.

player → guarda los resultados en modo player.


## Visualización de Animaciones Simultáneas

**Ver comparación de todos los métodos en un nivel:**
```
python -m src.animation_all_results level_1 [push|player]
```


**Esto ejecutará:**
- BFS, DFS, IDDFS
- A* con 3 heurísticas diferentes
- GGS con 3 heurísticas diferentes
- Guardará los resultados en src/results/level_1_push_results.csv o src/results/level_1_player_results.csv
