import os


block_files = os.listdir("block_files")
synth_files = os.listdir("synthesis_files")


for name in block_files:
    dir_name = os.path.join("synthesis_files", name+"_kernel")
    if not os.path.isdir(dir_name):
        print("\"" + name + "\"")
    elif len(os.listdir(dir_name)) == 0:
        print("\"" + name + "\"")
