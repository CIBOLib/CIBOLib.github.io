'''
Created on 17.09.2022

@author: michelle
'''
import json
import os
import tarfile
from subprocess import Popen
from json2html import *
import shutil


def addToHtml(json_str: str, infos: dict):
    page_file = open(json_str, "r")
    default_dict = json.load(page_file)
    infos.update(default_dict)
    page_file.close()
    page_file = open(json_str, "w")
    page_file.write(
        "---\nlayout: default\ntitle: CIBOLib Instance "+infos["Instance"]+"\n---\n")

    page_file.write(json2html.convert(json=infos))
    page_file.close()
    return infos


def initializeHtml(instance: str, folder: str, collection_home: str, htmls_home: str):

    # get the name of the instance
    instance_without_extension = instance[:-len(".aux")]
    # where to store html in the end
    instanceHtml = htmls_home + "/"+instance_without_extension+".html"

    # let the stats_writer initialize the json of the current instance -> json will change to html
    process = Popen(["./stats_writer", "-i", folder+"/" +
                    instance_without_extension, "-c", instanceHtml])
    exit_code = process.wait()
    return instanceHtml, instance_without_extension


def create_htmls_json_andCompress(collection_home: str, htmls_home: str, archives_home: str, layout_home:str):
    complete_dictionary: dict = {}
    os.makedirs(archives_home+"archives", exist_ok=True)
    os.makedirs(htmls_home+"/_layouts", exist_ok=True)
    src_path = layout_home+"_layouts/default.html"
    dst_path = htmls_home+"/_layouts/default.html"
    shutil.copy(src_path, dst_path)

    for folder, _, instances in os.walk(collection_home, topdown=True):
        # compress
        if ".git" in folder or folder in collection_home:  # git raus und collection_home raus
            continue
        if True:  # muss nicht immer laufen, wenn ich an den Unterseiten arbeite
            tar = tarfile.open(archives_home+"archives/" +
                               os.path.basename(folder)+".tar.gz", "w:gz")
            tar.add(folder)
            tar.close()
        # create big json and htmls
        for instance in instances:
            if instance.endswith(".aux"):
                instanceHtml, instance_without_extension = initializeHtml(
                    instance, folder, collection_home, htmls_home)

                # string which includes further default informations
                class_type_folder = folder[len(
                    collection_home+"mip-mip/"):].split("/")
                class_information = class_type_folder[0]
                type_information = class_type_folder[1]

                dictionary_of_instance = addToHtml(instanceHtml, {
                    "Instance": instance_without_extension, "Type": type_information, "Class": class_information,
                    "Path": str("https://cibolib.github.io/htmls/"+instance_without_extension+".html"),
                    "Folder": folder[len(collection_home):]})
                complete_dictionary[instance_without_extension] = dictionary_of_instance
    return complete_dictionary


if __name__ == "__main__":
    collection_home = input("Path: .../collection/ ")
    htmls_home = input("Path for initialized htmls ")
    archives_home = input("Path for tar.gz ")
    layout_home = input("Path for layout ")
    complete_dictionary = create_htmls_json_andCompress(
        collection_home, htmls_home, archives_home,layout_home)
    json_file = open(htmls_home+"/all_instances.json", "w")
    json.dump(complete_dictionary, json_file)
    json_file.close()
