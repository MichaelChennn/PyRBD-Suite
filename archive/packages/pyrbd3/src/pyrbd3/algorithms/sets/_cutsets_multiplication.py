from .pathsets import minimalpaths
from ._absorb_list import AbsorbList


def minimalcuts_multiplication(G, src, dst):
    # Get the minimal paths
    mps = minimalpaths(G, src, dst)

    # Return if src and dst are directly connected
    if len(mps) == 1 and [src, dst] in mps:
        return [[src], [dst]]

    # Sort the paths by length
    mps.sort(key=len)

    # Convert the minimal paths into two part: the first path and the rest paths
    # 1. remove src and dst from each path
    # 2. for the first path, initialize the temporary result with its each element as a set
    # 3. for the rest paths, convert each path into a set
    for i, mp in enumerate(mps):
        mp.remove(src)
        mp.remove(dst)
        mp.sort()

    # Multiply the pathsets
    result = multiply_pathsets(mps)

    # Convert the sets back to list of list
    result = [sorted(s) for s in result]
    result = sorted(result, key=lambda x: (len(x), x))

    return [[src], [dst], *result]


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
