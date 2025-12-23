import networkx as nx
import os
import pickle as pkl
import pandas as pd
import ast
from itertools import combinations
from tqdm import tqdm


# ==============================
# FileIO Functions
# ==============================
def read_graph(directory, top, file_path=None):
    """Read pickle file containing graph, positions, and labels.

    Args:
        directory (str): The directory containing the pickle file.
        top (str): The name of the topology.
        file_path (str, optional): The full path to the pickle file. Defaults to None.

    Notes:
        If file_path is provided, it will be used directly.
        Otherwise, the function constructs the file path using the directory and topology name.
        The pickle file is expected to be named "Pickle_<top>.pickle".

    Returns:
        tuple: A tuple containing the graph, positions, and labels.
    """
    # Read the pickle file
    if file_path:
        with open(file_path, "rb") as handle:
            f = pkl.load(handle)
    else:
        with open(os.path.join(directory, "Pickle_" + top + ".pickle"), "rb") as handle:
            f = pkl.load(handle)

    # Extract graph, positions, and labels
    G = f[0]
    pos = f[1]
    label = f[2]

    return G, pos, label


def _read_csv_data(directory, top, prefix, column_name, file_path=None):
    """Helper function to read and parse CSV data."""
    if file_path:
        df = pd.read_csv(file_path)
    else:
        df = pd.read_csv(os.path.join(directory, f"{prefix}_{top}.csv"))

    # Convert the column from string representation to actual list
    df[column_name] = df[column_name].apply(ast.literal_eval)

    return df


def read_mincutsets(directory, top, file_path=None):
    """Read mincutsets from a csv file.

    Args:
        directory (str): The directory containing the CSV file.
        top (str): The name of the topology.
        file_path (str, optional): The full path to the CSV file. Defaults to None.

    Notes:
        If file_path is provided, it will be used directly.
        Otherwise, the function constructs the file path using the directory and topology name.
        The CSV file is expected to be named "Mincutsets_<top>.csv"

    Returns:
        mincutsets (list): A list of mincutsets.
    """
    # Read the csv file
    df = _read_csv_data(directory, top, "Mincutsets", "mincutsets", file_path)

    return df["mincutsets"].values.tolist()


def read_pathsets(directory, top, file_path=None):
    """Read pathsets from a csv file.

    Args:
        directory (str): The directory containing the CSV file.
        top (str): The name of the topology.
        file_path (str, optional): The full path to the CSV file. Defaults to None.

    Notes:
        If file_path is provided, it will be used directly.
        Otherwise, the function constructs the file path using the directory and topology name.
        The CSV file is expected to be named "Pathsets_<top>.csv"

    Returns:
        pathsets (list): A list of pathsets.
    """
    # Read the csv file
    df = _read_csv_data(directory, top, "Pathsets", "pathsets", file_path)

    return df["pathsets"].values.tolist()


def _save_set_data(directory, top, set_data, prefix, column_name):
    """Helper function to save set data to a CSV file."""
    # Read the graph from the pickle file
    G, _, _ = read_graph(directory, top)

    # Get all node pairs
    node_pairs = list(combinations(G.nodes(), 2))

    # Initialize a list to store set data
    data = []

    # Iterate through each pair of nodes and the corresponding set data
    for (src, dst), sets in tqdm(
        zip(node_pairs, set_data),
        desc=f"Saving {prefix} for {top}",
        leave=False,
    ):
        if sets:
            data.append(
                {
                    "source": src,
                    "target": dst,
                    column_name: repr(sets),
                    "length": len(sets),
                }
            )

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(os.path.join(directory, f"{prefix}_{top}.csv"), index=False)


def save_mincutsets(directory, top, mincutsets):
    """Save mincutsets to a CSV file

    Args:
        directory (str): The directory containing the CSV file.
        top (str): The name of the topology.
        mincutsets (list): A list of mincutsets to save.

    Notes:
        The CSV file is named "Mincutsets_<top>.csv"
    """
    _save_set_data(directory, top, mincutsets, "Mincutsets", "mincutsets")


# Evaluate the pathset and save it to a csv file
def save_pathsets(directory, top, pathsets):
    """
    Save pathsets to a CSV file.

    Args:
        directory (str): The directory where the topology is located.
        top (str): The name of the topology.
        pathsets (list): A list of pathsets to save.

    Notes:
        The CSV file is named "Pathsets_<top>.csv"
    """
    _save_set_data(directory, top, pathsets, "Pathsets", "pathsets")


