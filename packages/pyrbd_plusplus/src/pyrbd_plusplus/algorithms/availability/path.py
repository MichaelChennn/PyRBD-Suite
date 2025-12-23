from .engine import to_boolean_expression, eval_single_pair, eval_topology

def pathset_to_boolexpr(G, src, dst):
    """Convert a pathset to a Boolean expression."""
    return to_boolean_expression(G, src, dst, 'pathset')

def eval_avail_pathset(G, A_dict, src, dst):
    """Evaluate the availability of a pathset for a single source-destination pair."""
    return eval_single_pair(G, A_dict, src, dst, 'pathset')

def eval_avail_link_pathset(G, A_dict, src, dst, edge_prob):
    """Evaluate the availability of a pathset for a single source-destination pair with link counting."""
    return eval_single_pair(G, A_dict, src, dst, 'pathset', count_link=True, edge_prob=edge_prob)

def eval_avail_topo_pathset(G, A_dict):
    """Evaluate the availability of a pathset for the entire topology."""
    return eval_topology(G, A_dict, 'pathset')

def eval_avail_link_topo_pathset(G, A_dict, edge_prob):
    """Evaluate the availability of a pathset for the entire topology with link counting."""
    return eval_topology(G, A_dict, 'pathset', count_link=True, edge_prob=edge_prob)

def eval_avail_topo_pathset_parallel(G, A_dict):
    """Evaluate the availability of a pathset for the entire topology in parallel."""
    return eval_topology(G, A_dict, 'pathset', parallel=True)

def eval_avail_link_topo_pathset_parallel(G, A_dict, edge_prob):
    """Evaluate the availability of a pathset for the entire topology with link counting in parallel."""
    return eval_topology(G, A_dict, 'pathset', parallel=True, count_link=True, edge_prob=edge_prob)
