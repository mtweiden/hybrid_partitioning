"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
import os
import pickle
from posix import listdir
from typing import Any, Sequence
from pickle import load, dump
from weighted_topology import get_unpartitionable_edges
from networkx import Graph
import networkx as nx
import argparse
import matplotlib.pyplot as plot
import re


# TODO: Want to sort edges into 4 categories:
#   1) Unused physical gate in block
#   2) Used physical gate in block
#   3) Non-physical partitionable gate (hard because not in hybrid topology)
#   4) Unpartitionable gate

def draw_subtopology(
    hybrid_topology : Graph,
    physical_topology : Graph,
    qudit_group : Sequence[int],
    save_path : str,
) -> None:    
    logical_edges = [(u,v) for (u,v) in hybrid_topology.edges if (u,v) 
        not in physical_topology.edges and (v,u) not in physical_topology.edges]
    subgraph = hybrid_topology.subgraph(qudit_group)
    colored_subgraph = Graph()
    colored_subgraph.add_nodes_from(qudit_group)
    all_edges = subgraph.edges
    for edge in all_edges:
        a = edge[0]
        b = edge[1]
        if (a,b) in logical_edges:
            weight = hybrid_topology[a][b]["weight"]
            colored_subgraph.add_edge(a,b,weight=weight,color='r',label=weight)
        elif (b,a) in logical_edges:
            weight = hybrid_topology[a][b]["weight"]
            colored_subgraph.add_edge(a,b,weight=weight,color='r',label=weight)
        else:
            weight = hybrid_topology[a][b]["weight"]
            colored_subgraph.add_edge(a,b,weight=weight,color='b',label=weight)

    pos = nx.circular_layout(colored_subgraph)
    colors = [colored_subgraph[u][v]["color"] for u,v in all_edges]
    weights = [colored_subgraph[u][v]["weight"] for u,v in all_edges]
    labels = {(u,v):colored_subgraph[u][v]["label"] for u,v in all_edges}
    widths = [3 if weight > 1 else 5 for weight in weights]
    label_dict = {q:q for q in qudit_group}
    # Edge presence: usable operation for synthesis
    # Edge labels: operation cost_function value
    # Edge color: blue - partitionable; red - unpartitionable
    nx.draw_networkx_edge_labels(colored_subgraph, pos, edge_labels=labels)
    nx.draw(colored_subgraph, pos, edge_color=colors, width=widths, labels=label_dict)
    plot.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hybrid_topology", type=str, 
		help="subtopology to draw")
    args = parser.parse_args()

    graph_files = sorted(listdir("subtopology_files/" + args.hybrid_topology))
    with open("block_files/" + args.hybrid_topology + "/structure.pickle", 
        "rb") as f:
        structure = pickle.load(f)

    coup = re.findall("mesh_\d+_\d+", args.hybrid_topology)[0]
    num_q_sqrt = int(re.findall("\d+", coup)[0])
    with open(f"coupling_maps/mesh_{num_q_sqrt}_{num_q_sqrt}", "rb") as f:
        physical = pickle.load(f)
    physical_topology = Graph()
    physical_topology.add_weighted_edges_from([(u,v,1) for u,v in physical])

    save_dir = f"graph_drawings/{args.hybrid_topology}"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    for block_num in range(len(graph_files)):
        with open(f"subtopology_files/{args.hybrid_topology}/" 
            + graph_files[block_num], "rb") as f:
            hybrid_edge_set = list(pickle.load(f))
        hybrid_topology = Graph()
        hybrid_topology.add_weighted_edges_from(hybrid_edge_set)
        draw_subtopology(hybrid_topology, physical_topology, 
            structure[block_num], f"{save_dir}/block_{block_num}")
       