import subprocess
import os
import os.path as path
import argparse

arg_parser = argparse.ArgumentParser(
    description="executes the filmosi (Fischetti, Ljubic, Monaci and Sinnl) solver for given auxfile"
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

counter = 0

if aux_file_path.endswith(".aux"):
    path_aux_file_without_extension = aux_file_path[: -len(".aux")]
    filename = path_aux_file_without_extension.rsplit("/", 1)[1]
    output_path_without_extension = path.join(output_dir, filename)
    print("Solve instance ", filename)

    with open(output_path_without_extension + ".mibs.log", "w") as output:
        command = [
            "dist/bin/mibs",
            "-Alps_instance",
            path_aux_file_without_extension + ".mps.gz",
            "-MibS_auxiliaryInfoFile",
            aux_file_path,
            "-Alps_timeLimit",
            "3600",
            "-writeSolnFile",
            output_path_without_extension + ".mibs.sol"
        ]
        # print(command)
        try:
            subprocess.run(command, stdout=output, timeout=3800)
            # run waits until the process is finished
        except subprocess.TimeoutExpired:
            print("Set timelimit was not respected by solver. Killed process on my own!")
