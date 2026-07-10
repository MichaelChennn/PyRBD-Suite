"""
pyrbd_suite.analysis — Availability evaluation
===============================================

Provides a unified evaluate_availability() entry point that dispatches
to the appropriate C++ algorithm (MCS, Pathset, SDP) via pyrbd_core.
"""

from itertools import combinations
from pyrbd_suite.io import read_graph
from pyrbd_suite.graph import graph_to_adjlist, to_link_graph, relabel_graph_A_dict

# Import the unified C++ core
try:
    import pyrbd_core_cpp as cpp
except ImportError:
    # Try relative import from the build location
    import sys
    import os
    # Add the pyrbd_core src directory to path for development
    _core_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                              "pyrbd_core", "src")
    if os.path.exists(_core_path):
        sys.path.insert(0, os.path.abspath(_core_path))
    import pyrbd_core_cpp as cpp


# ================================================================
# Algorithm configuration
# ================================================================
ALGORITHM_CONFIG = {
    "mcs": {
        "cpp_module": "mcs",
        "problem_set_func": "minimalcuts",
        "needs_cuts": True,
    },
    "pathset": {
        "cpp_module": "pathset",
        "problem_set_func": "minimalpaths",
        "needs_cuts": False,
    },
    "sdp": {
        "cpp_module": "sdp",
        "problem_set_func": "minimalpaths",
        "needs_cuts": False,
    },
}


def minimalpaths(G, src, dst):
    # Relabel graph to 0..N-1 to avoid phantom node bugs in C++
    G_r, _, mapping = relabel_graph_A_dict(G, {})
    reverse_mapping = {v: k for k, v in mapping.items()}
    src_r, dst_r = mapping[src], mapping[dst]
    
    adj = graph_to_adjlist(G_r)
    paths_r = cpp.sets.minimalpaths(adj, src_r, dst_r)
    
    # Map back
    return [[reverse_mapping[n] for n in p] for p in paths_r]


def minimalcuts(G, src, dst, method="cnf_tree"):
    # Relabel graph to 0..N-1 to avoid phantom node bugs in C++
    G_r, _, mapping = relabel_graph_A_dict(G, {})
    reverse_mapping = {v: k for k, v in mapping.items()}
    src_r, dst_r = mapping[src], mapping[dst]
    
    adj = graph_to_adjlist(G_r)
    num_nodes = len(G_r.nodes())
    cuts_r = cpp.sets.minimalcuts(adj, src_r, dst_r, num_nodes, method)
    
    # Map back
    return [[reverse_mapping[n] for n in c] for c in cuts_r]


def evaluate_availability(
    graph_or_filepath,
    nodes_probabilities,
    algorithm,
    src=None,
    dst=None,
    parallel=False,
    count_link=False,
    edge_prob=None,
):
    """Evaluate network availability.

    Args:
        graph_or_filepath: NetworkX graph or path to pickle file.
        nodes_probabilities (dict): Node ID → availability probability.
        algorithm (str): 'mcs', 'pathset', or 'sdp'.
        src (int, optional): Source node (None for all pairs).
        dst (int, optional): Destination node (None for all pairs).
        parallel (bool): Use OpenMP parallelization.
        count_link (bool): Consider link (edge) availability.
        edge_prob (dict, optional): Edge → probability mapping.

    Returns:
        tuple or list[tuple]: (src, dst, availability) results.
    """
    # Load graph
    if isinstance(graph_or_filepath, str):
        G, _, _ = read_graph("", "", graph_or_filepath)
    elif hasattr(graph_or_filepath, "nodes") and hasattr(graph_or_filepath, "edges"):
        G = graph_or_filepath
    else:
        raise TypeError("Invalid graph input. Provide a file path or a NetworkX graph object.")

    # Validate
    if not isinstance(nodes_probabilities, dict):
        raise TypeError("nodes_probabilities must be a dictionary.")
    if len(nodes_probabilities) != len(G.nodes()):
        raise ValueError("nodes_probabilities must contain probabilities for all nodes.")
    if algorithm not in ALGORITHM_CONFIG:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(ALGORITHM_CONFIG.keys())}.")

    if src is not None and dst is not None:
        if src not in G.nodes() or dst not in G.nodes():
            raise ValueError(f"Source {src} or destination {dst} not found in graph.")
        return _eval_single_pair(G, nodes_probabilities, src, dst, algorithm,
                                  parallel, count_link, edge_prob)
    elif src is None and dst is None:
        return _eval_topology(G, nodes_probabilities, algorithm,
                               parallel, count_link, edge_prob)
    else:
        raise ValueError("Both source and destination must be specified or neither.")


