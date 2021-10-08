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
    m : int = None,
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
        output_name = f"{coupling_type}_{num_q}"
    elif coupling_type == "mesh":
        n = ceil(sqrt(num_q))
        coup_map = mesh(n = n)
        output_name = f"{coupling_type}_{n**2}"
    elif coupling_type == "all" or coupling_type == "alltoall":
        coup_map = alltoall(num_q = num_q)
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
        qudits = [x[0] for x in coup_map]
        qudits.extend([x[1] for x in coup_map])
        num_p = 0
        if len(qudits) > 0:
            num_p = max(qudits) + 1
        file_name = coupling_type_or_file
    else:
        if coupling_type_or_file == "mesh":
            n = ceil(sqrt(num_q))
            num_p = n ** 2
            file_name = "%s_%d" %(coupling_type_or_file, num_p)
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
    get_coupling_map("mesh", 4, True)
    get_coupling_map("mesh", 9, True)
    get_coupling_map("mesh", 16, True)
    get_coupling_map("mesh", 25, True)
    get_coupling_map("mesh", 36, True)
    get_coupling_map("mesh", 64, True)
    get_coupling_map("mesh", 121, True)
    get_coupling_map("mesh", 128, True)

    get_coupling_map("linear", 5, True)
    get_coupling_map("linear", 9, True)
    get_coupling_map("linear", 10, True)
    get_coupling_map("linear", 15, True)
    get_coupling_map("linear", 16, True)
    get_coupling_map("linear", 17, True)
    get_coupling_map("linear", 20, True)
    get_coupling_map("linear", 25, True)
    get_coupling_map("linear", 30, True)
    get_coupling_map("linear", 32, True)
    get_coupling_map("linear", 40, True)
    get_coupling_map("linear", 41, True)
    get_coupling_map("linear", 50, True)
    get_coupling_map("linear", 64, True)
    get_coupling_map("linear", 100, True)
    get_coupling_map("linear", 128, True)

    # Falcons
    # 16
    falcon16 = set([
        (6,7),
        (0,1), (1,4), (4,7), (7,10), (10,12), (12,15),
        (1,2), (12,13),
        (2,3), (13,14),
        (3,5), (5,8), (8,11), (11,14),
        (8,9),
    ])
    with open("coupling_maps/falcon_16", "wb") as f:
        dump(falcon16, f)

    # 27
    falcon27 = set([
        (6,7), (17,18),
        (0,1), (1,4), (4,7), (7,10), (10,12), (12,15), (15,18), (18,21), (21,23),
        (1,2), (12,13), (23,24),
        (2,3), (13,14), (24,25),
        (3,5), (5,8), (8,11), (11,14), (14,16), (16,19), (19,22), (22,25), (25,26),
        (8,9), (19,20),
    ])
    with open("coupling_maps/falcon_27", "wb") as f:
        dump(falcon27, f)

    # 65
    falcon65 = set([
        (0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,8), (8,9),
        (0,10), (4,11), (8,12),
        (10,13), (11,17), (12,21),
        (13,14), (14,15), (15,16), (16,17), (17,18), (18,19), (19,20), (20,21), (21,22), (22,23),
        (15,24), (19,25), (23,26),
        (24,29), (25,33), (26,37),
        (27,28), (28,29), (29,30), (30,31), (31,32), (32,33), (33,34), (34,35), (35,36), (36,37),
        (27,38), (31,39), (35,40),
        (38,41), (39,43), (40,49),
        (41,42), (42,43), (43,44), (44,45), (45,46), (46,47), (47,48), (48,49), (49,50), (50,51),
        (43,52), (47,53), (51,54),
        (52,56), (53,60), (54,64),
        (55,56), (56,57), (57,58), (58,59), (59,60), (60,61), (61,62), (62,63), (63,64),
    ])
    with open("coupling_maps/falcon_65", "wb") as f:
        dump(falcon65, f)

    # 113
    falcon113 = set([
        (0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,8), (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15), (15,16), (16,17),
        (0,18), (18,23), (4,19), (19,27), (8,20), (20,31), (12,21), (21,35), (16,22), (22,39),
        (23,24), (24,25), (25,26), (26,27), (27,28), (28,29), (29,30), (30,31), (31,32), (32,33), (33,34), (34,35), (35,36), (36,37), (37,38), (38,39), (39,40), (40,41),
        (25,42), (42,49), (29,43), (43,53), (33,44), (44,57), (37,45), (45,61), (41,46), (46,65),
        (47,48), (48,49), (49,50), (50,51), (51,52), (52,53), (53,54), (54,55), (55,56), (56,57), (57,58), (58,59), (59,60), (60,61), (61,62), (62,63), (63,64), (64,65),
        (47,66), (66,71), (51,67), (67,75), (55,68), (68,79), (59,69), (69,83), (63,70), (70,87),
        (71,72), (72,73), (73,74), (74,75), (75,76), (76,77), (77,78), (78,79), (79,80), (80,81), (81,82), (82,83), (83,84), (84,85), (85,86), (86,87), (87,88), (88,89),
        (73,90), (90,96), (77,91), (91,100), (81,92), (92,104), (85,93), (93,108), (89,94), (94,112),
        (95,96), (96,97), (97,98), (98,99), (99,100), (100,101), (101,102), (102,103), (103,104), (104,105), (105,106), (106,107), (107,108), (108,109), (109,110), (110,111), (111,112),
    ])
    with open("coupling_maps/falcon_113", "wb") as f:
        dump(falcon113, f)

    # 209
    falcon209 = set([
        (0,1), (1,2), (2,3), (3,4), (4,5), (5,6), (6,7), (7,8), (8,9), (9,10), (10,11), (11,12), (12,13), (13,14), (14,15), (15,16), (16,17),
        (0,18), (18,23), (4,19), (19,27), (8,20), (20,31), (12,21), (21,35), (16,22), (22,39),
        (23,24), (24,25), (25,26), (26,27), (27,28), (28,29), (29,30), (30,31), (31,32), (32,33), (33,34), (34,35), (35,36), (36,37), (37,38), (38,39), (39,40), (40,41),
        (25,42), (42,49), (29,43), (43,53), (33,44), (44,57), (37,45), (45,61), (41,46), (46,65),
        (47,48), (48,49), (49,50), (50,51), (51,52), (52,53), (53,54), (54,55), (55,56), (56,57), (57,58), (58,59), (59,60), (60,61), (61,62), (62,63), (63,64), (64,65),
        (47,66), (66,71), (51,67), (67,75), (55,68), (68,79), (59,69), (69,83), (63,70), (70,87),
        (71,72), (72,73), (73,74), (74,75), (75,76), (76,77), (77,78), (78,79), (79,80), (80,81), (81,82), (82,83), (83,84), (84,85), (85,86), (86,87), (87,88), (88,89),
        (73,90), (90,97), (77,91), (91,101), (81,92), (92,115), (85,93), (93,109), (89,94), (94,113),
        (95,96), (96,97), (97,98), (98,99), (99,100), (100,101), (101,102), (102,103), (103,104), (104,105), (105,106), (106,107), (107,108), (108,109), (109,110), (110,111), (111,112), (112,113),
        (95,114), (114,119), (99,115), (115,123), (103,116), (116,127), (107,117), (117,131), (111,118), (118,135),
        (119,120), (120,121), (121,122), (122,123), (123,124), (124,125), (125,126), (126,127), (127,128), (128,129), (129,130), (130,131), (131,132), (132,133), (133,134), (134,135), (135,136), (136,137),
        (121,138), (138,145), (125,139), (139,149), (129,140), (140,153), (133,141), (141,157), (137,142), (142,161),
        (143,144), (144,145), (145,146), (146,147), (147,148), (148,149), (149,150), (150,151), (151,152), (152,153), (153,154), (154,155), (155,156), (156,157), (157,158), (158,159), (159,160), (160,161),
        (143,162), (162,167), (147,163), (163,171), (151,164), (164,175), (155,165), (165,179), (159,166), (166,183),
        (167,168), (168,169), (169,170), (170,171), (171,172), (172,173), (173,174), (174,175), (175,176), (176,177), (177,178), (178,179), (179,180), (180,181), (181,182), (182,183), (183,184), (184,185),
        (169,186), (186,192), (173,187), (187,196), (177,188), (188,200), (181,189), (189,204), (185,190), (190,208),
        (191,192), (192,193), (193,194), (194,195), (195,196), (196,197), (197,198), (198,199), (199,200), (200,201), (201,202), (202,203), (203,204), (204,205), (205,206), (206,207), (207,208),
    ])
    with open("coupling_maps/falcon_209", "wb") as f:
        dump(falcon209, f)