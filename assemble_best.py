import argparse
from os import listdir
from os.path import exists
from bqskit import Circuit
from bqskit.ir.gates.constant.cx import CNOTGate
from topology import kernel_type
import pickle

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
		"mesh_4", "mesh_9", "mesh_16", "mesh_25", "mesh_36", 
		"mesh_49","mesh_64", "mesh_81", "mesh_100", "mesh_121"
	)
	for suffix in mesh_suffices:
		mesh_name = f'{bname}_preoptimized_{suffix}_blocksize_4_scan'
		if exists(f'block_files/{mesh_name}'):
			break

	#benchmark_base   = f'block_files/{benchmark}'
	#benchmark_lines  = f'synthesis_files/lines-{mesh_name}_kernel'
	#benchmark_stars  = f'synthesis_files/stars-{mesh_name}_kernel'
	#benchmark_rings  = f'synthesis_files/rings-{mesh_name}_kernel'
	#benchmark_kites  = f'synthesis_files/kites-{mesh_name}_kernel'
	#benchmark_thetas = f'synthesis_files/thetas-{mesh_name}_kernel'
	#benchmark_alls   = f'synthesis_files/alls-{mesh_name}_kernel'

	# neighbors
	benchmark_base   = f'block_files/{benchmark}'
	benchmark_lines  = f'synthesis_files/neighbors_lines-{mesh_name}_kernel'
	benchmark_stars  = f'synthesis_files/neighbors_stars-{mesh_name}_kernel'
	benchmark_rings  = f'synthesis_files/neighbors_rings-{mesh_name}_kernel'
	benchmark_kites  = f'synthesis_files/kites-{mesh_name}_kernel'
	benchmark_thetas = f'synthesis_files/thetas-{mesh_name}_kernel'
	benchmark_alls   = f'synthesis_files/alls-{mesh_name}_kernel'

	# WITH NEIGHBOR NAME, OTHER IS ALSO NEIGHBORS JUST WITHOUT THE PREFIX
	## biased
	#best_blocks     = f'synthesis_files/neighbors_biased-{benchmark}_kernel'
	#best_topologies = f'subtopology_files/neighbors_biased-{benchmark}_kernel'
	# trees
	best_blocks       = f'synthesis_files/neighbors_trees-{benchmark}_kernel'
	best_topologies = f'subtopology_files/neighbors_trees-{benchmark}_kernel'
	## embedded
	#best_blocks     = f'synthesis_files/neighbors_embedded-{benchmark}_kernel'
	#best_topologies = f'subtopology_files/neighbors_embedded-{benchmark}_kernel'
	## best
	#best_blocks     = f'synthesis_files/neighbors_best-{benchmark}_kernel'

	## biased
	#best_blocks     = f'synthesis_files/biased-{benchmark}_kernel'
	#best_topologies = f'subtopology_files/biased-{benchmark}_kernel'
	## trees
	#best_blocks       = f'synthesis_files/trees-{benchmark}_kernel'
	#best_topologies = f'subtopology_files/trees-{benchmark}_kernel'
	## embedded
	#best_blocks     = f'synthesis_files/embedded-{benchmark}_kernel'
	#best_topologies = f'subtopology_files/embedded-{benchmark}_kernel'
	## best
	#best_blocks     = f'synthesis_files/best-{benchmark}_kernel'
	#best_topologies = f'subtopology_files/best-{benchmark}_kernel'

	#best_blocks     = f'synthesis_files/{benchmark}_kernel'
	#best_topologies = f'subtopology_files/{benchmark}_kernel'

	blocks = [b for b in sorted(listdir(benchmark_base)) if b.endswith('.qasm')]

	for block in blocks:
		best_topology = f'{block.split(".qasm")[0]}_kernel.pickle'
		circuit_lines = Circuit.from_file(f'{benchmark_lines}/{block}')
		circuit_stars = Circuit.from_file(f'{benchmark_stars}/{block}')
		circuit_rings = Circuit.from_file(f'{benchmark_rings}/{block}')
		#circuit_kites = Circuit.from_file(f'{benchmark_kites}/{block}')
		#circuit_thetas = Circuit.from_file(f'{benchmark_thetas}/{block}')
		#circuit_alls  = Circuit.from_file(f'{benchmark_alls}/{block}')
		#circuit_kites = Circuit(1)
		#circuit_thetas = Circuit(1)
		circuit_alls = Circuit(1)

		## biased
		#ring_bias = 3
		#kite_bias = 4
		#theta_bias = 4
		#all_bias = 500
		# trees
		ring_bias = 10
		kite_bias = 20
		theta_bias = 20
		all_bias = 500
		## embedded
		#ring_bias = 3
		#kite_bias = 10
		#theta_bias = 40
		#all_bias = 40
		## best
		#ring_bias = 0
		#kite_bias = 0
		#theta_bias = 0
		#all_bias = 500

		cnots_lines = circuit_lines.count(CNOTGate())
		cnots_stars = circuit_stars.count(CNOTGate()) + 4
		cnots_rings = circuit_rings.count(CNOTGate()) + ring_bias
		#cnots_kites = circuit_kites.count(CNOTGate()) + kite_bias
		#cnots_thetas= circuit_thetas.count(CNOTGate()) + theta_bias
		#cnots_alls = circuit_alls.count(CNOTGate()) + all_bias

		#cnots_list = [cnots_lines, cnots_stars, cnots_rings, cnots_kites, cnots_thetas, cnots_alls]
		cnots_list = [cnots_lines, cnots_stars, cnots_rings]
		min_cnots = min(cnots_list)
		
		print(f'Assembling best blocks for {benchmark}...')
		if min_cnots == cnots_lines: # lines
			#print(f'{block} - line - (->{cnots_lines}<-, {cnots_stars}, {cnots_rings}) = line selected')
			print(f'{block} - line {min_cnots} - {cnots_list}')
			write_subtopology(get_subtopology(circuit_lines), f'{best_topologies}/{best_topology}')
			write_block(f'{benchmark_lines}/{block}', f'{best_blocks}/{block}')
		elif min_cnots == cnots_stars: # stars
			#print(f'{block} - ({cnots_lines}, ->{cnots_stars}<-, {cnots_rings}) = star selected')
			print(f'{block} - star {min_cnots} - {cnots_list}')
			write_subtopology(get_subtopology(circuit_stars), f'{best_topologies}/{best_topology}')
			write_block(f'{benchmark_stars}/{block}', f'{best_blocks}/{block}')
		elif min_cnots == cnots_rings: # rings
			#print(f'{block} - ({cnots_lines}, {cnots_stars}, ->{cnots_rings}<-) = ring selected')
			print(f'{block} - ring {min_cnots} - {cnots_list}')
			write_subtopology(get_subtopology(circuit_rings), f'{best_topologies}/{best_topology}')
			write_block(f'{benchmark_rings}/{block}', f'{best_blocks}/{block}')
#		elif min_cnots == cnots_kites: # kites 
#			print(f'{block} - kite {min_cnots} - {cnots_list}')
#			write_subtopology(get_subtopology(circuit_kites), f'{best_topologies}/{best_topology}')
#			write_block(f'{benchmark_kites}/{block}', f'{best_blocks}/{block}')
#		elif min_cnots == cnots_thetas: # thetas 
#			print(f'{block} - theta {min_cnots} - {cnots_list}')
#			write_subtopology(get_subtopology(circuit_thetas), f'{best_topologies}/{best_topology}')
#			write_block(f'{benchmark_thetas}/{block}', f'{best_blocks}/{block}')
#		elif min_cnots == cnots_alls: # alls 
#			print(f'{block} - all {min_cnots} - {cnots_list}')
#			write_subtopology(get_subtopology(circuit_alls), f'{best_topologies}/{best_topology}')
#			write_block(f'{benchmark_alls}/{block}', f'{best_blocks}/{block}')


