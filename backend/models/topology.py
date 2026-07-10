from pydantic import BaseModel, Field
from typing import List, Optional

class NodeModel(BaseModel):
    id: str
    label: str
    prob: float = Field(default=1.0, description="Reliability/probability of the node")
    x: float = Field(default=0.0, description="X coordinate for visualization")
    y: float = Field(default=0.0, description="Y coordinate for visualization")

class EdgeModel(BaseModel):
    source: str
    target: str
    prob: float = Field(default=1.0, description="Reliability/probability of the edge")

class TopologyModel(BaseModel):
    name: str
    nodes: List[NodeModel]
    edges: List[EdgeModel]
