import os
import subprocess
"""
We run filmosi_solution_parser_executer.py for all instances/directories in collection
insert the paths at ...
"""

# now we go through all directories of collection
root_dir = ".../collection/"

# containing all logfiles of filmosi
logfile_dir = ".../logfiles-filmosi-complete-run-25-3-23/"

# output_dir of resulting dictionaries
output_dir = "./Test"

for root, dirs, files in os.walk(root_dir):
    # exclude hidden directories
    dirs[:] = [d for d in dirs if not d[0] == '.']
    # # run filmosi_solution_parser_executer.py for the directories
    for dir in dirs:
        command=["python3" ,".../filmosi_solution_parser_executer.py",
                 "--input_mpsaux_dir", root+"/"+str(dir),
                 "--input_log_dir", logfile_dir,
                 "--output_dir", output_dir]
        subprocess.run(command);  #run waits until the process is finished
