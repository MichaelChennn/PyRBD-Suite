import pytest
import pyrbd_suite

def canonicalize(sets):
    """Sort individual sets and the list of sets to ensure order independence."""
    if not sets:
        return []
    sorted_sets = [sorted(list(s)) for s in sets]
    sorted_sets.sort(key=lambda s: (len(s), s))
    return sorted_sets

def test_minimal_paths(germany17_data):
    """Test DFS pathset generation matches pyrbd_plusplus for all node pairs."""
    from itertools import combinations
    G, _ = germany17_data
    
    from pyrbd_plusplus.algorithms.sets import pathsets as legacy_pathsets
    
    for src, dst in combinations(G.nodes(), 2):
        new_paths = pyrbd_suite.minimalpaths(G, src, dst)
        old_paths = legacy_pathsets.minimalpaths(G, src, dst)
        assert canonicalize(new_paths) == canonicalize(old_paths), f"Minimal paths mismatch for {src}->{dst}!"


@pytest.mark.parametrize("method, legacy_pkg", [
    ("cnf_tree", "pyrbd3"),
    ("shannon", "pyrbd3"),
    ("multiplication", "pyrbd3")
])
def test_minimal_cuts(germany17_data, method, legacy_pkg):
    """Test mincut generation against corresponding legacy package implementations for all pairs."""
    from itertools import combinations
    G, _ = germany17_data
    
    # Preload legacy wrappers
    if legacy_pkg == "pyrbd3":
        import pyrbd3.algorithms.sets.cutsets as py3_cuts
        func_map = {
            "cnf_tree": py3_cuts.minimalcuts_cnf_tree,
            "shannon": py3_cuts.minimalcuts_shannon,
            "multiplication": py3_cuts.minimalcuts_multiplication
        }
    else:
        import pyrbd_plusplus.algorithms.sets.cutsets as pypp_cuts
        func_map = {
            "combination": pypp_cuts.minimalcuts_combination,
            "combination_matrix": pypp_cuts.minimalcuts_combination_matrix
        }
        
    for src, dst in combinations(G.nodes(), 2):
        new_cuts = pyrbd_suite.minimalcuts(G, src, dst, method=method)
        
        if legacy_pkg == "pyrbd_plusplus":
            # The legacy pyrbd_plusplus implementation of combination and combination_matrix 
            # had bugs: it failed to append {src} and {dst}, and its superset-pruning logic 
            # missed some elements (e.g., returning non-minimal cuts).
            # Therefore, we test the new combination implementations against the mathematically 
            # verified cnf_tree baseline from the new suite.
            baseline_cuts = pyrbd_suite.minimalcuts(G, src, dst, method="cnf_tree")
            assert canonicalize(new_cuts) == canonicalize(baseline_cuts), f"New {method} does not match new cnf_tree at {src}->{dst}!"
        else:
            old_cuts = func_map[method](G, src, dst)
            assert canonicalize(new_cuts) == canonicalize(old_cuts), f"Minimal cuts mismatch for {method} at {src}->{dst}!"
