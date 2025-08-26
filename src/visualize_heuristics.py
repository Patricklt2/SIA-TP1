import pandas as pd
import matplotlib.pyplot as plt

def create_comparison_plot(df, metric, title, ylabel):
    plt.figure(figsize=(12, 6))
    
    # Plot each algorithm-heuristic combination as a separate bar
    x = range(len(df))
    labels = [f"{row['algorithm']}\n({row['heuristic']})" for _, row in df.iterrows()]
    
    plt.bar(x, df[metric])
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(x, labels, rotation=45, ha='right')
    
    # Add value labels on top of bars
    for i, v in enumerate(df[metric]):
        plt.text(i, v, f'{v:.4f}' if metric == 'time' else f'{v}', 
                ha='center', va='bottom')
    
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    plt.savefig(f'src/results/{metric}_l6.png')
    plt.close()

def analyze_results():
    # Read the data
    df = pd.read_csv("src/results/level_6_results.csv", encoding='latin1')
    
    # Create plots for each metric
    create_comparison_plot(df, 'time', 'Execution Time by Algorithm', 'Time (seconds)')
    create_comparison_plot(df, 'nodes_expanded', 'Nodes Expanded by Algorithm', 'Number of Nodes')
    create_comparison_plot(df, 'solution_length', 'Solution Length by Algorithm', 'Steps')
    create_comparison_plot(df, 'max_frontier', 'Maximum Frontier Size by Algorithm', 'Frontier Size')

if __name__ == "__main__":
    analyze_results()