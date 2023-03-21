#Execute this script, while the terminal you use is actually in the solver-directory. A flag --programm_dir could not be used since
# the libcplex.so etc. cannot be found then

import subprocess
import os
import os.path as path
import argparse


arg_parser = argparse.ArgumentParser(description="executes the filmosi (Fischetti, Ljubic, Monaci and Sinnl) solver for all files in the input_dir")
arg_parser.add_argument('--input_dir', action='store', required=True, help='The input directory')
arg_parser.add_argument('--output_dir', action='store', required=True, help='The output directory')
arg_parser.add_argument('--start_index', action='store', required=True, help='Index of instance list we begin with')
arg_parser.add_argument('--end_index', action='store', required=True, help='Index of instance list we stop')

# we only solve instances the --start_index-th aux-file and stop with the --end_index-th-1 auxfile
# within the considered directory
# example: start_index = 0, end_index = 2 -> we solve the first, second, and third aux file in the considered directory

args = arg_parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir

start_index = int(args.start_index)
end_index = int(args.end_index)

os.makedirs(output_dir, exist_ok=True)

counter = 0

for filename in os.listdir(input_dir):

    if(filename.endswith(".aux")):

        # only solve instance if it is in range of the instances to solve
        if counter >= start_index and counter <= end_index:
            filename_without_extension=filename[:-len(".aux")]
            output_path_without_extension = path.join(output_dir, filename_without_extension)
            input_path_without_extension = path.join(input_dir, filename_without_extension)

            print("Solve instance number", counter, "with name", filename_without_extension)

            with open(output_path_without_extension+".filmosi.log", "w") as output:
                command=["./bilevel", "-mpsfile", input_path_without_extension+".mps.gz", "-auxfile", input_path_without_extension+".aux", "-time_limit", "3600", "-available_memory", "16000"]
                #print(command)
                subprocess.run(command, stdout=output); #run waits until the process is finished

        # increase counter
        counter=counter+1

        # we can break if counter is greater than end_index
        if counter > end_index:
            break