# ==============================
# FileIO Functions
# ==============================


# ==============================
# Graphic Operation Functions
# ==============================


def to_link_graph(G, A_dict, edge_prob):
    """Convert a NetworkX graph to a link counted graph representation.

    If 0 - 1 is connected in G, then in Link_G, there will be a node (0,1), 0 - (0,1) - 1.
    We keep the original node numbers and add new nodes for each edge.
    The edge_mapping dictionary maps each original edge to its corresponding new node in Link_G.

    Args:
        G (nx.Graph): The input graph.
        A_dict (dict): A dictionary mapping nodes to their availability.
        edge_prob (dict): A dictionary mapping edges to their availability.

    Returns:
        Link_G (nx.Graph): The link counted graph representation.
        A_dict_new (dict): Updated availability dictionary including new link nodes.
    """
    # Convert the link counted graph
    link_G = G.copy()
    A_dict_new = A_dict.copy()

    for i, (u, v) in enumerate(G.edges()):
        new_node = len(G.nodes()) + i

        # add new node and connect it to u and v
        link_G.add_node(new_node)
        link_G.add_edge(u, new_node)
        link_G.add_edge(new_node, v)

        # remove old connection
        link_G.remove_edge(u, v)

        # update A_dict
        A_dict_new[new_node] = edge_prob.get((u, v), edge_prob.get((v, u), 0.0))

    return link_G, A_dict_new


# ==============================
# Graphic Operation Functions
# ==============================


# ==============================
# Expression Formatting Functions
# ==============================


def relabel_graph_A_dict(G, avail_dict):
    """Relabel the graph and availability dictionary

    Args:
        G (nx.Graph): The input graph.
        avail_dict (dict): The availability dictionary.

    Returns:
        G_relabel (nx.Graph): The relabeled graph.
        avail_dict_relabel (dict): The relabeled availability dictionary.
        dict: The mapping from old labels to new labels.
    """
    # Get the nodes of G
    nodes = list(G.nodes())
    # Create a mapping of the nodes to new labels
    relabel_mapping = {nodes[i]: i + 1 for i in range(len(nodes))}
    # Relabel the nodes of G
    G_relabel = nx.relabel_nodes(G, relabel_mapping)
    # Relabel the nodes in A_dict
    A_dic = {relabel_mapping[node]: value for node, value in avail_dict.items()}
    return G_relabel, A_dic, relabel_mapping


# relabel boolean expression back and convert the boolean expression to a mathematical expression
def relabel_boolexpr_to_str(bool_expr):
    expr = "["
    bool_expr_len = len(bool_expr)
    for num_list in bool_expr:
        expr += "["
        list_len = len(num_list)
        for num in num_list:
            if num == -1:
                expr += "0"
            elif num > 0:
                expr += str(num - 1)
            elif num < 0:
                expr += str(num + 1)
            list_len -= 1
            if list_len > 0:
                expr += " * "
        expr += "]"
        bool_expr_len -= 1
        if bool_expr_len > 0:
            expr += " + "
    expr += "]"
    return expr


def sdp_boolexpr_to_str(sdp_lst_lst):
    sdp_str = ""
    sdp_lst_lst_len = len(sdp_lst_lst)
    for sdp_lst in sdp_lst_lst:
        sdp_lst_len = len(sdp_lst)
        sdp_str += "["
        for sdp in sdp_lst:

            if sdp.isComplementary():
                sdp_str += "-["
            else:
                sdp_str += "["

            sdp_elem_len = len(sdp.getSet())
            for sdp_elem in sdp.getSet():
                if sdp_elem_len == 1:
                    sdp_str += f"{sdp_elem}"
                else:
                    sdp_str += f"{sdp_elem} * "
                sdp_elem_len -= 1
            sdp_str += "]"

            sdp_lst_len -= 1

            if sdp_lst_len > 0:
                sdp_str += " * "

        sdp_str += "]"
        sdp_lst_lst_len -= 1
        if sdp_lst_lst_len > 0:
            sdp_str += " + "

    return sdp_str.strip()


def sdp_boolexpr_length(sdp_lst_lst):
    expr_len = 0

    for sdp_lst in sdp_lst_lst:

        sdp_lst_len = len(sdp_lst)

        expr_len += sdp_lst_len

    return expr_len


# ==============================
# Expression Formatting Functions
# ==============================
