from fastapi import APIRouter, HTTPException
import pyrbd_suite
from backend.models.analysis import AnalysisRequest, AvailabilityRequest
from backend.utils import storage

router = APIRouter()

def get_graph_and_probs(topology_name: str):
    topo = storage.load_topology(topology_name)
    if not topo:
        raise HTTPException(status_code=404, detail="Topology not found")
        
    G = storage.topology_to_networkx(topo)
    # Extract node probabilities dictionary
    node_prob = {n: topo.nodes[i].prob for i, n in enumerate(G.nodes())}
    return G, node_prob

@router.post("/minimal-cut-sets")
async def compute_minimal_cut_sets(req: AnalysisRequest):
    G, _ = get_graph_and_probs(req.topology_name)
    src = int(req.src) if req.src.isdigit() else req.src
    dst = int(req.dst) if req.dst.isdigit() else req.dst
    
    try:
        cuts = pyrbd_suite.minimalcuts(G, src, dst, method=req.method)
        # Convert output sets to lists for JSON serialization
        cuts_list = [list(c) for c in cuts]
        return {"cuts": cuts_list, "count": len(cuts_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/minimal-path-sets")
async def compute_minimal_path_sets(req: AnalysisRequest):
    G, _ = get_graph_and_probs(req.topology_name)
    src = int(req.src) if req.src.isdigit() else req.src
    dst = int(req.dst) if req.dst.isdigit() else req.dst
    
    try:
        paths = pyrbd_suite.minimalpaths(G, src, dst)
        paths_list = [list(p) for p in paths]
        return {"paths": paths_list, "count": len(paths_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/availability")
async def compute_availability(req: AvailabilityRequest):
    G, node_prob = get_graph_and_probs(req.topology_name)
    src = int(req.src) if req.src.isdigit() else req.src
    dst = int(req.dst) if req.dst.isdigit() else req.dst
    
    results = {}
    try:
        for method in req.methods:
            _, _, avail = pyrbd_suite.evaluate_availability(G, node_prob, algorithm=method, src=src, dst=dst)
            results[method] = avail
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
