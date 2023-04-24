import os
import subprocess

# now we go through all directories of collection
input_dir = "/home/michelle/Arbeit_Praktikas/HiWiJobs_und_Stundenzettel/gh_Pages_projekt/collection/general-bilevel/mixed-integer/MIPLIB2017/"
output_dir= "/home/michelle/Arbeit_Praktikas/HiWiJobs_und_Stundenzettel/gh_Pages_projekt/collection/general-bilevel/mixed-integer/MIPLIB2017_delSymb/"

os.makedirs(output_dir, exist_ok=True)
files=os.scandir(input_dir)
for file in files:
    # exclude hidden directories
    if file.name.endswith("mps.gz"):
            mps_link=os.path.join(input_dir,file.name)
            if os.path.islink(mps_link):
                original_name=os.readlink(mps_link)
                mps_file_in=os.path.join(input_dir,original_name)
                original_name=original_name.split("/")[1]
                mps_file_out=os.path.join(output_dir,file.name)
                command_copy=["cp", mps_file_in, os.path.join(output_dir,original_name)]
                command_rename=["mv", os.path.join(output_dir,original_name), mps_file_out]
                subprocess.run(command_copy) #copy the symbolic link not the original mps.gz in the output_dir
                subprocess.run(command_rename)
    else:
        subprocess.run(["cp",os.path.join(input_dir,file.name), os.path.join(output_dir,file.name)])