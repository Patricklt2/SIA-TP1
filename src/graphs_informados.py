import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def generar_graficos_player_informados(level):
    results_dir = "src/results"
    graphs_dir = "src/graphs"
    os.makedirs(graphs_dir, exist_ok=True)

    # Leer CSV del modo Player
    player_file = os.path.join(results_dir, f"{level}_player_results.csv")
    df = pd.read_csv(player_file)

    # Filtrar solo BFS, A* y GGS
    df = df[df["algorithm"].isin(["BFS", "A*", "GGS"])]

    # Crear columna 'method' combinando algoritmo y heurística
    def method_label(row):
        if row["algorithm"] in ["A*", "GGS"]:
            return f"{row['algorithm']} ({row['heuristic']})"
        else:
            return row["algorithm"]

    df["method"] = df.apply(method_label, axis=1)

    methods = df["method"].tolist()

    metrics = {
        "nodes_expanded": "Nodos Expandidos",
        "time": "Tiempo (segundos)",
        "cost": "Costo",
        "max_frontier": "Máximo de Frontera"
    }

    fig, axes = plt.subplots(2, 2, figsize=(18,12))
    axes = axes.flatten()

    for i, (key, label) in enumerate(metrics.items()):
        values = df[key].tolist()
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
        axes[i].tick_params(axis='x', labelrotation=45)
        axes[i].tick_params(axis='x', labelrotation=45)
        for tick in axes[i].get_xticklabels():
            tick.set_horizontalalignment('right')


    plt.suptitle(f"Comparación de Métodos Informados - {level} - Modo Player", fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_file = os.path.join(graphs_dir, f"{level}_player_comparison_informados.png")
    plt.savefig(output_file)
    plt.close()

    print(f"✅ Gráfico combinado generado en {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python -m src.graphs_informados <nivel>")
        sys.exit(1)
    nivel = sys.argv[1]
    generar_graficos_player_informados(nivel)
