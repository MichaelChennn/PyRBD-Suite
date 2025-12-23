from ._cutsets_cnf_tree import minimalcuts_cnf_tree
from ._cutsets_shannon import minimalcuts_shannon
from ._cutsets_multiplication import minimalcuts_multiplication

def minimalcuts(G, src, dst, method="cnf_tree"):
    """Find minimal cut sets between source and destination using specified method.

    Args:
        G (networkx.Graph): The input graph.
        src (int): The source node.
        dst (int): The destination node.
        method (str, optional): The method to use for finding minimal cut sets. Defaults to "cnf_tree". Options are "shannon", "cnf_tree", and "multiplication".

    Raises:
        ValueError: If an unknown method is specified.

    Returns:
        list: A list of minimal cut sets.
    """
    if method == "shannon":
        return minimalcuts_shannon(G, src, dst)
    elif method == "cnf_tree":
        return minimalcuts_cnf_tree(G, src, dst)
    elif method == "multiplication":
        return minimalcuts_multiplication(G, src, dst)
    else:
        raise ValueError(f"Unknown method: {method}")