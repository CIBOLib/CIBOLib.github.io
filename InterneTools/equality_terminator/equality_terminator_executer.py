import os
import subprocess

import argparse

arg_parser = argparse.ArgumentParser(description="executes the equality_terminator for all files in the miplib")

arg_parser.add_argument('--dir_path', action='store', required=True, help='The input directory')
arg_parser.add_argument('--output_dir', action='store', required=True, help='The output directory')
arg_parser.add_argument('--max_parallel', action='store', required=False, default=1, help='the number of commands to run in parallel')

args = arg_parser.parse_args()

#link = "./MIPLIB2010/acc-tight5_100_0.mps.gz"
#originalPath = os.readlink(link)
#print("Symbolic link points to", originalPath)
mps_aux_dict={}
subprocs = []
dir_path=args.dir_path

mps_out_dir = args.output_dir
aux_out_dir = args.output_dir

os.makedirs(aux_out_dir,exist_ok=True)

folder_contains_links = False

for aux_file in os.scandir(path=dir_path):
    if aux_file.is_file():
        if aux_file.name.endswith(".aux"):
            mps_link=dir_path + "/" + aux_file.name[:-len("aux")]+"mps.gz"
            if os.path.islink(mps_link):
                mps_file=dir_path + "/" + os.readlink(mps_link)
                folder_contains_links = True
                subprocess.run(["cp", "-P", mps_link, aux_out_dir])
            else:
                mps_file = mps_link
            print(mps_file)

            if mps_file in mps_aux_dict.keys():
                mps_aux_dict[mps_file].append(aux_file.path)
            else:
                mps_aux_dict[mps_file]=[aux_file.path]

if folder_contains_links:
    mps_out_dir = f"{aux_out_dir}/mps-files"
    os.makedirs(mps_out_dir, exist_ok=True)

here = os.path.dirname(__file__)
if here == "":
    here = "."

def generate_commands():
    for mps_file in mps_aux_dict.keys():
        command=["python3", f"{here}/equality_terminator.py", mps_file, "--mps_output_dir",
                 mps_out_dir, "--aux_output_dir", aux_out_dir, "--gzip_output", "--aux_files"]
        command.extend(mps_aux_dict[mps_file])
        yield command
        # print(command)
        # subprocess.run(command)

max_parallel = args.max_parallel
procs = {}
for command in generate_commands():
    if len(procs) == max_parallel:
        (pid, _) = os.wait()
        del procs[pid]
    print(command)
    new_proc = subprocess.Popen(command)
    procs[new_proc.pid] = new_proc

while len(procs) > 0:
    (pid, _) = os.wait()
    del procs[pid]
