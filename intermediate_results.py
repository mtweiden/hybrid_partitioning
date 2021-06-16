"""Module for observing intermediate results from synthesis"""


def check_for_synthesis_results(path_to_synth_project : str) -> str:
	"""
	Check for synthesis results for individual blocks.

	Args:
		path_to_synth_project (str): The path to the directory in which inter-
			mediate synthesis results for individual blocks are stored.
	
	Returns:
		qasm (str): OPENQASM string for the partitioned block. Note that the 
			QASM preamble is included.
	"""
	pass

def find_block_errors(path_to_synth_project : str) -> dict:
	"""
	Retrieve the synthesis error for each block that has been synthesized.

	Args:
		path_to_synth_project (str): The path to the directory in which inter-
			mediate synthesis results for individual blocks are stored.
	
	Returns:
		error_dict (dict): A dictionary where the key is the block number and
			the corresponding value is the error in the synthesis of that
			individual block.
	"""
	pass