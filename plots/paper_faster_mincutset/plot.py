import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import ast
import math
import numpy as np
import matplotlib.patches as mpatches
from pyrbd_utils import read_graph

FIG_SIZE = (9, 6)
FONT_SIZE = 15
LABEL_SIZE = 15
ROTATION = 30


def plot_1(plot_name, topologies=None):
    cnf_times = []
    combination_times = []
    minimalpaths_times = []
    for topo in topologies:
        # Read the CSV file
        cnf = pd.read_csv(f"benchmark/mincutsets/results/cnf/{topo}_MCS_cnf.csv")
        combination = pd.read_csv(f"benchmark/mincutsets/results/combination_matrix/{topo}_MCS_combination_matrix.csv")
        minimalpaths = pd.read_csv(f"benchmark/pathsets/results/minimalpaths/{topo}_Pathsets_minimalpaths.csv")
        # Sum the time columns
        cnf_time = cnf["cnf_time (second)"].sum()
        combination_time = combination["combination_matrix_time (second)"].sum()
        minimalpaths_time = minimalpaths["minimalpaths_time (second)"].sum()
        # Append to lists
        cnf_times.append(cnf_time - minimalpaths_time)
        combination_times.append(combination_time)
        minimalpaths_times.append(minimalpaths_time)

    print("CNF times:", cnf_times)
    print("Combination times:", combination_times)
    print("Minimal paths times:", minimalpaths_times)

    # Draw the plot
    fig, ax1 = plt.subplots(figsize=FIG_SIZE)
    width = 0.35  # Bar width for each series

    # x positions for grouped bars
    x = np.arange(len(topologies))
    ax1.bar(
        x - width/2,
        minimalpaths_times,
        width,
        label="Finding MPSs",
        color="#08519c",
    )
    ax1.bar(
        x - width/2,
        cnf_times,
        width,
        label="Finding MCSs from MPSs (Improved)",
        color="#B2182B",
        bottom=minimalpaths_times,
    )
    ax1.bar(
        x + width/2,
        combination_times,
        width,
        label="Finding MCSs (Old)",
        color="#D57E26",
    )

    # Set the x-ticks and labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(topologies, fontsize=FONT_SIZE - 2, rotation=ROTATION)
    ax1.tick_params(axis="y", labelsize=LABEL_SIZE)
    ax1.set_ylabel("Simulation time (seconds)", fontsize=FONT_SIZE + 3)
    ax1.set_ylim(10 ** (-3), 10**5)
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
    plt.savefig(f"plots/paper_faster_mincutset/{plot_name}.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_2(plot_name, topologies=None):
    cnf_time = []
    shannon_time = []
    for topo in topologies:
        # Read the CSV file
        cnf = pd.read_csv(f"benchmark/mincutsets/results/cnf/{topo}_MCS_cnf.csv")
        shannon = pd.read_csv(f"benchmark/mincutsets/results/shannon/{topo}_MCS_shannon.csv")
        # Sum the time columns
        cnf_time.append(cnf["cnf_time (second)"].sum())
        shannon_time.append(shannon["shannon_time (second)"].sum())
    
    # Draw the plot
    fig, ax1 = plt.subplots(figsize=FIG_SIZE)
    width = 0.4  # Bar width for each series

    # x positions for grouped bars
    x = np.arange(len(topologies))
    ax1.bar(
        x - width / 2,
        cnf_time,
        width,
        label="Finding MCSs",
        color="#4E79A7",
    )
    ax1.bar(
        x + width / 2,
        shannon_time,
        width,
        label="Finding MCSs (Shannon Expansion)",
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
    plt.savefig(f"plots/paper_faster_mincutset/{plot_name}.png", dpi=300, bbox_inches="tight")
    plt.close()

# plot only mps time
def plot_3(plot_name, topologies=None):
    mps_time = []
    for topo in topologies:
        # G, _, _ = read_graph(f"topologies/{topo}", topo)
        # print(f"Processing topology: {topo} with {len(G.nodes())} nodes and {len(G.edges())} edges")
        df = pd.read_csv(f"benchmark/pathsets/results/minimalpaths/{topo}_Pathsets_minimalpaths.csv")
        # add the sum of "minimalpaths_time (second)" to mps_time
        total_time = df["minimalpaths_time (second)"].sum()
        mps_time.append(total_time)

    # Draw the plot
    fig, ax1 = plt.subplots(figsize=FIG_SIZE)
    width = 0.5  # Bar width for each series
    
    # x positions for grouped bars
    x = np.arange(len(topologies))
    
    ax1.bar(
        x,
        mps_time,
        width,
        label="Finding MPSs",
        color="#4E79A7",
    )
    
    # Set the x-ticks and labels
    ax1.set_xticks(x)
    # ax1.set_xticklabels(topologies, fontsize=FONT_SIZE - 2, rotation=ROTATION)
    labels = ax1.set_xticklabels(
        topologies, fontsize=FONT_SIZE - 2, rotation=ROTATION
    )

    # Custom adjustment for Germany_17
    for label in labels:
        if label.get_text() == "Germany_17":
            # Shift left by 10 points
            offset = mtransforms.ScaledTranslation(-5 / 72, 0, fig.dpi_scale_trans)
            label.set_transform(label.get_transform() + offset)
    ax1.tick_params(axis="y", labelsize=LABEL_SIZE)
    ax1.set_ylabel("Simulation time (seconds)", fontsize=FONT_SIZE + 3)
    # ax1.set_ylim(10 ** (-1), 10**4)
    ax1.set_yscale("log")
    plt.yticks(fontsize=FONT_SIZE)
    ax1.legend(
        loc="upper left",
        fontsize=15,
    )
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(f"plots/paper_faster_mincutset/{plot_name}.png", dpi=300, bbox_inches="tight")
    plt.close()



topos_1= [
    "Abilene",
    "polska",
    "HiberniaUk",
    "Germany_17",
    "Spain",
    "Austria_24",
    "Sweden",
    "USA_26",
    "Norway",
    "Nobel_EU",
    # "india35",
    # "jonas-us-ca",
    # "pioro40",
    # "Germany_50",
    # "zib54",
]

topos_2_1= [
    "Abilene",
    "polska",
    "HiberniaUk",
    "Germany_17",
    "Spain",
    "Austria_24",
    "Sweden",
    "USA_26",
    "Norway",
    "Nobel_EU",
    # "india35",
    # "jonas-us-ca",
    # "pioro40",
    # "Germany_50",
    # "zib54",
]

topos_2_2= [
    "india35",
    "jonas-us-ca",
    "pioro40"
]

topos_3= [
    "Abilene",
    "polska",
    "HiberniaUk",
    "Germany_17",
    "Spain",
    "Austria_24",
    "Sweden",
    "USA_26",
    "Norway",
    "Nobel_EU",
    "india35",
    "jonas-us-ca",
    "pioro40",
    # "Germany_50",
    # "zib54",
]

plot_1("plot_1", topologies=topos_1)
plot_2("plot_2_1", topologies=topos_2_1)
plot_2("plot_2_2", topologies=topos_2_2)
plot_3("plot_3", topologies=topos_3)

