import re
import sys
from os import listdir
from numpy import pi

#pattern = r"[+-]?\d+e[-+]?\d+|[-+]?\d*\.\d+e[-+]?\d+|[-+]?\d*\.\d+|[-+]?\d+|q\[\d+\]|[+-]?\d+\*pi|[+-]?pi/\d+|[+-]?\d+\*pi/\d+|[+-]?pi"
pattern = r"[+-]?\d+e[-+]?\d+|[-+]?\d*\.\d+e[-+]?\d+|[-+]?\d*\.\d+|[-+]?\d+|q\[\d+\]"

def str_to_float(input_str: str) -> float:
	value = 0
	try:
		value = float(input_str)
		return value
	except ValueError:
		# See if there is a multiplier or divider
		mul = 1
		div = 1
		prefix = re.findall(r"[+-]?\d+\*", input_str)
		suffix = re.findall(r"/\d+", input_str)
		if len(prefix) > 0:
			mul = int(prefix[0])
		if len(suffix) > 0:
			div = int(suffix[0][1:])
		value = mul * pi / div
		return value
		

if __name__ == "__main__":

	input_files = sorted(listdir(sys.argv[1]))
	#input_files = sys.argv[1]
	
	for input_file in input_files:
		if input_file.endswith(".qasm"):
			lines = ""
			with open(f"{sys.argv[1]}/{input_file}", "r") as f:
				for line in f:
					new_line = ""
					pattern = 'u3\(1e-07'
					if re.match(pattern, line):
						print(input_file)

#					if re.match(r"u3", line):
#						# Just ignore pi for now
#						if len(re.findall("pi", line)) > 0:
#							continue
#						params = re.findall(pattern, line)
#						new_line = "u3("
#						# Start params offsets at 1 because the 3 from u3 counts
#						# Need to handle "pi"
#						#new_line += "{:0.16f}, ".format(str_to_float(params[1]))
#						#new_line += "{:0.16f}, ".format(str_to_float(params[2]))
#						#new_line += "{:0.16f}) ".format(str_to_float(params[3]))
#						new_line += "{:0.16f}, ".format(float(params[1]))
#						new_line += "{:0.16f}, ".format(float(params[2]))
#						new_line += "{:0.16f}) ".format(float(params[3]))
#						new_line += params[4]
#						new_line += ";\n"
#					elif re.match(r"rx", line):
#						if len(re.findall("pi", line)) > 0:
#							continue
#						params = re.findall(pattern, line)
#						new_line = "rx("
#						#new_line += "{:0.16f}) ".format(str_to_float(params[0]))
#						new_line += "{:0.16f}) ".format(float(params[0]))
#						new_line += params[1]
#						new_line += ";\n"
#					elif re.match(r"rz", line):
#						if len(re.findall("pi", line)) > 0:
#							continue
#						params = re.findall(pattern, line)
#						new_line = "rz("
#						#new_line += "{:0.16f}) ".format(str_to_float(params[0]))
#						new_line += "{:0.16f}) ".format(float(params[0]))
#						new_line += params[1]
#						new_line += ";\n"
#					elif re.match(r"ry", line):
#						if len(re.findall("pi", line)) > 0:
#							continue
#						params = re.findall(pattern, line)
#						new_line = "ry("
#						#new_line += "{:0.16f}) ".format(str_to_float(params[0]))
#						new_line += "{:0.16f}) ".format(float(params[0]))
#						new_line += params[1]
#						new_line += ";\n"
#					else:
#						new_line = line
#					lines += new_line
#
##			with open(f"{sys.argv[1]}/{input_file}", "w") as f:
##				f.write(lines)
#			print(lines)
