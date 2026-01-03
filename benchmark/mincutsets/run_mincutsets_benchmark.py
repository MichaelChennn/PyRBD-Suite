import os
import sys
import pandas as pd
from itertools import combinations
from tqdm import tqdm

# Add the package root to sys.path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pyrbd_utils import read_graph
from benchmark.mincutsets.mincutsets_benchmarks import MincutsetsBenchmarks

# Configuration
TOPOLOGIES_DIR = os.path.join(project_root, "topologies")
RESULTS_DIR = os.path.join(current_dir, "results")

# Algorithm mapping: (Short Name, Benchmark Function)
# Order: pyrbd3_cnf, pyrbd3_multiplication, pyrbd3_shannon, pyrbdpp_combination_matrix, pyrbdpp_combination
ALGORITHMS = [
    ("cnf", MincutsetsBenchmarks.pyrbd3_cnf_tree),
    ("multiplication", MincutsetsBenchmarks.pyrbd3_multiplication),
    ("shannon", MincutsetsBenchmarks.pyrbd3_shannon),
    ("combination_matrix", MincutsetsBenchmarks.pyrbdpp_combination_matrix),
    ("combination", MincutsetsBenchmarks.pyrbdpp_combination),
]


def run_benchmarks(topologies=None):
    # Check topologies directory
    if not os.path.exists(TOPOLOGIES_DIR):
        print(f"❌ Topologies directory not found: {TOPOLOGIES_DIR}")
        return

    # Get list of topologies if not provided
    if topologies is None:
        topologies = [
            d
            for d in os.listdir(TOPOLOGIES_DIR)
            if os.path.isdir(os.path.join(TOPOLOGIES_DIR, d))
        ]
        topologies.sort()

        print(f"Found {len(topologies)} topologies: {', '.join(topologies)}")

    # Iterate through algorithms in the specified order
    for algo_name, algo_func in ALGORITHMS:
        print(f"\n🚀 Starting benchmark for algorithm: {algo_name}")

        # Create results directory for this algorithm
        algo_results_dir = os.path.join(RESULTS_DIR, algo_name)
        os.makedirs(algo_results_dir, exist_ok=True)

        # Iterate through all topologies
        for topo_name in topologies:
            print(f"  📂 Processing topology: {topo_name}")

            try:
                topo_path = os.path.join(TOPOLOGIES_DIR, topo_name)
                pickle_path = os.path.join(topo_path, f"Pickle_{topo_name}.pickle")

                # Check if pickle file exists
                if not os.path.exists(pickle_path):
                    print(f"    ⚠️ Skipping {topo_name}: Pickle file not found.")
                    continue

                # Read graph
                G, _, _ = read_graph(topo_path, topo_name)

                # Get all node pairs
                node_pairs = list(combinations(G.nodes(), 2))
                results = []

                # Run benchmark for each pair
                for src, dst in tqdm(
                    node_pairs, desc=f"    Running {algo_name}", leave=False
                ):
                    try:
                        # Execute benchmark function
                        mincutsets, exec_time = algo_func(G, src, dst)

                        results.append(
                            {
                                "source": src,
                                "target": dst,
                                f"{algo_name}_time (second)": f"{exec_time:.10f}",
                                "length": len(mincutsets),
                            }
                        )
                    except Exception as e:
                        # Log error but continue
                        # print(f"    ❌ Error processing pair ({src}, {dst}): {e}")
                        pass

                # Save results to CSV
                if results:
                    df = pd.DataFrame(results)
                    output_filename = f"{topo_name}_MCS_{algo_name}.csv"
                    output_path = os.path.join(algo_results_dir, output_filename)
                    df.to_csv(output_path, index=False)
                    print(f"    ✅ Saved results to {output_path}")
                else:
                    print(f"    ⚠️ No results generated for {topo_name}")

            except Exception as e:
                print(f"  ❌ Failed to process topology {topo_name}: {e}")

        print(f"🏁 Finished benchmark for {algo_name}")


if __name__ == "__main__":
    topos_large_scale = ["india35", "jonas-us-ca", "pioro40","zib54", "Germany_50"]
    topos_small_scale = ["Abilene", "polska", "HiberniaUk", "Germany_17", "Spain", "Austria_24", "Nobel_EU", "Sweden", "USA_26", "Norway"]
    
    run_benchmarks(topos_small_scale)