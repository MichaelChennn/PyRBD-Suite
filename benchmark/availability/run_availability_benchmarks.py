import os
import sys
import pandas as pd
from itertools import combinations
from tqdm import tqdm
import networkx as nx

# Add the package root to sys.path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pyrbd_utils import read_graph, relabel_graph_A_dict
from benchmark.availability.availability_benchmarks import AvailabilityBenchmarks
from pyrbd3.algorithms.sets import minimalcuts as pyrbd3_minimalcuts
from pyrbd_plusplus.algorithms.sets.pathsets import minimalpaths

# Configuration
TOPOLOGIES_DIR = os.path.join(project_root, "topologies")
RESULTS_DIR = os.path.join(current_dir, "results")

# Algorithm mapping: (Short Name, Benchmark Function, Input Type)
# Input Type: "mcs" or "pathset"
ALGORITHMS_SINGLE = [
    # PyRBD++ MCS based
    ("pyrbdpp_mcs_single_flow", AvailabilityBenchmarks.pyrbdpp_mcs_single_flow, "mcs"),
    
    # PyRBD++ Pathset based
    ("pyrbdpp_pathset_single_flow", AvailabilityBenchmarks.pyrbdpp_pathset_single_flow, "pathset"),
    
    # PyRBD3 SDP based
    ("pyrbd3_sdp_single_flow", AvailabilityBenchmarks.pyrbd3_sdp_single_flow, "pathset"),
    
    # Parallel versions (Single Flow Parallel)
    ("pyrbd3_sdp_single_flow_parallel", AvailabilityBenchmarks.pyrbd3_sdp_single_flow_parallel, "pathset"),
]

ALGORITHMS_WHOLE = [
    # PyRBD++ MCS based
    ("pyrbdpp_mcs_whole_topo", AvailabilityBenchmarks.pyrbdpp_mcs_whole_topo, "mcs"),
    ("pyrbdpp_mcs_whole_topo_parallel", AvailabilityBenchmarks.pyrbdpp_mcs_whole_topo_parallel, "mcs"),
    
    # PyRBD++ Pathset based
    ("pyrbdpp_pathset_whole_topo", AvailabilityBenchmarks.pyrbdpp_pathset_whole_topo, "pathset"),
    ("pyrbdpp_pathset_whole_topo_parallel", AvailabilityBenchmarks.pyrbdpp_pathset_whole_topo_parallel, "pathset"),
    
    # PyRBD3 SDP based
    ("pyrbd3_sdp_whole_topo", AvailabilityBenchmarks.pyrbd3_sdp_whole_topo, "pathset"),
    ("pyrbd3_sdp_whole_topo_parallel", AvailabilityBenchmarks.pyrbd3_sdp_whole_topo_parallel, "pathset"),
]

