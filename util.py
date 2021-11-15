from __future__ import annotations
from posix import listdir
from re import S, match
from typing import Any, Sequence
import pickle
import argparse
from bqskit.ir.operation import Operation

from qiskit import circuit

from networkx.classes.graph import Graph
from math import sqrt, ceil
from bqskit import Circuit
from bqskit.ir.lang.qasm2.qasm2	import OPENQASM2Language
from bqskit.passes.util.converttocnot import ToCNOTPass

from mapping import find_num_qudits

def load_block_circuit(
    block_path : str,
    options : dict[str, Any]
) -> Circuit:
    if options['checkpoint_as_qasm']:
        with open(block_path, "r") as f:
            return OPENQASM2Language().decode(f.read())
    else:
        with open(block_path, 'rb') as f:
            return pickle.load(f)

def save_block_circuit(
    block_path : str,
    block_circuit : Circuit,
    options : dict[str, Any]
) -> None:
    if options['checkpoint_as_qasm']:
        qasm = OPENQASM2Language().encode(block_circuit)
        with open(block_path, "w") as f:
            f.write(qasm)
    else:
        with open(block_path, 'wb') as f:
            pickle.dump(block_circuit, f)


def load_block_topology(
    block_path : str,
) -> Graph | Sequence[tuple[int,int]]:
    with open(block_path, "rb") as f:
        return pickle.load(f)


def save_block_topology(
    subtopology: Graph,
    block_path : str,
) -> None:
    with open(block_path, 'wb') as f:
        pickle.dump(subtopology, f)


def save_circuit_structure(
    partition_directory: str,
    structure_list : Sequence[Sequence[int]],
) -> None:
    with open(f"{partition_directory}/structure.pickle", "wb") as f:
        pickle.dump(structure_list, f)


def load_circuit_structure(
    partition_directory : str,
) -> Sequence[Sequence[int]]:
    with open(f"{partition_directory}/structure.pickle", "rb") as f:
        return pickle.load(f)


def setup_options(
    qasm_file : str, 
    args : argparse.Namespace
) -> dict[str,Any]:

    # Select coupling map
    valid_map_types = ["mesh", "linear", "falcon"]
    if not args.map_type in valid_map_types:
        raise RuntimeError(
            f"{args.map_type} is not a valid coupling map type."
        )
    num_q = find_num_qudits(qasm_file)
    if args.map_type == "mesh":
        num_p_sqrt = ceil(sqrt(num_q))
        num_p = num_p_sqrt ** 2
        coupling_map = (
            f"{args.map_type}_{num_p}"
        )
    elif args.map_type == "linear":
        coupling_map = (
            f"{args.map_type}_{num_q}"
        )
        num_p = num_q
    else: #elif args.map_type == "falcon"
        #sizes = [16, 27, 65]
        if num_q <= 16:
            coupling_map = f"falcon_16"
            num_p = 16
        elif num_q <= 27:
            coupling_map = f"falcon_27"
            num_p = 27
        elif num_q <= 65:
            coupling_map = f"falcon_65"
            num_p = 65
        elif num_q <= 113:
            coupling_map = f"falcon_113"
            num_p = 113
        else:
            raise RuntimeError(
                f"{num_q} qubits is too large for the falcon map type."
            )

    # Select partitioner
    valid_partitioners = ["scan", "greedy", "quick", "custom"]
    if not args.partitioner in valid_partitioners:
        raise RuntimeError(
            f"{args.partitioner} is not a valid partitioner type."
        )
    partitioner = args.partitioner

    options = {
        "blocksize"	 : args.blocksize,
        "coupling_map"   : f"coupling_maps/{coupling_map}",
        "topology" : args.map_type,
        "num_p" : num_p,
        "partitioner" : partitioner,
        "checkpoint_as_qasm" : True,
        "direct_ops" : 0,
        "indirect_ops" : 0,
        "external_ops" : 0,
        "direct_volume" : 0,
        "indirect_volume" : 0,
        "external_volume" : 0,
        "max_block_length" : 0,
        "min_block_length" : 0,
        "estimated_cnots" : 0,
        "total_volume" : 0,
        "router" : args.router,
        "original_qasm_file" : qasm_file,
    }

    target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]

    target_name += "_" + coupling_map
    target_name += f"_blocksize_{args.blocksize}"

    options["layout_qasm_file"] = "layout_qasm/" + target_name + ".qasm"

    target_name += f"_{partitioner}"

    options["partition_dir"] = "block_files/" + target_name
    options["save_part_name"] = target_name

    suffix = "_kernel"

    target_name += suffix
    options["target_name"] = target_name
    options["synthesized_qasm_file"] = "synthesized_qasm/" + target_name + ".qasm"
    options["resynthesized_qasm_file"] = "resynthesized_qasm/" + target_name + ".qasm"
    options["relayout_qasm_file"] = "relayout_qasm/" + target_name + ".qasm"
    options["mapped_qasm_file"] = "mapped_qasm/" + target_name + f"_{args.router}" + ".qasm"
    options["remapped_qasm_file"] = "mapped_qasm/" + f"{target_name}_{args.router}_remapped.qasm"
    options["synthesis_dir"] = "synthesis_files/" + target_name
    options["resynthesis_dir"] = "synthesis_files/" + target_name + "_resynth"
    options["nosynth_dir"] = options["synthesis_dir"] + f"_{args.router}_nosynth"
    options["subtopology_dir"] = "subtopology_files/" + target_name
    options["kernel_dir"] = f"kernels/{coupling_map}_blocksize_{args.blocksize}"

    return options


