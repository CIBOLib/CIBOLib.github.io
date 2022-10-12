'''
Created on 17.09.2022

@author: michelle
'''
from bz2 import compress
import json
import os
import tarfile
from subprocess import Popen
from json2html import *

def addToHtml(json_str, infos: dict):
    json_file = open(json_str, "r")
    default_dict = json.load(json_file)
    infos.update(default_dict)
    json_file.close()
    json_file = open(json_str, "w")
    json_file.write(json2html.convert(json = infos))
    json_file.close()
    return infos


def initializeHtml(instance: str, folder: str, collection_home: str, htmls_home: str):

    # get the name of the instance
    instance_without_extension = instance[:-len(".aux")]

    # make the directories if they do not exists and get the new path for the json which will be created by the stats_writer
    instanceHtml = htmls_home+folder[len(collection_home):]
    os.makedirs(instanceHtml, exist_ok=True)
    instanceHtml += "/"+instance_without_extension+".html"

    # let the stats_writer initialize the json of the current instance
    process = Popen(["./stats_writer", "-i", folder+"/" +
                    instance_without_extension, "-c", instanceHtml])
    exit_code = process.wait()
    return instanceHtml, instance_without_extension


def create_htmls_json_andCompress(collection_home: str, htmls_home: str, archives_home:str):
    complete_dictionary: dict = {}
    os.makedirs(archives_home+"archives", exist_ok=True)
    for folder, _, instances in os.walk(collection_home, topdown=True):
        #compress
        if ".git" in folder or folder in collection_home: #git raus und collection_home raus
            continue;
        tar = tarfile.open(archives_home+"archives/"+os.path.basename(folder)+".tar.gz", "w:gz")
        tar.add(folder)
        tar.close()
        #create big json and htmls
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
                    "Path": str("https://cibolib.github.io/htmls/collection/mip-mip/"+folder[len(collection_home+"mip-mip/"):])})
                complete_dictionary[instance_without_extension] = dictionary_of_instance
    return complete_dictionary


if __name__ == "__main__":
    collection_home = input("Path: .../collection/ ")
    htmls_home = input("Path for initialized htmls ")
    archives_home=input("Path for tar.gz ")
    complete_dictionary = create_htmls_json_andCompress(collection_home, htmls_home,archives_home)
    json_file = open(htmls_home+"all_instances.json", "w")
    json.dump(complete_dictionary, json_file)
    json_file.close()
