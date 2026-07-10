"""
pyrbd_suite — Unified Python wrapper for PyRBD-Suite
====================================================

Public API:
    - pyrbd_suite.io: Topology and result I/O (JSON/Pickle)
    - pyrbd_suite.graph: NetworkX graph preparation (adjacency list, link graph)
    - pyrbd_suite.analysis: Availability evaluation (evaluate_availability)
"""

from pyrbd_suite.io import *
from pyrbd_suite.graph import *
from pyrbd_suite.analysis import *

__version__ = "1.0.0"

__all__ = [
    # IO
    "read_graph",
    "read_topology_json",
    "save_topology_json",
    "read_mincutsets",
    "read_pathsets",
    "save_mincutsets",
    "save_pathsets",
    # Graph
    "graph_to_adjlist",
    "to_link_graph",
    "relabel_graph_A_dict",
    # Analysis
    "evaluate_availability",
    "to_boolean_expression",
    "minimalpaths",
    "minimalcuts",
]
