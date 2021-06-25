"""
Functions to generate qubit coupling maps
"""
from __future__ import annotations
from typing import Sequence
from math import sqrt, ceil
from pickle import dump, load
from os.path import exists
from re import match, findall

def mesh(
    n : int,
    m : int = None
) -> set[tuple[int]]:
    """
    Generate a 2D mesh coupling map.

    Args:
        n (int): If only n is provided, then this is the side length of a square
            grid. Otherwise it is the number of rows in the mesh.

        m (int|None): If m is provided, it is the number of columns in the mesh.

    Returns:
        coupling_map (set[tuple[int]]): The coupling map corresponding to the 
            2D nearest neighbor mesh that is nxn or nxm in dimensions.
    """
    cols = n if m is None else m
    rows = n

    edges = set()
    # Horizontals
    for i in range(rows):
        for j in range(cols-1):
            edges.add((i*cols + j, i*cols + j+1))
    # Verticals
    for i in range(rows-1):
        for j in range(cols):
            edges.add((i*cols + j, i*cols + j+cols))
    return edges

def alltoall(num_q :int ) -> set[tuple[int]]:
    """
    Generate an all to all coupling map.

    Args:
        num_q (int): Number of vertices in the graph.

    Returns:
        coupling_map (set[tuple[int]]): All to all couplings.
    """
    edges = set()
    for i in range(num_q):
        for j in range(num_q):
            if i != j:
                edges.add((i,j))
    return edges

def linear(num_q : int) -> set[tuple[int]]:
    """
    Generate a linear coupling map.

    Args:
        num_q (int): Number of vertices in the graph.

    Returns:
        coupling_map (set[tuple[int]]): Linear couplings
    """
    return mesh(num_q, 1)


def make_coupling_map(
    coupling_type : str, 
    num_q : int
) -> Sequence[Sequence[int]] | None:
    if coupling_type == "linear":
        coup_map = linear(num_q = num_q)
        output_name = "%s_%d" %(coupling_type, num_q)
    elif coupling_type == "mesh":
        n = ceil(sqrt(num_q))
        coup_map = mesh(n = n)
        output_name = "%s_%d_%d" %(coupling_type, n, n)
    elif coupling_type == "all" or coupling_type == "alltoall":
        coup_map = alltoall(num_q = num_q)
        output_name = "%s_%d" %(coupling_type, num_q)
    else:
        # If there's no such coupling map type, use all to all
        print("No such coupling map type (%s), using all-to-all" 
            %(coupling_type))
        coup_map = alltoall(num_q = num_q)
        output_name = "%s_%d" %(coupling_type, num_q)
    
    with open('coupling_maps/%s'%(output_name), 'wb') as f:
        dump(coup_map, f)
    
    return coup_map


def get_coupling_map(
    coupling_type_or_file : str, 
    num_q : int = -1,
    make_coupling_map_flag : bool = False
) -> tuple[int, Sequence[Sequence[int]]] | None:
    # If the file name was provided, return that file
    if exists(coupling_type_or_file):
        with open(coupling_type_or_file, 'rb') as f:
            coup_map = load(f)
        num_p = max(max(coup_map)) + 1
        file_name = coupling_type_or_file
    else:
        if coupling_type_or_file == "mesh":
            n = ceil(sqrt(num_q))
            num_p = n ** 2
            file_name = "%s_%d_%d" %(coupling_type_or_file, n, n)
        else:
            num_p = num_q
            file_name = "%s_%d" %(coupling_type_or_file, num_q)
        file_name = 'coupling_maps/%s'%(file_name) 

    if exists(file_name):
        with open(file_name, 'rb') as f:
            coup_map = load(f)
    elif make_coupling_map_flag:
        coup_map = make_coupling_map(coupling_type_or_file, num_q)
    else:
        print("No such coupling map type (%s)" %(coupling_type_or_file))
        return None
    
    return (num_p, coup_map)

if __name__ == "__main__":
	get_coupling_map("mesh", 2, True)
	get_coupling_map("mesh", 4, True)
	get_coupling_map("mesh", 8, True)
	get_coupling_map("mesh", 16, True)
	get_coupling_map("mesh", 32, True)
	get_coupling_map("mesh", 64, True)
	get_coupling_map("mesh", 128, True)
	get_coupling_map("alltoall", 5, True)

