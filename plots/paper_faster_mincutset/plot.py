import pandas as pd
import matplotlib.pyplot as plt
import ast
import math
import numpy as np
import matplotlib.patches as mpatches

FIG_SIZE = (9, 6)
FONT_SIZE = 15
LABEL_SIZE = 15
ROTATION = 30


def plot_1(plot_name, topologies=None):
    # Read the CSV file
    df_v2 = pd.read_csv("results_v2/benchmark_summary.csv", index_col="Topology")
    df_v3 = pd.read_csv("results_v3/benchmark_summary.csv", index_col="Topology")

    # Sort the topos with the number of nodes
    topologies = sorted(topologies, key=lambda x: df_v2.loc[x, "Number of Pairs"])

    # Read the time for each topology
    time_faster_mcs_v2 = []
    time_faster_mcs_v3 = []
    time_pathset = []
    for topo in topologies:
        time_faster_mcs_v2.append(df_v2.loc[topo, f"Total Time Faster MCS v2 (s)"])
        time_faster_mcs_v3.append(df_v3.loc[topo, f"Total Time Faster MCS v3 (s)"])
        time_pathset.append((df_v2.loc[topo, f"Total Time MPS (s)"] + df_v3.loc[topo, f"Total Time MPS (s)"]) / 2)

    # Draw the plot
    fig, ax1 = plt.subplots(figsize=FIG_SIZE)
    width = 0.3  # Bar width for each series

    # x positions for grouped bars
    x = np.arange(len(topologies))
    ax1.bar(
        x - width,
        time_pathset,
        width,
        label="Finding MPSs",
        color="#08519c",
    )
    ax1.bar(
        x,
        time_faster_mcs_v3,
        width,
        label="Finding MCSs from MPSs (Shannon Expansion)",
        color="#B2182B",
    )
    ax1.bar(
        x + width,
        time_faster_mcs_v2,
        width,
        label="Finding MCSs from MPSs (Faster MCS v2)",
        color="#008080",
    )

    # Set the x-ticks and labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(topologies, fontsize=FONT_SIZE - 2, rotation=ROTATION)
    ax1.tick_params(axis="y", labelsize=LABEL_SIZE)
    ax1.set_ylabel("Simulation time (seconds)", fontsize=FONT_SIZE + 3)
    # ax1.set_ylim(10 ** (-1), 10**4)
    ax1.set_yscale("log")
    plt.yticks(fontsize=FONT_SIZE)

    # Merge legends
    handles, labels = ax1.get_legend_handles_labels()

    ax1.legend(
        handles,
        labels,
        loc="upper left",
        fontsize=15,
    )

    # Save the plot
    plt.tight_layout()
    plt.savefig(f"plot/{plot_name}.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_2(plot_name, topologies=None):
    # Read the CSV file
    df_v2 = pd.read_csv("results_v2/benchmark_summary.csv", index_col="Topology")
    df_old = pd.read_csv("results_v2/Summary_Series.csv", index_col="Topology")

    # Sort the topos with the number of nodes
    topologies = sorted(topologies, key=lambda x: df_v2.loc[x, "Number of Pairs"])
    
    # Read the time for each topology
    time_faster_mcs_v2 = []
    time_mcs = []
    for topo in topologies:
        time_faster_mcs_v2.append(df_v2.loc[topo, f"Total Time Faster MCS v2 (s)"] + df_v2.loc[topo, f"Total Time MPS (s)"])
        time_mcs.append(df_old.loc[topo, f"Optimized MCS Time (Second)"])

    # Draw the plot
    fig, ax1 = plt.subplots(figsize=FIG_SIZE)
    width = 0.4  # Bar width for each series

    # x positions for grouped bars
    x = np.arange(len(topologies))
    ax1.bar(
        x - width / 2,
        time_mcs,
        width,
        label="Finding MCSs",
        color="#4E79A7",
    )
    ax1.bar(
        x + width / 2,
        time_faster_mcs_v2,
        width,
        label="Finding MCSs (Improved)",
        color="#F28E2B",
    )

    # Set the x-ticks and labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(topologies, fontsize=FONT_SIZE - 2, rotation=ROTATION)
    ax1.tick_params(axis="y", labelsize=LABEL_SIZE)
    ax1.set_ylabel("Simulation time (seconds)", fontsize=FONT_SIZE + 3)
    # ax1.set_ylim(10 ** (-1), 10**4)
    ax1.set_yscale("log")
    plt.yticks(fontsize=FONT_SIZE)

    # Merge legends
    handles, labels = ax1.get_legend_handles_labels()

    ax1.legend(
        handles,
        labels,
        loc="upper left",
        fontsize=15,
    )

    # Save the plot
    plt.tight_layout()
    plt.savefig(f"plot/{plot_name}.png", dpi=300, bbox_inches="tight")
    plt.close()

topos_1_1 = [
    "Abilene",
    "polska",
    "HiberniaUk",
    "Germany_17",
    "Spain",
    "Austria_24",
    "Nobel_EU",
    "Sweden",
    "USA_26",
    "Norway",
]

topos_1_2 = ["india35", "jonas-us-ca", "pioro40"]

topos_2 = [
    "Abilene",
    "polska",
    "HiberniaUk",
    "Germany_17",
    "Spain",
    "Austria_24",
    "Nobel_EU",
    # "Sweden",
    # "USA_26",
    # "Norway",
    # "india35",
    # "jonas-us-ca",
    # "pioro40"
]

plot_1("plot1_1", topos_1_1)
plot_1("plot1_2", topos_1_2)
plot_2("plot2", topos_2)