def get_summary(
    options : dict[str, Any], 
    block_files : Sequence[str],
    post_flag : bool = False,
) -> str:
    total_ops = sum([options["direct_ops"], options["indirect_ops"], 
        options["external_ops"]])
    string = (
        "\nSummary:\n"
        f"Number of blocks: {len(block_files)}\n"
        f"Mean block size (cnots): {total_ops/len(block_files)}\n\n"
        f"Total internal direct operations: {options['direct_ops']}\n"
        f"Total internal indirect operations: {options['indirect_ops']}\n"
        f"Total external operations: {options['external_ops']}\n"
    )
    if post_flag:
        string += get_mapping_results(options)
        string += get_original_count(options)
    print(string)
    return string

def get_mapping_results(
    options : dict[str, Any],
) -> dict:
    path = options["mapped_qasm_file"]
    cnots = 0
    swaps = 0
    with open(path, "r") as qasmfile:
        for line in qasmfile:
            if match("cx", line):
                cnots += 1
            elif match("swap", line):
                swaps += 1
    with open(path, "r") as f:
        circ = OPENQASM2Language().decode(f.read())
        ToCNOTPass().run(circ)
        depth = circ.num_cycles
        parallelism = circ.parallelism

    return {"Synthesized CNOTs": cnots, "SWAPs from routing": swaps, "Circuit Depth": depth, "Parallelism": parallelism}
    # return (
    # 	f"Synthesized CNOTs: {cnots}\nSWAPs from routing: {swaps}\n"
    # 	f"Circuit depth: {depth}\nParallelism: {parallelism}\n"
    # )


def get_remapping_results(
    options : dict[str, Any],
) -> dict:
    path = options["remapped_qasm_file"]
    cnots = 0
    swaps = 0
    with open(path, "r") as qasmfile:
        for line in qasmfile:
            if match("cx", line):
                cnots += 1
            elif match("swap", line):
                swaps += 1
    with open(path, "r") as f:
        circ = OPENQASM2Language().decode(f.read())
        ToCNOTPass().run(circ)
        depth = circ.num_cycles
        parallelism = circ.parallelism
    return {"Synthesized CNOTs": cnots, "SWAPs from routing": swaps, "Circuit Depth": depth, "Parallelism": parallelism}


def get_original_count(
    options : dict[str, Any],
) -> str:
    path = options["original_qasm_file"]
    cnots = 0
    with open(path, "r") as qasmfile:
        for line in qasmfile:
            if match("cx", line):
                cnots += 1
    with open(path, "r") as f:
        circ = OPENQASM2Language().decode(f.read())
        ToCNOTPass().run(circ)
        depth = circ.num_cycles
        parallelism = circ.parallelism
    return (
        f"Original CNOTs: {cnots}\nOriginal depth: {depth}\n"
        f"Parallelism: {parallelism}\n"
    )


def rewrite_block(
    block_path : str,
    original_qudit_group : Sequence[int],
    new_qudit_group : Sequence[int],
    options : dict[str, Any],
) -> None:
    circuit = load_block_circuit(block_path, options)

    for i, qudit in enumerate(sorted(new_qudit_group)):
        if qudit in original_qudit_group:
            continue
        circuit.insert_qudit(i)
    
    save_block_circuit(block_path, circuit, options)
