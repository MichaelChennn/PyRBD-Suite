from itertools import combinations
from ._cnf_decision_tree import CNFDecisionTree
from .pathsets import minimalpaths


def minimalcuts_cnf_tree(G, src, dst):
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

    # Create a tree structure
    tree = CNFDecisionTree(pathsets, max(G.nodes()))
    tree.evaluate_all()

    evaluation = tree.__getattribute__("evaluation")

    # Convert the sets back to list of list
    temp_result = [sorted(s) for s in evaluation]
    sorted_result = sorted(temp_result, key=lambda x: (len(x), x))

    return [[src], [dst], *sorted_result]
