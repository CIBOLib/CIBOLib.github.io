import os
import subprocess
import argparse
"""
We run filmosi or mibs solution_parser_executer.py for all instances/directories in collection
insert the paths at ...
"""

arg_parser = argparse.ArgumentParser(
    description="run solution_parser_executer for each dir of collection"
)
arg_parser.add_argument(
    "--collection",
    action="store",
    required=True,
    help="Directory of the considered instances",
)
arg_parser.add_argument(
    "--logfile_dir", action="store", required=True, help="Directory of the logfiles"
)
arg_parser.add_argument(
    "--store_dir", action="store", required=True, help="Directory in which the results are stored"
)
arg_parser.add_argument(
    "--solver", action="store", required=True, help="filmosi || mibs"
)
args = arg_parser.parse_args()

# now we go through all directories of collection
root_dir = args.collection

# containing all logfiles of filmosi
logfile_dir = args.logfile_dir

# directory where to store the output
output_dir = args.store_dir

solver= args.solver


if solver in ["mibs","filmosi"]:
    for root, dirs, files in os.walk(root_dir):
        # exclude hidden directories
        dirs[:] = [d for d in dirs if not d[0] == '.']
        # # run filmosi_solution_parser_executer.py for the directories
        for dir in dirs:
            command=["python3" ,"solution_parser_executer.py",
                    "--input_mpsaux_dir", root+"/"+str(dir),
                    "--input_log_dir", logfile_dir,
                    "--output_dir", output_dir,
                    "--solver", solver]
            subprocess.run(command);  #run waits until the process is finished
