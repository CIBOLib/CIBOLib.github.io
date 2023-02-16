import subprocess
import os
import os.path as path
import argparse

arg_parser = argparse.ArgumentParser(description="executes the equality_terminator for all files in the input_dir")
arg_parser.add_argument('--input_dir', action='store', required=True, help='The input directory')
arg_parser.add_argument('--output_dir', action='store', required=True, help='The output directory')
arg_parser.add_argument('--start_index', action='store', required=True, help='Index of instance list we begin with')
arg_parser.add_argument('--end_index', action='store', required=True, help='Index of instance list we stop')

args = arg_parser.parse_args()

input_dir = args.input_dir
output_dir = args.output_dir

start_index = int(args.start_index)
end_index = int(args.end_index)


os.makedirs(output_dir, exist_ok=True)

counter = 0

for filename in os.listdir(input_dir):
    if(filename.endswith(".aux")):
        
        if counter >= start_index and counter <= end_index:
            filename_without_extension=filename[:-len(".aux")]
            output_path_without_extension = path.join(output_dir, filename_without_extension)
            input_path_without_extension = path.join(input_dir, filename_without_extension)

            print("Solve instance ", filename_without_extension)

            with open(output_path_without_extension+".txt", "w") as output:

                command=["dist/bin/mibs", "-Alps_instance", input_path_without_extension+".mps.gz", "-MibS_auxiliaryInfoFile", input_path_without_extension+".aux", "-Alps_timeLimit", "3600"]
                #print(command)
                subprocess.run(command, stdout=output); #run waits until the process is finished
        counter=counter+1
        if counter > end_index:
            break
    
    
