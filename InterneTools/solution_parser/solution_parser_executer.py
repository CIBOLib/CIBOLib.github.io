# should be considered to add an argument for different solver

import subprocess
import os
import os.path as path
import argparse
import os


arg_parser = argparse.ArgumentParser(
    description="executes the filmosi (Fischetti, Ljubic, Monaci and Sinnl) parser or MibS parser for all files in the input_log_dir")
arg_parser.add_argument('--input_mpsaux_dir', action='store', required=True,
                        help='The input directory of the original mps/aux files')
arg_parser.add_argument('--input_log_dir', action='store',
                        required=True, help='The input directory of the logs')
arg_parser.add_argument('--output_dir', action='store',
                        required=True, help='The output directory')
arg_parser.add_argument(
    "--solver", action="store", required=True, help="filmosi || mibs"
)
args = arg_parser.parse_args()

dir_path = args.input_mpsaux_dir
log_mpsaux_dict = {}  # key=filename_without_extension value: mps_path and aux_path
mps_input_dir = args.input_mpsaux_dir
aux_input_dir = args.input_mpsaux_dir
solver=args.solver

folder_contains_links = False

for aux_file in os.scandir(path=aux_input_dir):
    if aux_file.is_file():
        if aux_file.name.endswith(".aux"):
            aux_filename_without_extension = aux_file.name[:-len(".aux")]
            mps_link = aux_input_dir + "/" + \
                aux_file.name[:-len("aux")]+"mps.gz"
            if os.path.islink(mps_link):
                mps_file = aux_input_dir + "/" + os.readlink(mps_link)
                folder_contains_links = True
            else:
                mps_file = mps_link

            if aux_filename_without_extension in log_mpsaux_dict.keys():
                print("Key cannot be used twice.")
            else:
                log_mpsaux_dict[aux_filename_without_extension] = (
                    mps_file, aux_file.path)

if folder_contains_links:
    mps_input_dir = f"{aux_input_dir}/mps-files"

input_log_dir = args.input_log_dir
output_dir = args.output_dir

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_log_dir):
    if (filename.endswith("."+solver+".log")):
        filename_without_extension = filename[:-len("."+solver+".log")]
        output_path_without_extension = path.join(
            output_dir, filename_without_extension)
        input_path = path.join(input_log_dir, filename)

        if filename_without_extension in log_mpsaux_dict.keys():

            print("Parsing ", filename)

            (mps, aux) = log_mpsaux_dict[filename_without_extension]
            command = ["python3", "./"+solver+"_solution_parser.py", "--logfile", path.join(input_log_dir, filename),
                       "--mpsfile", mps,
                       "--auxfile", aux,
                       "--output_path", output_path_without_extension + "."+solver+".res"]
            # run waits until the process is finished
            subprocess.run(command)
