from __future__ import annotations
from typing import Sequence

from scipy.stats import unitary_group
from scipy.stats.morestats import circmean

from qiskit.quantum_info import OneQubitEulerDecomposer

from sys import path
path.append("../bqskit")

from bqskit.ir import Circuit
from bqskit.ir.lang.qasm2.qasm2 import OPENQASM2Language
from bqskit.compiler.machine import MachineModel
from bqskit.compiler.passes.partitioning.scan import ScanPartitioner

#from qsearch.utils import endian_reverse

from mapping import do_layout, do_routing, find_num_qudits
from hybrid_topology import get_hybrid_edge_set, save_hybrid_topology
from old_codebase import call_old_codebase_leap, parse_leap_files, check_for_leap_files

from math import ceil, sqrt
from os.path import exists
import argparse


def get_sub_topology(
	topology : Sequence[Sequence[int]],
	subset : list[int]
) -> set[tuple[int]]:
	subset_map_inv = {i:subset[i] for i in range(len(subset))}
	subset_map = {v: k for k, v in subset_map_inv.items()}

	sub_topology = set()
	for edge in topology:
		if edge[0] in subset and edge[1] in subset:
			sub_topology.add((subset_map[edge[0]], subset_map[edge[1]]))
			sub_topology.add((subset_map[edge[1]], subset_map[edge[0]]))
	return sub_topology


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Run topoloy aware synthesis"+\
		" based on the hybrid logical-physical topology scheme")
	parser.add_argument("qasm_files", nargs='+', type=str, 
		help="files to synthesize")
	parser.add_argument("--block_size", dest="block_size", action="store",
		nargs='?', default=3, type=int, help="synthesis block size")
	parser.add_argument("--reuse_edges", action="store_true",
		help="reuse logical edges in the hybrid topology")
	parser.add_argument("--shortest_path", action="store_true",
		help="use shortest paths in the physical topology to add logical edges")
	parser.add_argument("--add_interactors", action="store_true",
		help="add extra edges for strongly interacting qudits")
	args = parser.parse_args()

	for qasm_file in args.qasm_files:
		# Run setup
		num_q = find_num_qudits(qasm_file)
		num_p = ceil(sqrt(num_q))
		coupling_map = "coupling_maps/mesh_%d_%d" %(num_p, num_p)
		#coupling_map = "coupling_maps/alltoall_5"

		options = {
			"block_size"	 : args.block_size,
			"reuse_edges"	: args.reuse_edges,
			"shortest_path"  : args.shortest_path,
			"add_interactors": args.add_interactors
		}

		target_name = qasm_file.split("qasm/")[-1].split(".qasm")[0]
		target_name += "_" + coupling_map.split("coupling_maps/")[-1]
		layout_qasm_file = "layout_qasm/" + target_name
		synthesized_qasm_file = "synthesized_qasm/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		mapped_qasm_file = "mapped_qasm/" + target_name \
			+ "_blocksize_" + str(args.block_size)
		if args.reuse_edges:
			layout_qasm_file += "_reuseedges"
			synthesized_qasm_file += "_reuseedges"
			mapped_qasm_file += "_reuseedges"
		if args.shortest_path:
			layout_qasm_file += "_shortestpath"
			synthesized_qasm_file += "_shortestpath"
			mapped_qasm_file += "_shortestpath"
		if args.add_interactors:
			layout_qasm_file += "_addinteractors"
			synthesized_qasm_file += "_addinteractors"
			mapped_qasm_file += "_addinteractors"

		# Layout
		print("="*80)
		print("Doing Layout for %s..." %(qasm_file))
		print("="*80)
		if exists(layout_qasm_file):
			print("Found existing file for %s, skipping layout" 
				%(layout_qasm_file))
		else:
			do_layout(qasm_file, coupling_map, layout_qasm_file)

		# Logical Connectivity
		print("="*80)
		print("Doing Logical Connectivity Analysis on %s..."%(layout_qasm_file))
		print("="*80)
		hybrid = get_hybrid_edge_set(layout_qasm_file, coupling_map, options)
		save_hybrid_topology(hybrid, qasm_file, coupling_map, options)

		# Partitioning and synthesis
		print("="*80)
		print("Doing Partitioning on %s..." %(layout_qasm_file))
		print("="*80)
		if exists(synthesized_qasm_file):
			print("Found existing file for %s, skipping synthesis" 
				%(synthesized_qasm_file))
		else:
			with open(layout_qasm_file, 'r') as f:
				circuit = OPENQASM2Language().decode(f.read())
			partitioner = ScanPartitioner(args.block_size)
			machine = MachineModel(circuit.get_size(), hybrid)
			data = {"machine_model": machine}
			partitioner.run(circuit, data)
			print("="*80)
			print("Doing Synthesis on %s..." %(layout_qasm_file))
			print("="*80)
			proj_name = mapped_qasm_file.split("mapped_qasm/")[-1]
			unitaries = [op.get_unitary().get_numpy() for op in circuit]
			locations = [op.location for op in circuit]
			synthesized_qasm = "OPENQASM 2.0;\ninclude \"qelib1.inc\";" + \
				"\nqreg q[%d];\n"%(circuit.get_size())
			for i in range(len(unitaries)):
				unitary = unitaries[i]
				q_map = {k:locations[i][k] for k in range(len(locations[i]))}
				if not check_for_leap_files(proj_name + "_" + str(i)):
					synthesized_qasm += call_old_codebase_leap(
						unitary, 
						list(get_sub_topology(hybrid, locations[i])),
						proj_name + "_" + str(i),
						q_map
					)
				else:
					synthesized_qasm += parse_leap_files(proj_name + "_" \
						+ str(i), q_map)

			# Clean up synthesized qasm
			with open(synthesized_qasm_file, 'w') as f:
				f.write(synthesized_qasm)

		# Routing
		print("="*80)
		print("Doing Routing for %s..." %(synthesized_qasm_file))
		print("="*80)
		if exists(mapped_qasm_file):
			print("Found existing file for %s, skipping routing" 
				%(mapped_qasm_file))
		else:
			do_routing(synthesized_qasm_file, coupling_map, mapped_qasm_file)

