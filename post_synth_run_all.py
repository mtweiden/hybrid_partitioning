import os


synth_files = os.listdir("synthesis_files")
already_mapped_files = os.listdir("mapped_qasm")


for name in synth_files:
    # tfim_10_falcon_16_blocksize_4_quick_kernel 
    dir_name = os.path.join("synthesis_files", name)
    mapped_name = os.path.join("mapped_qasm",name+"_qiskit.qasm")
    if "resynth" in name or "nosynth" in name:
        continue
    if os.path.exists(mapped_name):
        continue
    if len(os.listdir(dir_name)) != 0:
        name_arr = name.split("_")
        test_name = "_".join(name_arr[0:2])
        topology = name_arr[2]
        blocksize = name_arr[5]
        partitioner = name_arr[-2]
   
        cmd = "python stas.py qasm/{}.qasm --topology={} --blocksize={} --partitioner={}".format(test_name, topology, blocksize, partitioner)
        print(cmd)
        os.system(cmd)
