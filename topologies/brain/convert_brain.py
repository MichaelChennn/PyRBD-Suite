import xml.etree.ElementTree as ET
import pickle
import os
import math
import networkx as nx

def main():
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(current_dir, 'brain.xml')
    pickle_path = os.path.join(current_dir, 'Pickle_brain.pickle')

    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} not found.")
        return

    # Parse XML
    print("Parsing XML file...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Sndlib namespaces
    ns = {'ns': 'http://sndlib.zib.de/network'}

    # 1. Parse nodes
    nodes_data = {}
    for node_elem in root.findall('.//ns:node', ns):
        node_id = node_elem.attrib['id']
        x_elem = node_elem.find('.//ns:x', ns)
        y_elem = node_elem.find('.//ns:y', ns)
        if x_elem is not None and y_elem is not None:
            x = float(x_elem.text)
            y = float(y_elem.text)
            nodes_data[node_id] = (x, y)
        else:
            print(f"Warning: Node {node_id} is missing coordinates. Using default (0, 0)")
            nodes_data[node_id] = (0.0, 0.0)

    # Sort nodes alphabetically to ensure deterministic mapping
    sorted_node_ids = sorted(nodes_data.keys())
    node_to_int = {node_id: i for i, node_id in enumerate(sorted_node_ids)}

    # 2. Parse links (edges)
    edges = []
    for link_elem in root.findall('.//ns:link', ns):
        src_elem = link_elem.find('ns:source', ns)
        dst_elem = link_elem.find('ns:target', ns)
        if src_elem is not None and dst_elem is not None:
            src = src_elem.text
            dst = dst_elem.text
            edges.append((src, dst))
        else:
            link_id = link_elem.attrib.get('id', 'unknown')
            print(f"Warning: Link {link_id} is missing source or target element.")

    # Haversine distance formula
    def haversine(lon1, lat1, lon2, lat2):
        R = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    # 3. Create NetworkX graph
    G = nx.Graph()

    # Add nodes with attributes to G
    for node_id in sorted_node_ids:
        int_id = node_to_int[node_id]
        x, y = nodes_data[node_id]
        G.add_node(int_id, label=node_id, pos=(x, y))

    # Add edges with attributes to G
    for src, dst in edges:
        if src not in node_to_int or dst not in node_to_int:
            print(f"Warning: edge {src} -> {dst} refers to undefined node(s)")
            continue
        int_src = node_to_int[src]
        int_dst = node_to_int[dst]
        
        # Calculate weight using Haversine formula
        lon1, lat1 = nodes_data[src]
        lon2, lat2 = nodes_data[dst]
        dist = haversine(lon1, lat1, lon2, lat2)
        
        G.add_edge(int_src, int_dst, weight=dist)

    # 4. Construct pos and label dicts
    pos = {node_to_int[node_id]: nodes_data[node_id] for node_id in sorted_node_ids}
    label = {node_to_int[node_id]: node_id for node_id in sorted_node_ids}

    # Save to pickle
    print(f"Saving pickle file to {pickle_path}...")
    with open(pickle_path, 'wb') as handle:
        pickle.dump((G, pos, label), handle)

    print(f"Successfully converted brain.xml to Pickle_brain.pickle!")
    print(f"Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")

if __name__ == '__main__':
    main()
