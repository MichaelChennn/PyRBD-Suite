import os
import json
import pickle
import networkx as nx
from backend.models.topology import TopologyModel, NodeModel, EdgeModel

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "topologies")
os.makedirs(DATA_DIR, exist_ok=True)

def get_topology_path(name: str) -> str:
    return os.path.join(DATA_DIR, f"{name}.json")

def list_topologies():
    topologies = []
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".json"):
                topologies.append(f[:-5])
    return topologies

def load_topology(name: str) -> TopologyModel:
    path = get_topology_path(name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return TopologyModel(**data)

def save_topology(topology: TopologyModel):
    path = get_topology_path(topology.name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topology.model_dump(), f, indent=2)

def import_pickle_topologies(pickle_dir: str):
    """Scan pickle_dir and import all topologies into JSON format."""
    imported = []
    if not os.path.exists(pickle_dir):
        return imported
        
    for item in os.listdir(pickle_dir):
        item_path = os.path.join(pickle_dir, item)
        if os.path.isdir(item_path):
            # Look for pickle files inside
            for f in os.listdir(item_path):
                if f.endswith(".pickle"):
                    p_path = os.path.join(item_path, f)
                    try:
                        with open(p_path, "rb") as pf:
                            G = pickle.load(pf)
                            if isinstance(G, (tuple, list)):
                                G = G[0]  # Some files save (Graph, pos) or similar
                        
                        topo = networkx_to_topology(G, name=item)
                        save_topology(topo)
                        imported.append(item)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"Failed to import {p_path}: {e}")
    return imported

def networkx_to_topology(G: nx.Graph, name: str) -> TopologyModel:
    nodes = []
    pos = nx.spring_layout(G) # Generate default layout if none exists
    
    for n, data in G.nodes(data=True):
        # Handle nodes that might just be integers without data
        prob = data.get("prob", 1.0)
        p = pos.get(n, [0.0, 0.0])
        nodes.append(NodeModel(
            id=str(n),
            label=str(n),
            prob=prob,
            x=float(p[0] * 500), # Scale to a reasonable canvas size
            y=float(p[1] * 500)
        ))
        
    edges = []
    for u, v, data in G.edges(data=True):
        prob = data.get("prob", 1.0)
        edges.append(EdgeModel(
            source=str(u),
            target=str(v),
            prob=prob
        ))
        
    return TopologyModel(name=name, nodes=nodes, edges=edges)

def topology_to_networkx(topo: TopologyModel) -> nx.Graph:
    G = nx.Graph()
    for n in topo.nodes:
        # Use integer IDs if possible, else string
        node_id = int(n.id) if n.id.isdigit() else n.id
        G.add_node(node_id, prob=n.prob, pos=(n.x, n.y))
        
    for e in topo.edges:
        u = int(e.source) if e.source.isdigit() else e.source
        v = int(e.target) if e.target.isdigit() else e.target
        G.add_edge(u, v, prob=e.prob)
    return G
