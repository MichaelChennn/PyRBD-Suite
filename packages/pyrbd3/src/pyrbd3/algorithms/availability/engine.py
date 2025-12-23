from itertools import combinations
from ...algorithms.sets import minimalpaths
from pyrbd_utils import relabel_graph_A_dict, read_graph, sdp_boolexpr_to_str, to_link_graph
import pyrbd3._core.pyrbd3_cpp as cpp

# Algorithm Configuration
ALGORITHM_CONFIG = {
    'sdp': {
        'cpp_module': 'sdp',
        'problem_set_func': minimalpaths,  # SDP is based on pathsets
        'bool_expr_func': sdp_boolexpr_to_str,
        'to_set_func': 'to_sdp_set',
    }
}

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
    """Evaluate the availability of a network based on the given parameters.

    Args:
        graph_or_filepath (Union[str, nx.Graph]): Either a file path to the graph pickle data or a NetworkX graph object.
        nodes_probabilities (dict): A dictionary mapping node IDs to their availability probabilities.
        algorithm (str): The algorithm to use for evaluation. Can be 'mcs' or 'pathset'.
        src (int, optional): The source node ID. Defaults to None.
        dst (int, optional): The destination node ID. Defaults to None.
        parallel (bool, optional): Whether to evaluate in parallel. Defaults to False.
        count_link (bool, optional): Whether to consider link availability. Defaults to False.
        edge_prob (dict, optional): A dictionary mapping edge tuples to their availability probabilities if count
    """
    # Read the graph from the specified directory and topology
    if isinstance(graph_or_filepath, str):
        G, _, _ = read_graph("", "", graph_or_filepath)
    elif hasattr(graph_or_filepath, "nodes") and hasattr(graph_or_filepath, "edges"):
        # Assume graph_or_filepath is a networkx.Graph object
        G = graph_or_filepath
    else:
        raise TypeError(
            "Invalid graph input. Provide a file path or a NetworkX graph object."
        )
    # Validate the nodes_probabilities
    if not isinstance(nodes_probabilities, dict):
        raise TypeError(
            "nodes_probabilities must be a dictionary mapping node IDs to probabilities."
        )
    if len(nodes_probabilities) != len(G.nodes()):
        raise ValueError(
            "nodes_probabilities must contain probabilities for all nodes in the graph."
        )

    # Validate source and destination nodes
    if src is not None and dst is not None:
        if src not in G.nodes() or dst not in G.nodes():
            raise ValueError(
                f"Source node {src} or destination node {dst} not found in the graph."
            )
        return eval_single_pair(G, nodes_probabilities, src, dst, algorithm, parallel, count_link, edge_prob)
    elif src is None and dst is None:
        return eval_topology(G, nodes_probabilities, algorithm, parallel, count_link, edge_prob)
    else:
        raise ValueError(
            "Both source and destination nodes must be specified or neither."
        )

def to_boolean_expression(G, src, dst, algorithm):
    """Convert a SUM of Disjoint Products (SDP) to a Boolean expression.
    
    Args:
        G (networkx.Graph): The graph representation of the topology.
        src (int): The source node index.
        dst (int): The destination node index.
        algorithm (str): The algorithm to use for generating the Boolean expression. Can be 'mcs', 'pathset', 'sdp', or 'pyrbd'.
    
    Returns:
        bool_expr (str): A string representation of the Boolean expression.
    """
    if algorithm not in ALGORITHM_CONFIG:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(ALGORITHM_CONFIG.keys())}.")
        
    # Get algorithm configuration
    config = ALGORITHM_CONFIG[algorithm]
    cpp_module = getattr(cpp, config['cpp_module'])
    
    # Relabel
    G_relabel, _, relabel_mapping = relabel_graph_A_dict(G, {})
    src_relabel = relabel_mapping[src]
    dst_relabel = relabel_mapping[dst]
    
    # Get problem sets
    problem_sets = config['problem_set_func'](G_relabel, src_relabel, dst_relabel)
    
    # Convert to probability set or SDP set
    to_set_func = getattr(cpp_module, config['to_set_func'])
    result_set = to_set_func(src_relabel, dst_relabel, problem_sets)
    
    # Convert to boolean expression
    return config['bool_expr_func'](result_set)

