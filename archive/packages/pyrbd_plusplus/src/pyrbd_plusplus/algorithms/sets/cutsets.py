from ._cutsets_combination import minimalcuts_combination
from ._cutsets_combination_matrix import minimalcuts_combination_matrix


def minimalcuts(H, src_, dst_, order=None, method="combination_matrix"):
    """Find minimal cut sets using specified method.

    Args:
        H (networkx.Graph): Graph
        src_ (int): Source node
        dst_ (int): Destination node
        order (int, optional): Order of the minimal cut sets. Defaults to None.
        method (str, optional): Method to use for finding minimal cut sets. Defaults to "combination_matrix". Can be "combination" or "combination_matrix".
    Raises:
        ValueError: If an unknown method is specified.

    Returns:
        list: A list of minimal cut sets
    """
    if method == "combination":
        return minimalcuts_combination(H, src_, dst_, order)
    elif method == "combination_matrix":
        return minimalcuts_combination_matrix(H, src_, dst_, order)
    else:
        raise ValueError(f"Unknown method: {method}")
