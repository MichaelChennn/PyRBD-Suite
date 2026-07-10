import pytest
import os
import sys
import subprocess
import networkx as nx
import pickle as pkl

import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "archive")
def build_legacy_package(pkg_name):
    """Build the legacy C++ extension if not already built."""
    pkg_dir = os.path.join(ARCHIVE_DIR, "packages", pkg_name)
    core_dir = os.path.join(pkg_dir, "src", pkg_name, "_core")
    
    so_files = [f for f in os.listdir(core_dir) if f.endswith(".so")] if os.path.exists(core_dir) else []
    if not so_files:
        print(f"\n[conftest] Compiling legacy {pkg_name} C++ extension...")
        build_dir = os.path.join(pkg_dir, "build")
        os.makedirs(build_dir, exist_ok=True)
        try:
            subprocess.run(["cmake", ".."], cwd=build_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["make", "-j"], cwd=build_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[conftest] {pkg_name} compiled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to compile {pkg_name}:\n{e.stderr.decode()}")
            raise e

def pytest_sessionstart(session):
    """Called before tests run. Sets up sys.path and compiles legacy code."""
    build_legacy_package("pyrbd3")
    build_legacy_package("pyrbd_plusplus")
    
    # Inject legacy packages into sys.path
    pyrbd3_path = os.path.join(ARCHIVE_DIR, "packages", "pyrbd3", "src")
    pyrbdpp_path = os.path.join(ARCHIVE_DIR, "packages", "pyrbd_plusplus", "src")
    pyrbd_utils_path = os.path.join(ARCHIVE_DIR, "packages", "pyrbd_utils", "src")
    
    if pyrbd_utils_path not in sys.path:
        sys.path.insert(0, pyrbd_utils_path)
    if pyrbd3_path not in sys.path:
        sys.path.insert(0, pyrbd3_path)
    if pyrbdpp_path not in sys.path:
        sys.path.insert(0, pyrbdpp_path)


@pytest.fixture(scope="session")
def germany17_data():
    """Returns (G, node_prob) for Germany_17 topology."""
    topo = "Germany_17"
    path = os.path.join(PROJECT_ROOT, "topologies", topo, f"Pickle_{topo}.pickle")
    
    with open(path, "rb") as f:
        data = pkl.load(f)
    
    G = data[0]
    # Standard prob mapping: node -> 0.9
    node_prob = {node: 0.9 for node in G.nodes()}
    
    return G, node_prob

@pytest.fixture(scope="session")
def usa26_data():
    """Returns (G, node_prob) for USA_26 topology."""
    topo = "USA_26"
    path = os.path.join(PROJECT_ROOT, "topologies", topo, f"Pickle_{topo}.pickle")
    
    with open(path, "rb") as f:
        data = pkl.load(f)
    
    G = data[0]
    node_prob = {node: 0.9 for node in G.nodes()}
    
    return G, node_prob
