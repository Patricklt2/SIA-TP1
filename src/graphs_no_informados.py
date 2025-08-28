import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import numpy as np

def generar_graficos_player_unido(level: int):
    # Paths
    results_dir = "src/results"
    graphs_dir = "src/graphs"
    os.makedirs(graphs_dir, exist_ok=True)

    # Archivo del modo Player
    player_file = os.path.join(results_dir, f"level_{level}_player_results.csv")
    df = pd.read_csv(player_file)

    # Filtrar solo BFS, DFS e IDDFS
    df = df[df["algorithm"].isin(["BFS", "DFS", "IDDFS"])]

    # Crear columna con etiqueta clara
    df["method"] = df["algorithm"]

    methods = ["BFS", "DFS", "IDDFS"]
    metrics = {
        "nodes_expanded": "Nodos Expandidos",
        "time": "Tiempo (segundos)",
        "cost": "Costo",
        "max_frontier": "Máximo de Frontera"
    }

    fig, axes = plt.subplots(2, 2, figsize=(14,10))
    axes = axes.flatten()

    for i, (key, label) in enumerate(metrics.items()):
        values = [df[df["method"] == m][key].values[0] for m in methods]
        bars = axes[i].bar(methods, values, color='skyblue')

        # Etiquetas encima de las barras
        for bar in bars:
            height = bar.get_height()
            if key == "time":
                axes[i].annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                                 xytext=(0,3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
            else:
                axes[i].annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                                 xytext=(0,3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

        axes[i].set_ylabel(label)
        axes[i].set_title(label)

    plt.suptitle(f"Comparación de Métodos - Nivel {level} - Modo Player", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_file = os.path.join(graphs_dir, f"level_{level}_player_comparison.png")
    plt.savefig(output_file)
    plt.close()

    print(f"✅ Gráfico combinado generado en {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python generar_graficos_player_unido.py <nivel>")
        sys.exit(1)
    nivel = int(sys.argv[1])
    generar_graficos_player_unido(nivel)
