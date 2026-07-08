import numpy as np
from ._absorb_list import AbsorbList
from .pathsets import minimalpaths


def minimalcuts_shannon(G, src, dst):
    # Get the minimal paths
    mps = minimalpaths(G, src, dst)

    # Return if src and dst are directly connected
    if len(mps) == 1 and [src, dst] in mps:
        return [[src], [dst]]

    # Sort the paths by length
    mps.sort(key=len)

    # remove src and dst from each path
    for mp in mps:
        mp.remove(src)
        mp.remove(dst)

    # Convert each path into a CNF
    pathsets = [set(mp) for mp in mps]

    # Do the Shannon expansion
    result = shannon_expansion(pathsets, max(G.nodes()))

    # Convert the sets back to list of list
    temp_result = [sorted(s) for s in result]
    sorted_result = sorted(temp_result, key=lambda x: (len(x), x))

    return [[src], [dst], *sorted_result]


def shannon_expansion(pathsets, max_node):
    # Find the most common element and its count
    pivot_elem, counts = most_common_element(pathsets, max_node)

    if counts < 2:
        return multiply_pathsets(pathsets)
    else:
        left_subset = []
        right_subset = []
        for subset in pathsets:
            left_subset.append(subset - {pivot_elem})
            if pivot_elem not in subset:
                right_subset.append(subset)
        # Append pivot element to the end of the right results
        right_subset.append({pivot_elem})

    # Multiply the two subsets
    left_result = multiply_pathsets(left_subset)
    right_result = multiply_pathsets(right_subset)

    # Combine the two results
    absorbed_list = AbsorbList()
    absorbed_list.add_many(left_result)
    absorbed_list.add_many(right_result)

    result = absorbed_list.to_set_list()
    return result


def most_common_element(pathsets, max_node):
    """Couts the most common element

    Args:
        pathsets (list of sets): list of sets of paths
        max_node (int): max node index

    Returns:
       most_common_element (int), count (int)
    """
    counts = np.zeros(max_node + 1, dtype=np.int32)
    for subset in pathsets:
        counts[list(subset)] += 1
    idx = np.argmax(counts)

    return int(idx), int(counts[int(idx)])


def multiply_pathsets(pathsets):
    """
    Multiply all the sets in the pathsets list.
    Initialize the result with the first set.
    Then multiply the result with each subsequent set.
    """
    if not pathsets:
        return []

    # Initialize the result with the first set
    result = [{elem} for elem in pathsets[0]]

    # Multiply the result with each subsequent set
    for s in pathsets[1:]:
        result = multiply_two_pathsets(result, set(s))

    return result


def multiply_two_pathsets(partial_set_list, factor_set):
    """
    Multiply each set in the partial_set_list with the factor_set.
    For each partial set in the list, merge it with each element in the factor_set if they are disjoint.
    Else keep the original set.
    Add all the new sets in a list
    """
    absorbed_list = AbsorbList()

    for partial_set in partial_set_list:
        if partial_set.isdisjoint(factor_set):
            for f in factor_set:
                new_set = partial_set.union({f})
                absorbed_list.add(new_set)
        else:
            absorbed_list.add(partial_set)

    return absorbed_list.to_set_list()
