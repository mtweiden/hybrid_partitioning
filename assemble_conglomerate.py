import argparse
from os import listdir
from os.path import exists
from bqskit import Circuit
from bqskit.ir.gates.constant.cx import CNOTGate
from bqskit.ir.point import CircuitPoint
from bqskit.ir.gates.circuitgate import CircuitGate
from topology import kernel_type
import pickle
from conglomerate import get_block_logical_edges, match_kernel

def get_subtopology(circuit):
	edge_set = set([])
	for op in circuit:
		if len(op.location) > 1:
			edge_set.add(op.location)
	return list(edge_set)
			

def write_subtopology(edge_set, location):
	with open(location, "wb") as f:
		pickle.dump(edge_set, f)

def write_block(qasm_file, location):
	with open(location, "w") as f_out:
		with open(qasm_file, "r") as f_qasm:
			f_out.write(f_qasm.read())

if __name__ == '__main__':
	"""
	NOTE: Only support blocksize 4 right now
	"""

	parser = argparse.ArgumentParser()
	# NOTE: Give block_files/benchmark directory
	parser.add_argument("benchmark", type=str)
	args = parser.parse_args()

	if args.benchmark.endswith('/'):
		benchmark = args.benchmark.split('/')[-2]
	else:
		benchmark = args.benchmark.split('/')[-1]
	if '-' in benchmark:
		benchmark = benchmark.split('-')[-1]

	print(benchmark)
	bname = benchmark.split('_preoptimized')[0]
	mesh_suffices = (
		"mesh_16", "mesh_25", "mesh_36", "mesh_49",
		"mesh_64", "mesh_81", "mesh_100", "mesh_121"
	)
	for suffix in mesh_suffices:
		mesh_name = f'{bname}_preoptimized_{suffix}_blocksize_4_scan'
		if exists(f'block_files/{mesh_name}'):
			break

	benchmark_base   = f'block_files/{benchmark}'
	benchmark_lines  = f'synthesis_files/conglomerate_lines-{mesh_name}_kernel'
	benchmark_stars  = f'synthesis_files/conglomerate_stars-{mesh_name}_kernel'
	benchmark_rings  = f'synthesis_files/conglomerate_rings-{mesh_name}_kernel'
	subtopology_lines  = f'subtopology_files/conglomerate_lines-{mesh_name}_kernel'
	subtopology_stars  = f'subtopology_files/conglomerate_stars-{mesh_name}_kernel'
	subtopology_rings  = f'subtopology_files/conglomerate_rings-{mesh_name}_kernel'

	# trees
	output_blocks       = f'synthesis_files/conglomerate_trees-{benchmark}_kernel'
	output_topologies = f'subtopology_files/conglomerate_trees-{benchmark}_kernel'
	valid_subtopologies = 'trees'
	## embedded
	#output_blocks       = f'synthesis_files/conglomerate_embedded-{benchmark}_kernel'
	#output_topologies = f'subtopology_files/conglomerate_embedded-{benchmark}_kernel'
	#valid_subtopologies = 'embedded'

	partitioned_circuit = f'partitioned_circuits/{mesh_name}.pickle'
	with open(partitioned_circuit, "rb") as f:
		circuit : Circuit = pickle.load(f)

	group_to_indices = {} 
	group_to_block_nums = {}
	block_count = 0

	# Organize blocks by which qudits they act on
	for cycle, partition in circuit.operations_with_cycles():
		location = tuple(partition.location)
		if not location in group_to_indices.keys():
			group_to_indices[location] = [(cycle, location[0])]
			group_to_block_nums[location] = [block_count]
		else:
			group_to_indices[location].append((cycle, location[0]))
			group_to_block_nums[location].append(block_count)
		block_count += 1
	
	# Go through the group list and collect the conglomerate operations 
	conglomerate_operations = {}
	for group in group_to_indices.keys():
		points_to_consider = group_to_indices[group]
		operations = []
		for cycle, qubit in points_to_consider:
			op = circuit.get_operation(CircuitPoint(cycle,qubit))
			if isinstance(op.gate, CircuitGate):
				block_circ = Circuit(len(group))
				block_circ.append_gate(
					op.gate, range(len(group)), op.params
				)
				block_circ.unfold_all()
				operations.extend(get_block_logical_edges(block_circ))
		conglomerate_operations[group] = operations

	# Select subtopologies for each conglomerate group
	conglomerate_subtopologies = {}
	for group in group_to_indices.keys():
		print(conglomerate_operations[group])
		conglomerate_subtopologies[group] = match_kernel(
			conglomerate_operations[group], len(group), valid_subtopologies
		)
	
	# Choose the subtopology that has the fewest CNOTs across all groups
	line_cnots = {}
	star_cnots = {}
	ring_cnots = {}
	from math import ceil, log10
	for block_num, op in enumerate(circuit.operations()):

		block_num_str = str(block_num).zfill(ceil(log10(block_count)))
		block_name = f"block_{block_num_str}.qasm"

		line_circ = Circuit(1).from_file(f'{benchmark_lines}/{block_name}')
		star_circ = Circuit(1).from_file(f'{benchmark_stars}/{block_name}')
		ring_circ = Circuit(1).from_file(f'{benchmark_rings}/{block_name}')
		line_count_for_block = line_circ.count(CNOTGate())
		star_count_for_block = star_circ.count(CNOTGate())
		ring_count_for_block = ring_circ.count(CNOTGate())

		if tuple(op.location) not in line_cnots.keys():
			line_cnots[tuple(op.location)] = line_count_for_block
		else:
			line_cnots[tuple(op.location)] += line_count_for_block
		if tuple(op.location) not in star_cnots.keys():
			star_cnots[tuple(op.location)] = star_count_for_block
		else:
			star_cnots[tuple(op.location)] += star_count_for_block
		if tuple(op.location) not in ring_cnots.keys():
			ring_cnots[tuple(op.location)] = ring_count_for_block
		else:
			ring_cnots[tuple(op.location)] += ring_count_for_block

	from math import log10, ceil
	for block_num, op in enumerate(circuit.operations()):

		block_num_str = str(block_num).zfill(ceil(log10(block_count)))
		block_name = f"block_{block_num_str}"

		# Choose subtopology with fewest CNOTs
		line_count = line_cnots[tuple(op.location)]
		star_count = star_cnots[tuple(op.location)]
		ring_count = ring_cnots[tuple(op.location)]

		min_count = min([line_count, star_count, ring_count])
		
		subtopology_name = f'{block_name}_kernel.pickle'
		subcircuit_name  = f'{block_name}.qasm'

		subtopology_source = ''
		subcircuit_source  = ''
		if min_count == line_count:
			subtopology_source = f'{subtopology_lines}/{subtopology_name}'
			subcircuit_source    = f'{benchmark_lines}/{subcircuit_name}'
		elif min_count == star_count:
			subtopology_source = f'{subtopology_stars}/{subtopology_name}'
			subcircuit_source    = f'{benchmark_stars}/{subcircuit_name}'
		else:
			subtopology_source = f'{subtopology_rings}/{subtopology_name}'
			subcircuit_source    = f'{benchmark_rings}/{subcircuit_name}'

		# Copy over blocks and subtopologies
		with open(subtopology_source, 'rb') as f:
			subtopology = pickle.load(f)
		with open(subcircuit_source, 'r') as f:
			subcircuit = f.read()
		
		with open(f"{output_topologies}/{subtopology_name}", "wb") as f:
			pickle.dump(subtopology, f)
		with open(f"{output_blocks}/{subcircuit_name}", "w") as f:
			f.write(subcircuit)
