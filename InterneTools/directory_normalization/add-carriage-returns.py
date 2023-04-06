import os
import gzip
import shutil
import argparse

arg_parser = argparse.ArgumentParser(description="adds a carriage return to the mps file if necessary and gzips the mps files of the input directory if necessary")

arg_parser.add_argument('--input_dir', action='store', required=True, help='The input directory')
args = arg_parser.parse_args()


def add_carriage_return_to_file(file_path):
    with gzip.open(file_path, 'rb') as f_in:
        data = f_in.read()
    if data.endswith("\n"):
        return
    with gzip.open(file_path, 'wb') as f_out:
        f_out.write(data + b'\n')


def update_mps_gz_files_in_directory(directory):
    count=0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.mps'):
                with open(file, 'rb') as f_in:
                    file_gz=file+".gz"
                    f_out=gzip.open(file_gz,"wb")
                    shutil.copyfileobj(f_in, f_out)
                    del(file)
                    file=file_gz

            if file.endswith('.mps.gz'):
                print(file)
                count+=1
                print(count)
                file_path = os.path.join(root, file)
                add_carriage_return_to_file(file_path)


# Usage example:

update_mps_gz_files_in_directory(args.input_dir)
