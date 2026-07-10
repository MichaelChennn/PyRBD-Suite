import pytest
import pyrbd_suite

# Tolerance for floating point availability equivalence
TOL = 1e-9

def test_eval_single_pair_sdp(germany17_data):
    from itertools import combinations
    G, node_prob = germany17_data
    from pyrbd3.algorithms.availability.engine import evaluate_availability as pyrbd3_eval
    
    for src, dst in combinations(G.nodes(), 2):
        new_avail = pyrbd_suite.evaluate_availability(G, node_prob, src=src, dst=dst, algorithm="sdp")
        old_avail = pyrbd3_eval(G, node_prob, algorithm="sdp", src=src, dst=dst, parallel=False)
        assert new_avail[2] == pytest.approx(old_avail[2], abs=TOL), f"SDP mismatch at {src}->{dst}"


@pytest.mark.parametrize("algorithm", ["mcs", "pathset"])
def test_eval_single_pair_plusplus(germany17_data, algorithm):
    from itertools import combinations
    G, node_prob = germany17_data
    from pyrbd_plusplus.algorithms.availability.engine import evaluate_availability as pypp_eval
    
    for src, dst in combinations(G.nodes(), 2):
        new_avail = pyrbd_suite.evaluate_availability(G, node_prob, src=src, dst=dst, algorithm=algorithm)
        old_avail = pypp_eval(G, node_prob, src=src, dst=dst, algorithm=algorithm, parallel=False)
        assert new_avail[2] == pytest.approx(old_avail[2], abs=TOL), f"{algorithm} mismatch at {src}->{dst}"


def test_eval_topology_sdp(usa26_data):
    """Test full topology calculations for SDP."""
    G, node_prob = usa26_data
    
    # Sequential
    new_all = pyrbd_suite.evaluate_availability(G, node_prob, algorithm="sdp", parallel=False)
    
    from pyrbd3.algorithms.availability.engine import evaluate_availability as pyrbd3_eval
    old_all = pyrbd3_eval(G, node_prob, algorithm="sdp", parallel=False)
    
    # Ensure all lengths and elements match
    assert len(new_all) == len(old_all)
    
    # Sort just in case iterator ordering is different
    new_all.sort()
    old_all.sort()
    
    for n, o in zip(new_all, old_all):
        assert n[0] == o[0] and n[1] == o[1]
        assert n[2] == pytest.approx(o[2], abs=TOL), f"Topology SDP mismatch at {n[0]}->{n[1]}"


def test_eval_topology_parallel_consistency(usa26_data):
    """Ensure parallel evaluates to exactly the same values as sequential in the new suite."""
    G, node_prob = usa26_data
    
    seq_all = pyrbd_suite.evaluate_availability(G, node_prob, algorithm="sdp", parallel=False)
    par_all = pyrbd_suite.evaluate_availability(G, node_prob, algorithm="sdp", parallel=True)
    
    seq_all.sort()
    par_all.sort()
    
    for s, p in zip(seq_all, par_all):
        assert s[0] == p[0] and s[1] == p[1]
        assert s[2] == pytest.approx(p[2], abs=1e-12), "Parallel output diverged from sequential!"


def test_link_counted_availability(germany17_data):
    """Test link-counted functionality against legacy for all pairs."""
    from itertools import combinations
    G, node_prob = germany17_data
    edge_prob = {edge: 0.95 for edge in G.edges()}
    
    from pyrbd3.algorithms.availability.engine import evaluate_availability as pyrbd3_eval
    
    for src, dst in combinations(G.nodes(), 2):
        new_link = pyrbd_suite.evaluate_availability(
            G, node_prob, algorithm="sdp", 
            src=src, dst=dst, count_link=True, edge_prob=edge_prob
        )
        old_link = pyrbd3_eval(
            G, node_prob, algorithm="sdp", src=src, dst=dst, 
            count_link=True, edge_prob=edge_prob, parallel=False
        )
        assert new_link[2] == pytest.approx(old_link[2], abs=TOL), f"Link-counted mismatch at {src}->{dst}!"
