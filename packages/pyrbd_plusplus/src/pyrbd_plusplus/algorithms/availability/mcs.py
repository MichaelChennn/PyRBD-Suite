from .engine import to_boolean_expression, eval_single_pair, eval_topology

def mcs_to_boolexpr(G, src, dst):
    """Convert a Minimal Cut Set (MCS) to a Boolean expression."""
    return to_boolean_expression(G, src, dst, 'mcs')

def eval_avail_mcs(G, A_dict, src, dst):
    """Evaluate the availability of a Minimal Cut Set (MCS) for a single source-destination pair."""
    return eval_single_pair(G, A_dict, src, dst, 'mcs')

def eval_avail_link_mcs(G, A_dict, src, dst, edge_prob):
    """Evaluate the availability of a Minimal Cut Set (MCS) for a single source-destination pair with link counting."""
    return eval_single_pair(G, A_dict, src, dst, 'mcs', count_link=True, edge_prob=edge_prob)

def eval_avail_topo_mcs(G, A_dict):
    """Evaluate the availability of a Minimal Cut Set (MCS) for the entire topology."""
    return eval_topology(G, A_dict, 'mcs')

def eval_avail_link_topo_mcs(G, A_dict, edge_prob):
    """Evaluate the availability of a Minimal Cut Set (MCS) for the entire topology with link counting."""
    return eval_topology(G, A_dict, 'mcs', count_link=True, edge_prob=edge_prob)

def eval_avail_topo_mcs_parallel(G, A_dict):
    """Evaluate the availability of a Minimal Cut Set (MCS) for the entire topology in parallel."""
    return eval_topology(G, A_dict, 'mcs', parallel=True)

def eval_avail_link_topo_mcs_parallel(G, A_dict, edge_prob):
    """Evaluate the availability of a Minimal Cut Set (MCS) for the entire topology with link counting in parallel."""
    return eval_topology(G, A_dict, 'mcs', parallel=True, count_link=True, edge_prob=edge_prob)