from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_topologies():
    # Import all legacy topologies so analysis tests can use them
    client.post("/api/topologies/import/pickle")
    yield

def test_minimal_paths_api():
    # Germany_17, nodes 0->1
    req = {
        "topology_name": "Germany_17",
        "src": "0",
        "dst": "1",
        "method": "dfs"
    }
    response = client.post("/api/analysis/minimal-path-sets", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    # Check that paths are lists of integers (or strings representing ints)
    paths = data["paths"]
    # In Germany_17 0->1, paths should contain [0, 13, 1] or similar
    assert any(13 in p and 1 in p for p in paths)

def test_minimal_cuts_api():
    req = {
        "topology_name": "Germany_17",
        "src": "0",
        "dst": "1",
        "method": "cnf_tree"
    }
    response = client.post("/api/analysis/minimal-cut-sets", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 7
    cuts = data["cuts"]
    # Check that single node cuts exist
    assert [0] in cuts
    assert [1] in cuts
    # Check that [13, 14, 16] exists
    assert sorted([13, 14, 16]) in [sorted(c) for c in cuts]

def test_availability_api():
    req = {
        "topology_name": "Germany_17",
        "src": "0",
        "dst": "1",
        "methods": ["sdp", "mcs"]
    }
    response = client.post("/api/analysis/availability", json=req)
    assert response.status_code == 200
    data = response.json()
    assert "sdp" in data
    assert "mcs" in data
    assert type(data["sdp"]) == float
    assert data["sdp"] > 0.0
