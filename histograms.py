"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
import os
import pickle
from posix import listdir

from networkx import Graph
import argparse
import matplotlib.pyplot as plot
import re
import statistics



def cnot_histograms(
    partition_dir : str,
) -> None:
    # TODO: Implement support for non-qasm checkpointing
    block_files = sorted(listdir(partition_dir))
    block_names = [x.split("/")[-1].split(".")[0] for x in block_files]
    block_names.remove("structure")

    # Get CNOT counts for each block
    cnots_list = []
    for block in block_names:
        # Get CNOT count
        cnots = 0
        with open(f"{partition_dir}/{block}.qasm", "r") as qasmfile:
            for line in qasmfile:
                if re.match("cx", line):
                    cnots += 1
        cnots_list.append(cnots)
    
    # Create a histogram
    cnots_set = set(cnots_list)
    data_min = min(cnots_set)
    data_max = max(cnots_set)
    
    counts = [cnots_list.count(x) for x in cnots_set]
    upper = max(counts) + 1
    plot.yticks(range(upper + 1))

    plot.xlabel("Block CNOT Count")
    bins = range(data_min, data_max+2)
    plot.xticks(bins)
    plot.hist(cnots_list, align="left", bins=bins, rwidth=0.8)

    name = partition_dir.split("/")[-1].split(".")[0]
    plot.title(f"Histogram of CNOT counts in blocks of \n{name}")

    name = f"figures/{name}-cnots.png"
    plot.savefig(name)
    plot.clf()


def volume_histograms(
    subtopology_dir : str,
) -> None:
    # Get internal op volumes for each block
    with open(f"{subtopology_dir}/summary.txt", "r") as stats:
        volume_list = []
        for line in stats:
            if re.match("    direct volume", line):
                dirvol = int(re.search("\d+", line)[0])
            elif re.match("    indirect volume", line):
                indirvol = int(re.search("\d+", line)[0])
                vol = dirvol + indirvol
                volume_list.append(vol)

    # Create a histogram
    volume_set = set(volume_list)
    data_min = min(volume_set)
    data_max = max(volume_set)
    
    counts = [volume_list.count(x) for x in volume_set]
    upper = max(counts) + 1
    plot.yticks(range(upper + 1))

    plot.xlabel("Block Internal Volume")
    #bins = range(data_min, data_max+2)
    bins = []
    for bin in volume_set:
        bins.append(bin-1)
        bins.append(bin)
        bins.append(bin+1)
    bins = sorted(bins)
    plot.xticks(sorted(volume_set))
    plot.hist(volume_list, align="left", bins=bins, rwidth=0.8)

    name = subtopology_dir.split("/")[-1].split(".")[0]
    suffix = name.split('_')[-1]
    name = name.split(f"_{suffix}")[0]
    plot.title(f"Histogram of Internal Operation Volume in blocks of \n{name}")

    name = f"figures/{name}-volume.png"
    plot.savefig(name)
    plot.clf()


def block_stats(partition_dir : str):
    # TODO: Implement support for non-qasm checkpointing
    block_files = sorted(listdir(partition_dir))
    block_names = [x.split("/")[-1].split(".")[0] for x in block_files]
    block_names.remove("structure")

    # Get CNOT counts for each block
    cnots_list = []
    for block in block_names:
        # Get CNOT count
        cnots = 0
        with open(f"{partition_dir}/{block}.qasm", "r") as qasmfile:
            for line in qasmfile:
                if re.match("cx", line):
                    cnots += 1
        cnots_list.append(cnots)
    
    mean = statistics.mean(cnots_list)
    median = statistics.median(cnots_list)
    std = statistics.stdev(cnots_list)
    small_thresh = mean - std
    large_thresh = mean + std

    small_count  = 0
    medium_count = 0
    large_count  = 0
    for block in cnots_list:
        if block < small_thresh:
            small_count += 1
        elif block > large_thresh:
            large_count += 1
        else:
            medium_count += 1

    print(f"Mean   : {mean}")
    print(f"stdev  : {std}")
    print(f"Median : {median}")
    print(f"Small coverage  : {small_count/len(cnots_list)*100}%")
    print(f"Medium coverage : {medium_count/len(cnots_list)*100}%")
    print(f"Large coverage  : {large_count/len(cnots_list)*100}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", type=str, 
        help="blocks to plot")
    args = parser.parse_args()

    name = args.project_name.split("/")[-1]
    kind = args.project_name.split("/")[0]

    if kind == "block_files":
        cnot_histograms(f"block_files/{name}")
        block_stats(f"block_files/{name}")
    else:
        volume_histograms(f"subtopology_files/{name}")
    

