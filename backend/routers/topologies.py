from fastapi import APIRouter, HTTPException
from typing import List, Dict
import os

from backend.models.topology import TopologyModel
from backend.utils import storage

router = APIRouter()

@router.get("/", response_model=List[str])
async def list_topologies():
    return storage.list_topologies()

@router.get("/{name}", response_model=TopologyModel)
async def get_topology(name: str):
    topo = storage.load_topology(name)
    if not topo:
        raise HTTPException(status_code=404, detail="Topology not found")
    return topo

@router.post("/", response_model=TopologyModel)
async def save_topology(topology: TopologyModel):
    storage.save_topology(topology)
    return topology

@router.delete("/{name}")
async def delete_topology(name: str):
    path = storage.get_topology_path(name)
    if os.path.exists(path):
        os.remove(path)
        return {"status": "deleted", "name": name}
    raise HTTPException(status_code=404, detail="Topology not found")

@router.post("/import/pickle", response_model=Dict[str, List[str]])
async def import_pickle_topologies():
    """Import all legacy pickle topologies into JSON format."""
    # The topologies are in the root 'topologies/' directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pickle_dir = os.path.join(project_root, "topologies")
    
    imported = storage.import_pickle_topologies(pickle_dir)
    return {"imported": imported}
