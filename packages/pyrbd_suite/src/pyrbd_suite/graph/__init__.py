"""
pyrbd_suite.graph — NetworkX graph preparation
===============================================

Converts NetworkX graphs to adjacency lists for the C++ core,
and provides link-graph transformation for edge reliability.
"""

import networkx as nx


def graph_to_adjlist(G):
    """Convert a NetworkX graph to an adjacency list (0-indexed).

    The resulting adjacency list is a list of lists where adj[i] contains
    the neighbours of node i. Nodes are assumed to be 0-indexed integers.

    Args:
        G (nx.Graph): The input graph.

    Returns:
        list[list[int]]: Adjacency list.
    """
    num_nodes = max(G.nodes()) + 1
    adj = [[] for _ in range(num_nodes)]
    for u, v in G.edges():
        adj[u].append(v)
        adj[v].append(u)
    return adj


def to_link_graph(G, A_dict, edge_prob):
    """Convert a NetworkX graph to a link counted graph representation.

    For each edge (u, v) in G, a new node is inserted between u and v.
    The new node inherits the edge's availability probability.

    Args:
        G (nx.Graph): The input graph.
        A_dict (dict): Node availability probabilities.
        edge_prob (dict): Edge availability probabilities.

    Returns:
        tuple: (link_G, A_dict_new)
    """
    link_G = G.copy()
    A_dict_new = A_dict.copy()

    for i, (u, v) in enumerate(G.edges()):
        new_node = len(G.nodes()) + i
        link_G.add_node(new_node)
        link_G.add_edge(u, new_node)
        link_G.add_edge(new_node, v)
        link_G.remove_edge(u, v)
        A_dict_new[new_node] = edge_prob.get((u, v), edge_prob.get((v, u), 0.0))

    return link_G, A_dict_new


def relabel_graph_A_dict(G, avail_dict):
    """Relabel graph nodes to 0-based contiguous integers.

    Args:
        G (nx.Graph): The input graph.
        avail_dict (dict): Node availability dictionary.

    Returns:
        tuple: (relabeled_graph, relabeled_avail_dict, mapping)
    """
    nodes = sorted(G.nodes())
    relabel_mapping = {nodes[i]: i for i in range(len(nodes))}
    G_relabel = nx.relabel_nodes(G, relabel_mapping)
    A_dict_relabel = {relabel_mapping[node]: value for node, value in avail_dict.items()}
    return G_relabel, A_dict_relabel, relabel_mapping


__all__ = [
    "graph_to_adjlist",
    "to_link_graph",
    "relabel_graph_A_dict",
]
