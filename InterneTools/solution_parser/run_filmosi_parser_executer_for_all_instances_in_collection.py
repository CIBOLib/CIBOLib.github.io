import os
import subprocess
"""
We run filmosi_solution_parser_executer.py for all instances/directories in collection
"""

# now we go through all directories of collection
root_dir = "/home/michelle/Arbeit_Praktikas/HiWiJobs_und_Stundenzettel/gh_Pages_projekt/collection/"

# containing all logfiles of filmosi
logfile_dir = "/home/michelle/Nextcloud/Masterarbeit_Praxis/filmosi_run_25-27_3/logfiles-filmosi-complete-run-25-3-23/"

# output_dir of resulting dictionaries
output_dir = "./Test"

for root, dirs, files in os.walk(root_dir):
    # exclude hidden directories
    dirs[:] = [d for d in dirs if not d[0] == '.']
    # # run filmosi_solution_parser_executer.py for the directories
    for dir in dirs:
        command=["python3" ,"/home/michelle/Arbeit_Praktikas/HiWiJobs_und_Stundenzettel/gh_Pages_projekt/CIBOLib.github.io/InterneTools/solution_parser/filmosi_solution_parser_executer.py",
                 "--input_mpsaux_dir", root+"/"+str(dir),
                 "--input_log_dir", logfile_dir,
                 "--output_dir", output_dir]
        subprocess.run(command);  #run waits until the process is finished
