# Sokoban Solver - Instrucciones de Uso

## Ejecución del Programa

**Ejecutar la interfaz gráfica principal:**
```
python -m src.runner
```
```
python3 -m src.runner
```

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

## Visualización de Animaciones Simultáneas

**Ver comparación de todos los métodos en un nivel:**
```
python -m src.animation_all_results src/results/level_6_results.csv level_6 src/maps/level_6.txt
```


**Parámetros:**
- src/results/level_6_results.csv → Archivo CSV con los resultados
- level_6 → Nombre del nivel a visualizar
- src/maps/level_6.txt → Archivo del mapa correspondiente

## Generar Resultados para un Nivel

**Guardar soluciones de un nivel específico:**
```
python -m src.level_results level_1 [push|player]
```

push → guarda los resultados en modo push.

player → guarda los resultados en modo player.

**Esto ejecutará:**
- BFS, DFS, IDDFS
- A* con 3 heurísticas diferentes
- GGS con 3 heurísticas diferentes
- Guardará los resultados en src/results/level_1_push_results.csv o src/results/level_1_player_results.csv