def to_boolean_expression(G, src, dst, algorithm):
    """Convert results to a Boolean expression string.

    Args:
        G (nx.Graph): The graph.
        src (int): Source node.
        dst (int): Destination node.
        algorithm (str): Algorithm to use.

    Returns:
        str: Boolean expression string.
    """
    config = ALGORITHM_CONFIG[algorithm]
    cpp_module = getattr(cpp, config["cpp_module"])

    G_r, _, mapping = relabel_graph_A_dict(G, {})
    src_r, dst_r = mapping[src], mapping[dst]
    adj = graph_to_adjlist(G_r)

    if config["needs_cuts"]:
        problem_sets = cpp.sets.minimalcuts(adj, src_r, dst_r, max(G_r.nodes()) + 1)
    else:
        problem_sets = cpp.sets.minimalpaths(adj, src_r, dst_r)

    to_set_func = getattr(cpp_module, "to_probaset", None) or getattr(cpp_module, "to_sdp_set")
    result_set = to_set_func(src_r, dst_r, problem_sets)

    # Format as string
    return _format_bool_expr(result_set, algorithm)


# ================================================================
# Internal helpers
# ================================================================

def _eval_single_pair(G, A_dict, src, dst, algorithm, parallel=False,
                       count_link=False, edge_prob=None):
    """Evaluate availability for a single (src, dst) pair."""
    if count_link and not edge_prob:
        raise ValueError("Edge probabilities required when count_link is True.")

    config = ALGORITHM_CONFIG[algorithm]
    cpp_module = getattr(cpp, config["cpp_module"])

    if count_link:
        G, A_dict = to_link_graph(G, A_dict, edge_prob)

    G_r, A_dict_r, mapping = relabel_graph_A_dict(G, A_dict)
    src_r, dst_r = mapping[src], mapping[dst]
    adj = graph_to_adjlist(G_r)

    if config["needs_cuts"]:
        problem_sets = cpp.sets.minimalcuts(adj, src_r, dst_r, max(G_r.nodes()) + 1)
    else:
        problem_sets = cpp.sets.minimalpaths(adj, src_r, dst_r)

    if parallel and hasattr(cpp_module, "eval_avail_parallel"):
        availability = cpp_module.eval_avail_parallel(src_r, dst_r, A_dict_r, problem_sets)
    else:
        availability = cpp_module.eval_avail(src_r, dst_r, A_dict_r, problem_sets)

    return (src, dst, availability)


def _eval_topology(G, A_dict, algorithm, parallel=False,
                    count_link=False, edge_prob=None):
    """Evaluate availability for all node pairs."""
    if count_link and not edge_prob:
        raise ValueError("Edge probabilities required when count_link is True.")

    config = ALGORITHM_CONFIG[algorithm]
    cpp_module = getattr(cpp, config["cpp_module"])

    if count_link:
        G, A_dict = to_link_graph(G, A_dict, edge_prob)

    G_r, A_dict_r, mapping = relabel_graph_A_dict(G, A_dict)
    reverse_mapping = {v: k for k, v in mapping.items()}

    node_pairs = list(combinations(sorted(G_r.nodes()), 2))
    adj = graph_to_adjlist(G_r)

    if config["needs_cuts"]:
        problem_sets_list = [
            cpp.sets.minimalcuts(adj, s, d, max(G_r.nodes()) + 1)
            for s, d in node_pairs
        ]
    else:
        problem_sets_list = [
            cpp.sets.minimalpaths(adj, s, d)
            for s, d in node_pairs
        ]

    if parallel and hasattr(cpp_module, "eval_avail_topo_parallel"):
        availability_lst = cpp_module.eval_avail_topo_parallel(
            node_pairs, A_dict_r, problem_sets_list
        )
    else:
        availability_lst = cpp_module.eval_avail_topo(
            node_pairs, A_dict_r, problem_sets_list
        )

    return [
        (reverse_mapping[s], reverse_mapping[d], avail)
        for s, d, avail in availability_lst
    ]


def _format_bool_expr(result_set, algorithm):
    """Format a probability set or SDP set as a boolean expression string."""
    if algorithm == "sdp":
        # SDP format: list of list of SDP objects
        parts = []
        for sdp_list in result_set:
            terms = []
            for sdp in sdp_list:
                prefix = "-" if sdp.isComplementary() else ""
                elems = " * ".join(str(e) for e in sdp.getSet())
                terms.append(f"{prefix}[{elems}]")
            parts.append("[" + " * ".join(terms) + "]")
        return " + ".join(parts)
    else:
        # MCS/Pathset format: list of lists
        parts = []
        for num_list in result_set:
            elems = " * ".join(str(n) for n in num_list)
            parts.append(f"[{elems}]")
        return " + ".join(parts)


__all__ = [
    "evaluate_availability",
    "to_boolean_expression",
    "minimalpaths",
    "minimalcuts",
]
