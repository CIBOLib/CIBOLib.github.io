'''
Created on 17.09.2022
@author: Michelle Mergen
'''
import json
import os
import tarfile
from subprocess import Popen
from json2html import *
import shutil

def add_To_Html(json_path: str, infos: dict):
    page_file = open(json_path, "r")
    default_dict = json.load(page_file)
    infos.update(default_dict)
    page_file.close()
    page_file = open(json_path, "w")
    page_file.write(
        "---\nlayout: default\ntitle: BOBILib Instance "+infos["Instance"]+"\n---\n")

    page_file.write(json2html.convert(json=infos))
    page_file.close()
    return infos


def initialize_Html(instance: str, folder: str, collection_home: str, htmls_home: str):

    instance_without_extension = instance[:-len(".aux")]
    instance_store_html = htmls_home + "/"+instance_without_extension+".html"

    # let the stats_writer initialize the json of the current instance -> json will change to html
    process = Popen(["./stats_writer", "-i", folder+"/" +
                    instance_without_extension, "-c", instance_store_html])
    exit_code = process.wait()
    return instance_store_html, instance_without_extension


def make_dirs(htmls_home: str, archives_home: str, compress):

    if compress:
        os.makedirs(archives_home, exist_ok=True)
    os.makedirs(htmls_home, exist_ok=True)
    os.makedirs(htmls_home+"/_layouts", exist_ok=True)
    os.makedirs(htmls_home+"/css", exist_ok=True)


def copy_design_files(htmls_home: str, layout_home: str, css_home: str):

    dst_layout_path = htmls_home+"/_layouts/default.html"
    shutil.copy(layout_home, dst_layout_path)

    dst_css_path = htmls_home+"/css/main.css"
    shutil.copy(css_home, dst_css_path)

def compress_to_tarball(folder:str, archives_home:str):
    print("Compress " + os.path.basename(folder) + ".")
    tar = tarfile.open(config_dict["archives_home"] + "/" +
                        os.path.basename(folder)+".tar.gz", "w:gz")
    tar.add(folder, arcname=os.path.basename(folder))
    tar.close()


def create_htmls_json_and_Compress(config_dict:dict):

    config_dict["collection_home"] += "/"

    make_dirs(config_dict["htmls_home"], config_dict["archives_home"], config_dict["compress"])
    copy_design_files(config_dict["htmls_home"], config_dict["layout_home"], config_dict["css_home"])

    complete_dictionary: dict = {}

    for folder, _, instances in os.walk(config_dict["collection_home"], topdown=True):
        # compress, less than all
        if ".git" in folder or folder in config_dict["collection_home"]:
            continue
        # do not compress MIPLIB... etc.
        if config_dict["compress"] and not any((".aux" in instance or ".mps" in instance for instance in instances)):
            compress_to_tarball(folder, config_dict["archives_home"])
            
        # create big json and htmls
        for instance in instances:
            if instance.endswith(".aux"):
                instanceHtml, instance_without_extension = initialize_Html(
                    instance, folder, config_dict["collection_home"], config_dict["htmls_home"])

                # string which includes further default informations
                class_type_folder = folder[len(
                    config_dict["collection_home"]):].split("/")
                class_information = class_type_folder[0]
                type_information = class_type_folder[1]

                dictionary_of_instance = add_To_Html(instanceHtml, {
                    "Instance": instance_without_extension, "Type": type_information, "Class": class_information,
                    "Path": str("https://CIBOLib.github.io/htmls/"+instance_without_extension+".html"), #to change after move
                    "Folder": folder[len(config_dict["collection_home"]):]})

                complete_dictionary[instance_without_extension] = dictionary_of_instance

    return complete_dictionary


def write_big_json(htmls_home:str,complete_dictionary: dict):
    json_file = open(htmls_home+"/all_instances.json", "w")
    json.dump(complete_dictionary, json_file)
    json_file.close()


if __name__ == "__main__":

    config_path = input("Path of config.json (.../config.json,skip if you did not change its location):")
    if len(config_path) == 0:
        config_path = "./config.json"
    config_file = open(config_path, "r")
    config_dict = json.load(config_file)
    
    complete_dictionary = create_htmls_json_and_Compress(config_dict)

    write_big_json(config_dict["htmls_home"],complete_dictionary)