def get_probabilities(G):
    """
    Generate a probability dictionary for the graph.
    Assigns 0.9 to all nodes.
    """
    probs = {}
    for node in G.nodes():
        probs[node] = 0.9
    return probs

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

    # Iterate through all topologies first to generate sets once per topology
    for topo_name in topologies:
        print(f"\n📂 Processing topology: {topo_name}")

        try:
            topo_path = os.path.join(TOPOLOGIES_DIR, topo_name)
            pickle_path = os.path.join(topo_path, f"Pickle_{topo_name}.pickle")

            # Check if pickle file exists
            if not os.path.exists(pickle_path):
                print(f"  ⚠️ Skipping {topo_name}: Pickle file not found.")
                continue

            # Read graph
            G, _, _ = read_graph(topo_path, topo_name)
            
            # Generate probabilities
            probabilities = get_probabilities(G)

            # Relabel graph and probabilities
            G, probabilities, _ = relabel_graph_A_dict(G, probabilities)

            # Get all node pairs
            node_pairs = list(combinations(G.nodes(), 2))
            
            # Pre-compute sets for all pairs to avoid re-computing for each algo
            # We store them in a dict: (src, dst) -> {'mcs': ..., 'pathset': ...}
            pair_data = {}
            
            print(f"  ⚙️  Generating MCS and Pathsets for {len(node_pairs)} pairs...")
            for src, dst in tqdm(node_pairs, desc="  Pre-computing sets", leave=False):
                try:
                    # Generate MCS (using pyrbd3_cnf_tree as default/fastest)
                    mcs = pyrbd3_minimalcuts(G, src, dst, method="cnf_tree")
                    
                    # Generate Pathsets
                    ps = minimalpaths(G, src, dst)
                    
                    pair_data[(src, dst)] = {
                        "mcs": mcs,
                        "pathset": ps
                    }
                except Exception as e:
                    # print(f"    ⚠️ Error generating sets for ({src}, {dst}): {e}")
                    pass

            if not pair_data:
                print(f"  ⚠️ No sets generated for {topo_name}, skipping algorithms.")
                continue

            # Prepare data for whole topo algorithms
            pairs_list = list(pair_data.keys())
            mcs_list = [pair_data[p]["mcs"] for p in pairs_list]
            pathset_list = [pair_data[p]["pathset"] for p in pairs_list]

            # 1. Run Single Flow Algorithms
            for algo_name, algo_func, input_type in ALGORITHMS_SINGLE:
                print(f"  🚀 Running {algo_name} (Single Flow)...")
                
                # Create results directory for this algorithm
                algo_results_dir = os.path.join(RESULTS_DIR, algo_name)
                os.makedirs(algo_results_dir, exist_ok=True)
                
                results = []
                
                for (src, dst), data in tqdm(pair_data.items(), desc=f"    Running {algo_name}", leave=False):
                    try:
                        sets = data.get(input_type)
                        if sets is None:
                            continue
                            
                        # Prepare arguments based on function signature
                        if "single_flow" in algo_name or "eval_avail" in algo_name:
                            res, exec_time = algo_func(src, dst, probabilities, sets)
                        else:
                            res, exec_time = algo_func(src, dst, sets)

                        results.append(
                            {
                                "source": src,
                                "target": dst,
                                f"{algo_name}_time (second)": f"{exec_time:.10f}",
                            }
                        )
                    except Exception as e:
                        pass

                # Save results to CSV
                if results:
                    df = pd.DataFrame(results)
                    output_filename = f"{topo_name}_Availability_{algo_name}.csv"
                    output_path = os.path.join(algo_results_dir, output_filename)
                    df.to_csv(output_path, index=False)
                    print(f"    ✅ Saved results to {output_path}")
                else:
                    print(f"    ⚠️ No results generated for {topo_name} - {algo_name}")

            # 2. Run Whole Topo Algorithms
            for algo_name, algo_func, input_type in ALGORITHMS_WHOLE:
                print(f"  🚀 Running {algo_name} (Whole Topo)...")
                algo_results_dir = os.path.join(RESULTS_DIR, algo_name)
                os.makedirs(algo_results_dir, exist_ok=True)
                
                sets_list = mcs_list if input_type == "mcs" else pathset_list
                
                try:
                    # Whole topo functions return (result, time)
                    # Signature: (node_pairs, probabilities, sets_list)
                    res, exec_time = algo_func(pairs_list, probabilities, sets_list)
                    
                    results = [{
                        "topology": topo_name,
                        "num_pairs": len(pairs_list),
                        f"{algo_name}_time (second)": f"{exec_time:.10f}"
                    }]
                    
                    df = pd.DataFrame(results)
                    output_filename = f"{topo_name}_Availability_{algo_name}.csv"
                    output_path = os.path.join(algo_results_dir, output_filename)
                    df.to_csv(output_path, index=False)
                    print(f"    ✅ Saved results to {output_path}")

                except Exception as e:
                    print(f"    ❌ Error running {algo_name}: {e}")
                else:
                    print(f"    ⚠️ No results generated for {topo_name} - {algo_name}")

        except Exception as e:
            print(f"  ❌ Failed to process topology {topo_name}: {e}")

    print(f"🏁 Finished all benchmarks")


if __name__ == "__main__":
    topos_large_scale = ["india35", "jonas-us-ca", "pioro40","zib54", "Germany_50"]
    topos_small_scale = ["Abilene", "polska", "HiberniaUk", "Germany_17", "Spain", "Austria_24", "Sweden", "USA_26", "Norway","Nobel_EU"]
    
    # Default to small scale for testing
    run_benchmarks(topos_small_scale)