def eval_single_pair(G, A_dict, src, dst, algorithm, parallel=False, count_link=False, edge_prob=None):
    """Evaluate the availability of a source and destination pair in the topology using SDP.
    
    Args:
        G (networkx.Graph): The graph representation.
        A_dict (dict): A dictionary mapping nodes to their availability.
        src (int): The source node index.
        dst (int): The destination node index.
        algorithm (str): The algorithm to use for evaluation ('mcs', 'pathset', or 'sdp').
        parallel (bool): Whether to use parallel evaluation if available.
        count_link (bool): Whether to consider link availability.
        edge_prob (dict): A dictionary mapping edges to their availability if count_link is True.
    
    Raises:
        ValueError: If the specified algorithm does not support parallel evaluation.
    
    Returns:
        tuple: (src, dst, availability)
    """
    # Validate algorithm
    if algorithm not in ALGORITHM_CONFIG:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(ALGORITHM_CONFIG.keys())}.")
    
    if count_link and not edge_prob:
        raise ValueError("Edge probabilities must be provided when count_link is True.")
    
    # Get algorithm configuration
    config = ALGORITHM_CONFIG[algorithm]
    cpp_module = getattr(cpp, config['cpp_module'])
    
    # Handle link counting
    if count_link:
        # Convert to link graph
        G, A_dict = to_link_graph(G, A_dict, edge_prob)

    # Relabel
    G_relabel, A_dict_relabeled, relabel_mapping = relabel_graph_A_dict(G, A_dict)
    src_relabel = relabel_mapping[src]
    dst_relabel = relabel_mapping[dst]
    
    # Get problem sets
    problem_sets = config['problem_set_func'](G_relabel, src_relabel, dst_relabel)
    
    # Choose evaluation method
    if parallel:
        if hasattr(cpp_module, 'eval_avail_parallel'):
            availability = cpp_module.eval_avail_parallel(
                src_relabel, dst_relabel, A_dict_relabeled, problem_sets
            )
        else:
            raise ValueError(f"Parallel evaluation not available for {algorithm} algorithm.")
    else:
        availability = cpp_module.eval_avail(
            src_relabel, dst_relabel, A_dict_relabeled, problem_sets
        )
    
    return (src, dst, availability)

def eval_topology(G, A_dict, algorithm, parallel=False, count_link=False, edge_prob=None):
    """Evaluate the availability for all pairs of nodes in the topology using SDP.

    Args:
        G (networkx.Graph): The graph representation.
        A_dict (dict): A dictionary mapping nodes to their availability.
        algorithm (str): The algorithm to use for evaluation ('mcs', 'pathset', or 'sdp').
        parallel (bool): Whether to use parallel evaluation if available.
        count_link (bool): Whether to consider link availability.
        edge_prob (dict): A dictionary mapping edges to their availability if count_link is True.
        
    Raises:
        ValueError: If the specified algorithm does not support parallel evaluation.
    
    Returns:
        List[tuple]: A list of tuples, each containing (src, dst, availability).
    """
    # Validate algorithm
    if algorithm not in ALGORITHM_CONFIG:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(ALGORITHM_CONFIG.keys())}.")
        
    if count_link and not edge_prob:
        raise ValueError("Edge probabilities must be provided when count_link is True.")
    
    # Get algorithm configuration
    config = ALGORITHM_CONFIG[algorithm]
    cpp_module = getattr(cpp, config['cpp_module'])
    
    # Handle link counting
    if count_link:
        # Convert to link graph
        G, A_dict = to_link_graph(G, A_dict, edge_prob)
    
    # Relabel
    G_relabel, A_dict_relabeled, relabel_mapping = relabel_graph_A_dict(G, A_dict)
    reverse_mapping = {v: k for k, v in relabel_mapping.items()}
    
    # Get all pairs
    node_pairs = list(combinations(G_relabel.nodes(), 2))
    
    # Get all problem sets
    problem_sets_list = [
        config['problem_set_func'](G_relabel, src, dst)
        for src, dst in node_pairs
    ]

    # Choose evaluation method
    if parallel:
        if hasattr(cpp_module, 'eval_avail_topo_parallel'):
            availability_lst = cpp_module.eval_avail_topo_parallel(
                node_pairs, A_dict_relabeled, problem_sets_list
            )
        else:
            raise ValueError(f"Parallel evaluation not available for {algorithm} algorithm.")
    else:
        availability_lst = cpp_module.eval_avail_topo(
            node_pairs, A_dict_relabeled, problem_sets_list
        )
    
    # Relabel results
    return [
        (reverse_mapping[src], reverse_mapping[dst], availability)
        for src, dst, availability in availability_lst
    ]