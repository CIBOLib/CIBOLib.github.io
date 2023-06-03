# should be considered to add an argument for different solver

import os
import os.path as path
import argparse
from multiprocessing import Pool

from lib.filmosi_solution_parser import Filmosi_Solution_Parser
from lib.mibs_solution_parser import Mibs_Solution_Parser
from lib.util import dump_json_to_file


def process_mibs(mps, aux, logfile):
    return Mibs_Solution_Parser(translate_var_indices).run(mps, aux, logfile)


def process_filmosi(mps, aux, logfile):
    return Filmosi_Solution_Parser().run(mps, aux, logfile)


def process_instance(input_files, output_file):
    mps_file, aux_file, logfile = input_files
    print(f"processing {logfile}")
    result = parse_file(mps_file, aux_file, logfile)
    dump_json_to_file(output_file, result)


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
arg_parser.add_argument("--index_based", action=argparse.BooleanOptionalAction,
                        help="translate the index-based output of mibs to variable names")

args = arg_parser.parse_args()

translate_var_indices = args.index_based
solver = args.solver
input_log_dir = args.input_log_dir
folder_contains_links = False

input_instances = {}
for curdir, _, files in os.walk(args.input_mpsaux_dir):
    for aux_file in (x for x in files if x.endswith(".aux")):
        instance = aux_file.removesuffix('.aux')
        if instance in input_instances:
            raise Exception(
                f"instance {instance} is present in the collection twice")

        mps_file = path.join(curdir, f"{instance}.mps")
        if not path.exists(mps_file):
            mps_file = mps_file + ".gz"
        if not path.exists(mps_file):
            raise Exception(f"could not find mps file for instance {instance}")
        aux_file = path.join(curdir, aux_file)

        log_file = path.join(input_log_dir, instance+f".{solver}.log")
        if path.exists(log_file):  # logfile does not exist
            input_instances[instance] = (mps_file, aux_file, log_file)


output_dir = args.output_dir

os.makedirs(output_dir, exist_ok=True)

parse_file = process_filmosi
if solver == "mibs":
    parse_file = process_mibs

keys = list(input_instances.keys())

for i in range(len(input_instances)):
    output_path = path.join(output_dir, keys[i]) + f".{solver}.res"
    process_instance(input_instances[keys[i]], output_path)
