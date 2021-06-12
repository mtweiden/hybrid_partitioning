"""
Takes a circuit (qasm file) and a physical topology and produces a hybrid 
logical-physical topology.
"""

from __future__ import annotations
from typing import Sequence
from re import S, match, findall
from pickle import load, dump
from networkx import Graph, shortest_path_length

def check_multi(qasm_line):
    """
    Determine if a line of QASM code is a multi-qubit interaction. If it is, 
    return a tuple of ints (control, target).
    """
    if bool(match("cx", qasm_line)):
        # line is in the form - cx q[<control>], q[<target>];
        q = findall('\d+', qasm_line)
        return (int(q[0]), int(q[1]))
    else:
        return None


def num_unimplementable_gates(
    circuit_file  : str, 
    coupling_file : str,
    block_size : int,
) -> int:
    """
	Number of unimplementable gates in
    """
    # Get the logical connectivity graph
    logical_edge_set = set()
    with open(qasm_file, 'r') as f:
        for qasm_line in f:
            if (edge := check_multi(qasm_line)) is not None:
                logical_edge_set.add(edge)

    # Get the physical topology
    with open(coupling_file, 'rb') as f:
        physical_edge_set = load(f)
 
    # Convert the physical topology to a networkx graph
    graph = Graph()
    graph.add_edges_from(list(physical_edge_set))

	unimplementable_gates = 0

    for logical_edge in logical_edge_set:
        a = logical_edge[0]
        b = logical_edge[1]
        # NOTE: Should logical edges be reused?
        if shortest_path_length(hybrid_graph, a, b) > block_size - 1:
			unimplementable_gates += 1

	return unimplementable_gates
