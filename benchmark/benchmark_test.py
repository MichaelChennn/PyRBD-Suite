from pyrbd_plusplus import evaluate_availability, read_graph
import time
topo = "Germany_17"
G, _, _ = read_graph(f"topologies/{topo}", topo)
node_probs = {node: 0.99 for node in G.nodes()}
src = 1
dst = 10
time_start = time.perf_counter()
result = evaluate_availability(G, node_probs, "pathset", src, dst)
time_end = time.perf_counter()
print(f"Computation Time: {time_end - time_start} seconds")
print(f"Availability from node {src} to node {dst}: {result}")

from pyrbd3 import evaluate_availability

time_start = time.perf_counter()
result = evaluate_availability(G, node_probs, "sdp", src, dst)
time_end = time.perf_counter()
print(f"Computation Time: {time_end - time_start} seconds")
print(f"Availability from node {src} to node {dst} using SDP: {result}")

