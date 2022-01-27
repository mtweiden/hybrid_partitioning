from __future__ import annotations
from os.path import exists
from os import mkdir, listdir, stat
import argparse
from post_synth import replace_blocks

from topology import run_stats_dict
from stas import setup_args, save_dict, get_saved_dict

from util import setup_options

import pandas as pd
import numpy as np
import json
import os
import statistics 

import pickle

import networkx as nx
import matplotlib.pyplot as plt

# Enable logging
import logging
logging.getLogger('bqskit').setLevel(logging.INFO)


def create_dag_from_pickle_list(p_list):
    num_partitions = len(p_list)
    G = nx.DiGraph()
    for i in range(num_partitions):
        for j in range(i + 1, num_partitions):
            if len(p_list[i].intersection(p_list[j])) > 0:
                G.add_edge(i,j)

    # Remove redundant edges
    G1 = nx.transitive_reduction(G)

    return G1

def get_adjacency_measure_in_dag(G, p_list):
    total_similarity = []
    for node in G.nodes:
        for neighbor in G.successors(node):
            total_similarity.append(len(p_list[node].intersection(p_list[neighbor])))

    
    return statistics.mean(total_similarity), statistics.stdev(total_similarity)


if __name__ == '__main__':
    args =  setup_args(need_qasm=False)

    block_dir = "block_files"

    qasms = listdir(block_dir)
    rows = []

    for qasm in qasms:

        if "linear" in qasm or "falcon" in qasm:
            # Don't need to repeat calcs
            continue

        if "filter" not in qasm:
            continue

        full_dir = os.path.join(block_dir, qasm)

        try:
            pickle_file = os.path.join(full_dir, "structure.pickle")

            print(pickle_file)

            with open(pickle_file, 'rb') as f:   
                p = pickle.load(f)

            # Turn into list of sets
            p = [set(x) for x in p]

            block_size = len(max(p, key=len))

            dag = create_dag_from_pickle_list(p)

            adj_measure, std_dev = get_adjacency_measure_in_dag(dag, p)

            data = {"name": qasm, "blocksize": block_size, "Avg. qubits shared between adjacent partitions": adj_measure, "Std. Deviation": std_dev}

            rows.append(data)
        except:
            data = {"name": qasm, "blocksize": 4, "Avg. qubits shared between adjacent partitions": 0, "Std. Deviation": 0}

            rows.append(data)

    full_data = pd.DataFrame.from_dict(rows, orient='columns')

    full_data.to_csv("out_adjacency.csv")
