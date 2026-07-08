"""
PyRBD-Suite Unified Mini Demo
====================
This demo shows the usage of the unified library:

1) Load a graph
2) Build a node-probability dict
3) Evaluate availability using SDP, MCS, and Pathset methods
   - single (src, dst)
   - full topology (all pairs)
   - sequential vs parallel
"""

import time
from pyrbd_suite import read_graph, evaluate_availability

def print_section_start(title: str):
    print("\n" + "=" * 70)
    print(title)

def print_section_end():
    print("=" * 70)

def main():
    # Load a sample graph
    print_section_start("Load graph")
    topo = "Germany_17"
    G, _, _ = read_graph(f"topologies/{topo}", topo)
    print(f"Loaded {topo}: |V|={len(G.nodes())}, |E|={len(G.edges())}")

    # Build node probability dict (uniform p=0.9 as example)
    node_prob = {node: 0.9 for node in G.nodes()}
    first_five = list(node_prob.items())[:5]
    print("Sample Node Probabilities (first 5):", {n: p for n, p in first_five})
    print_section_end()

    # Single pair evaluation with several algorithms
    src, dst = 0, 1
    print_section_start(f"Single pair availability: src={src}, dst={dst}")
    
    # MCS
    mcs_res = evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="mcs")
    print("MCS Result:", mcs_res)
    
    # Pathset
    pathset_res = evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="pathset")
    print("Pathset Result:", pathset_res)
    
    # SDP
    sdp_res = evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="sdp")
    print("SDP Result:", sdp_res)
    print_section_end()
    
    # Full topology (all pairs), sequential
    print_section_start("All pairs (SDP, sequential)")
    t0 = time.time()
    res_all = evaluate_availability(G, node_prob, algorithm="sdp")
    print("Sample Results (first 2 pairs):", res_all[:2])
    dt = time.time() - t0
    print(f"Time: {dt:.4f} s")
    print_section_end()

    # Full topology (all pairs), parallel
    print_section_start("All pairs (SDP, parallel)")
    t0 = time.time()
    res_all_p = evaluate_availability(G, node_prob, algorithm="sdp", parallel=True)
    print("Sample Results (first 2 pairs):", res_all_p[:2])
    dt = time.time() - t0
    print(f"Time: {dt:.4f} s")
    print_section_end()
    
    # Link-counted evaluation example
    print_section_start("Link-counted evaluation example")
    edge_prob = {edge: 0.95 for edge in G.edges()}
    t0 = time.time()
    res_link_counted = evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="sdp", count_link=True, edge_prob=edge_prob)
    print("Link-counted Result:", res_link_counted)
    dt = time.time() - t0
    print(f"Time: {dt:.4f} s")
    print_section_end()
    
    # Link-counted full topology, parallel
    print_section_start("All pairs link-counted (SDP, parallel)")
    t0 = time.time()
    res_all_link = evaluate_availability(G, node_prob, algorithm="sdp", parallel=True, count_link=True, edge_prob=edge_prob)
    print("Sample Results (first 2 pairs):", res_all_link[:2])
    dt = time.time() - t0
    print(f"Time: {dt:.4f} s")
    print_section_end()
    
if __name__ == "__main__":
    main()