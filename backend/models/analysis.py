from pydantic import BaseModel
from typing import List, Optional

class AnalysisRequest(BaseModel):
    topology_name: str
    src: str
    dst: str
    method: str = "cnf_tree"

class AvailabilityRequest(BaseModel):
    topology_name: str
    src: str
    dst: str
    methods: List[str] = ["sdp", "mcs", "pathset"]
