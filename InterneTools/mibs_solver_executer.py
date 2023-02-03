#Execute this script, while the terminal you use is actually in the solver-directory. A flag --programm_dir could not be used since
# the libcplex.so etc. cannot be found then

import subprocess
import os
import os.path as path
import argparse

arg_parser = argparse.ArgumentParser(description="executes the equality_terminator for all files in the input_dir")
arg_parser.add_argument('--input_dir', action='store', required=True, help='The input directory')
arg_parser.add_argument('--output_dir', action='store', required=True, help='The output directory')

args = arg_parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if(filename.endswith(".aux")):

        filename_without_extension=filename[:-len(".aux")]
        output_path_without_extension = path.join(output_dir, filename_without_extension)
        input_path_without_extension = path.join(input_dir, filename_without_extension)

        print("Solve instance ", filename_without_extension)

        with open(output_path_without_extension+".txt", "w") as output:


#todo
#dist/bin/mibs -Alps_instance
#/home/thuerauf/Desktop/tmp/after-equality-rewritten/30n20b8_0_100.mps.gz
#-MibS_auxiliaryInfoFile
#/home/thuerauf/Desktop/tmp/after-equality-rewritten/30n20b8_0_100.aux

            #command=["./bilevel", "-mpsfile", input_path_without_extension+".mps.gz", "-auxfile", input_path_without_extension+".aux", "-time_limit", "3600"]
            #print(command)
            subprocess.run(command, stdout=output); #run waits until the process is finished