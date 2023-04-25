# Execute this script, while the terminal you use is actually in the solver-directory. A flag --programm_dir could not be used since
# the libcplex.so etc. cannot be found then

import subprocess
import os
import os.path as path
import argparse

arg_parser = argparse.ArgumentParser(
    description="executes the filmosi (Fischetti, Ljubic, Monaci and Sinnl) solver for all files in the input_dir"
)
arg_parser.add_argument(
    "--aux_file_path",
    action="store",
    required=True,
    help="The auxfile of the instance to solve",
)
arg_parser.add_argument(
    "--output_dir", action="store", required=True, help="The output directory"
)

# we solve problem for given auxfile and assume a directory structure as in the collection, i.e. mpsfile is within the same directory

args = arg_parser.parse_args()

aux_file_path = args.aux_file_path
output_dir = args.output_dir

os.makedirs(output_dir, exist_ok=True)


if aux_file_path.endswith(".aux"):
    path_aux_file_without_extension = aux_file_path[: -len(".aux")]
    filename = path_aux_file_without_extension.rsplit("/", 1)[1]
    output_path_without_extension = path.join(output_dir, filename)
    print("Solve instance ", filename)

    with open(output_path_without_extension + ".filmosi.log", "w") as output:
        command = [
            "./bilevel",
            "-mpsfile",
            path_aux_file_without_extension + ".mps.gz",
            "-auxfile",
            aux_file_path,
            "-time_limit",
            "3600",
            "-available_memory",
            "32768",
            "-print_sol", "2"
        ]
        # print(command)
        subprocess.run(command, stdout=output)
        # run waits until the process is finished
