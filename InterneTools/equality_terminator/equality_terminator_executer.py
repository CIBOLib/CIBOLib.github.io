import os
import subprocess

#link = "./MIPLIB2010/acc-tight5_100_0.mps.gz"
#originalPath = os.readlink(link)
#print("Symbolic link points to", originalPath)
mps_aux_dict={}
subprocs = []
dir_path="./MIPLIB2010/"
output_dir_path="./newMiplib2010"
os.makedirs(output_dir_path,exist_ok=True)
for aux_file in os.scandir(path=dir_path):
    if aux_file.is_file():
        if aux_file.name.endswith(".aux"):
            mps_link=dir_path + aux_file.name[:-len("aux")]+"mps.gz"
            mps_file=dir_path+os.readlinkreadlink(mps_link)
            if mps_file in mps_aux_dict.keys():
                mps_aux_dict[mps_file].append(dir_path+aux_file.name)
            else:
                mps_aux_dict[mps_file]=[dir_path+aux_file.name]
            

for mps_file in mps_aux_dict.keys():
    
        command=f"python3 ./equality_terminator.py "+mps_file+ " --aux_files "+ str(mps_aux_dict[mps_file])
        
        command=["python3", "./equality_terminator.py", mps_file, "--aux_files"]
        command.extend(mps_aux_dict[mps_file])
        command.extend(["--output_dir", output_dir_path, "--gzip_output"])
        print(command)
        subprocess.run(command)

	
