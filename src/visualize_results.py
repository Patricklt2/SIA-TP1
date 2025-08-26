import pandas as pd
import matplotlib.pyplot as plt

def load_and_analyze_results():
    try:
        df = pd.read_csv("src/results/consolidated_results_all.csv", encoding='latin1')
        
        # Create algorithm-heuristic combinations for grouping
        df['algo_heur'] = df.apply(lambda row: f"{row['algorithm']}\n({row['heuristic']})", axis=1)
        
        # Calculate means for each algorithm-heuristic combination
        means = df.groupby('algo_heur').agg({
            'time': 'mean',
            'nodes_expanded': 'mean',
            'solution_length': 'mean',
            'max_frontier': 'mean',  # Add max_frontier to metrics
            'success': lambda x: (x == 'Éxito').mean() * 100
        }).round(2)

        # Sort the index to group algorithms together
        def sort_key(x):
            if 'A*' in x: return '1' + x
            if 'GGS' in x: return '2' + x
            return '0' + x
        means = means.reindex(sorted(means.index, key=sort_key))

        # Create all visualizations
        create_time_comparison(means)
        create_nodes_comparison(means)
        create_solution_length_comparison(means)
        create_success_rate_comparison(means)
        create_frontier_comparison(means)  # Add new visualization
        
    except Exception as e:
        print(f"Error analyzing results: {str(e)}")

def create_time_comparison(means):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(means)), means['time'])
    plt.title('Average Execution Time by Algorithm and Heuristic')
    plt.ylabel('Time (seconds)')
    plt.xticks(range(len(means)), means.index, rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}s', ha='center', va='bottom')
    
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    plt.savefig('src/results/time_comparison.png')
    plt.close()

def create_nodes_comparison(means):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(means)), means['nodes_expanded'])
    plt.title('Average Nodes Expanded by Algorithm and Heuristic')
    plt.ylabel('Number of Nodes')
    plt.xticks(range(len(means)), means.index, rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom')
    
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    plt.savefig('src/results/nodes_comparison.png')
    plt.close()

def create_solution_length_comparison(means):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(means)), means['solution_length'])
    plt.title('Average Solution Length by Algorithm and Heuristic')
    plt.ylabel('Steps')
    plt.xticks(range(len(means)), means.index, rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    plt.savefig('src/results/solution_length_comparison.png')
    plt.close()

def create_success_rate_comparison(means):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(means)), means['success'])
    plt.title('Success Rate by Algorithm and Heuristic')
    plt.ylabel('Success Rate (%)')
    plt.xticks(range(len(means)), means.index, rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.ylim(0, 100)  # Set y-axis from 0 to 100%
    plt.tight_layout()
    plt.savefig('src/results/success_rate_comparison.png')
    plt.close()

def create_frontier_comparison(means):
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(means)), means['max_frontier'])
    plt.title('Average Maximum Frontier Size by Algorithm and Heuristic')
    plt.ylabel('Number of Nodes in Frontier')
    plt.xticks(range(len(means)), means.index, rotation=45, ha='right')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom')
    
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    plt.tight_layout()
    plt.savefig('src/results/frontier_comparison.png')
    plt.close()

if __name__ == "__main__":
    load_and_analyze_results()