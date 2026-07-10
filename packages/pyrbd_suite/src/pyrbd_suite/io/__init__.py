"""
pyrbd_suite.io — Topology and result I/O
========================================

Handles reading/writing topologies in JSON and Pickle formats,
as well as CSV-based cut set / path set data.
"""

import json
import os
import pickle as pkl
import networkx as nx
from itertools import combinations


# ==============================
# Graph / Topology IO
# ==============================

def read_graph(directory, top, file_path=None):
    """Read pickle file containing graph, positions, and labels.

    Args:
        directory (str): The directory containing the pickle file.
        top (str): The name of the topology.
        file_path (str, optional): The full path to the pickle file.

    Returns:
        tuple: (graph, positions, labels)
    """
    if file_path:
        with open(file_path, "rb") as handle:
            f = pkl.load(handle)
    else:
        with open(os.path.join(directory, "Pickle_" + top + ".pickle"), "rb") as handle:
            f = pkl.load(handle)

    G = f[0]
    pos = f[1]
    label = f[2]
    return G, pos, label


def read_topology_json(filepath):
    """Read a topology from a JSON file.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        dict: Topology data with keys: 'graph', 'positions', 'labels',
              'node_probabilities', 'metadata'.
    """
    with open(filepath, "r") as f:
        data = json.load(f)

    # Reconstruct NetworkX graph
    G = nx.node_link_graph(data.get("graph", {}))

    return {
        "graph": G,
        "positions": data.get("positions", {}),
        "labels": data.get("labels", {}),
        "node_probabilities": data.get("node_probabilities", {}),
        "metadata": data.get("metadata", {}),
    }


def save_topology_json(filepath, G, positions=None, labels=None,
                       node_probabilities=None, metadata=None):
    """Save a topology to a JSON file.

    Args:
        filepath (str): Path to the output JSON file.
        G (nx.Graph): The NetworkX graph.
        positions (dict, optional): Node positions for visualization.
        labels (dict, optional): Node labels.
        node_probabilities (dict, optional): Per-node availability probabilities.
        metadata (dict, optional): Additional metadata (name, description, etc.).
    """
    data = {
        "graph": nx.node_link_data(G),
        "positions": {str(k): list(v) for k, v in (positions or {}).items()},
        "labels": {str(k): v for k, v in (labels or {}).items()},
        "node_probabilities": {str(k): v for k, v in (node_probabilities or {}).items()},
        "metadata": metadata or {},
    }

    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


# ==============================
# CSV-based set data IO
# ==============================

def _read_csv_data(directory, top, prefix, column_name, file_path=None):
    """Helper function to read and parse CSV data."""
    import pandas as pd
    import ast

    if file_path:
        df = pd.read_csv(file_path)
    else:
        df = pd.read_csv(os.path.join(directory, f"{prefix}_{top}.csv"))

    df[column_name] = df[column_name].apply(ast.literal_eval)
    return df


def read_mincutsets(directory, top, file_path=None):
    """Read mincutsets from a CSV file.

    Args:
        directory (str): The directory containing the CSV file.
        top (str): The name of the topology.
        file_path (str, optional): Direct path to the CSV file.

    Returns:
        list: A list of mincutsets.
    """
    df = _read_csv_data(directory, top, "Mincutsets", "mincutsets", file_path)
    return df["mincutsets"].values.tolist()


def read_pathsets(directory, top, file_path=None):
    """Read pathsets from a CSV file.

    Args:
        directory (str): The directory containing the CSV file.
        top (str): The name of the topology.
        file_path (str, optional): Direct path to the CSV file.

    Returns:
        list: A list of pathsets.
    """
    df = _read_csv_data(directory, top, "Pathsets", "pathsets", file_path)
    return df["pathsets"].values.tolist()


def _save_set_data(directory, top, set_data, prefix, column_name):
    """Helper function to save set data to a CSV file."""
    import pandas as pd
    from tqdm import tqdm

    G, _, _ = read_graph(directory, top)
    node_pairs = list(combinations(G.nodes(), 2))

    data = []
    for (src, dst), sets in tqdm(
        zip(node_pairs, set_data),
        desc=f"Saving {prefix} for {top}",
        leave=False,
    ):
        if sets:
            data.append({
                "source": src,
                "target": dst,
                column_name: repr(sets),
                "length": len(sets),
            })

    df = pd.DataFrame(data)
    df.to_csv(os.path.join(directory, f"{prefix}_{top}.csv"), index=False)


def save_mincutsets(directory, top, mincutsets):
    """Save mincutsets to a CSV file."""
    _save_set_data(directory, top, mincutsets, "Mincutsets", "mincutsets")


def save_pathsets(directory, top, pathsets):
    """Save pathsets to a CSV file."""
    _save_set_data(directory, top, pathsets, "Pathsets", "pathsets")


__all__ = [
    "read_graph",
    "read_topology_json",
    "save_topology_json",
    "read_mincutsets",
    "read_pathsets",
    "save_mincutsets",
    "save_pathsets",
]
