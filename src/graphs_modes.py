import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import numpy as np

def generar_graficos(level: int):
    # Paths
    results_dir = "src/results"
    graphs_dir = "src/graphs"
    os.makedirs(graphs_dir, exist_ok=True)

    # Archivos
    push_file = os.path.join(results_dir, f"{level}_push_results.csv")
    player_file = os.path.join(results_dir, f"{level}_player_results.csv")

    # Leer CSV
    push_df = pd.read_csv(push_file)
    player_df = pd.read_csv(player_file)

    # Agregar columna para identificar modo
    push_df["mode"] = "Push"
    player_df["mode"] = "Player"

    # Combinar
    df = pd.concat([push_df, player_df], ignore_index=True)

    # Filtrar solo BFS, DFS, IDDFS y A* con manhattan
    df = df[
        (df["algorithm"].isin(["BFS", "DFS", "IDDFS"])) |
        ((df["algorithm"] == "A*") & (df["heuristic"] == "manhattan"))
    ]

    # Crear columna con etiqueta clara
    df["method"] = df.apply(
        lambda row: f"{row['algorithm']} (manhattan)" 
        if row["algorithm"] == "A*" and row["heuristic"] == "manhattan"
        else row["algorithm"], axis=1
    )

    methods = ["BFS", "DFS", "IDDFS", "A* (manhattan)"]
    modes = ["Push", "Player"]

    # =========================
    # Comparar Tiempo
    # =========================
    x = np.arange(len(methods))  # posiciones para los métodos
    width = 0.35  # ancho de cada barra

    fig, ax = plt.subplots(figsize=(10,6))
    for i, mode in enumerate(modes):
        sub_df = df[df["mode"] == mode]
        times = [sub_df[sub_df["method"] == m]["time"].values[0] for m in methods]
        bars = ax.bar(x + i*width, times, width, label=mode)
        # valores encima de cada barra
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0,3),  # desplazamiento
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x + width/2)
    ax.set_xticklabels(methods)
    ax.set_ylabel("Tiempo (segundos)")
    ax.set_title(f"Comparación Tiempo - {level}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(graphs_dir, f"{level}_time_comparison.png"))
    plt.close()

    # =========================
    # Comparar Nodos Expandidos
    # =========================
    fig, ax = plt.subplots(figsize=(10,6))
    for i, mode in enumerate(modes):
        sub_df = df[df["mode"] == mode]
        nodes = [sub_df[sub_df["method"] == m]["nodes_expanded"].values[0] for m in methods]
        bars = ax.bar(x + i*width, nodes, width, label=mode)
        # valores encima de cada barra
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0,3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x + width/2)
    ax.set_xticklabels(methods)
    ax.set_ylabel("Nodos expandidos")
    ax.set_title(f"Comparación Nodos Expandidos - {level}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(graphs_dir, f"{level}_nodes_comparison.png"))
    plt.close()

    print(f"✅ Gráficos comparativos (BFS, DFS, IDDFS, A* manhattan) generados en {graphs_dir}/")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python generar_graficos.py <nivel>")
        sys.exit(1)
    generar_graficos(sys.argv[1])
