from fastapi.testclient import TestClient
import os
import json

from backend.main import app
from backend.models.topology import TopologyModel

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_topology_crud():
    # 1. Create a dummy topology
    topo_data = {
        "name": "test_topo_api",
        "nodes": [
            {"id": "0", "label": "node0", "prob": 0.9, "x": 10.0, "y": 20.0},
            {"id": "1", "label": "node1", "prob": 0.95, "x": 30.0, "y": 40.0}
        ],
        "edges": [
            {"source": "0", "target": "1", "prob": 0.99}
        ]
    }
    
    # Save
    response = client.post("/api/topologies/", json=topo_data)
    assert response.status_code == 200
    assert response.json()["name"] == "test_topo_api"
    
    # List
    response = client.get("/api/topologies/")
    assert response.status_code == 200
    assert "test_topo_api" in response.json()
    
    # Get
    response = client.get("/api/topologies/test_topo_api")
    assert response.status_code == 200
    assert response.json()["name"] == "test_topo_api"
    assert len(response.json()["nodes"]) == 2
    
    # Delete
    response = client.delete("/api/topologies/test_topo_api")
    assert response.status_code == 200
    
    # List again to ensure it's deleted
    response = client.get("/api/topologies/")
    assert "test_topo_api" not in response.json()

def test_import_pickle():
    # Import
    response = client.post("/api/topologies/import/pickle")
    assert response.status_code == 200
    imported = response.json()["imported"]
    
    # Should have imported Germany_17, Abilene, USA_26 etc.
    assert "Germany_17" in imported
    assert "Abilene" in imported
    
    # Verify we can get Germany_17
    response = client.get("/api/topologies/Germany_17")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Germany_17"
    assert len(data["nodes"]) == 17
