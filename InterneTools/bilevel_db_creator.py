'''
Created on 17.09.2022

@author: michelle
'''
import json
import os
from subprocess import Popen


def addToJson(json_str, infos: dict):
    json_file=open(json_str,"r")
    default_dict=json.load(json_file)
    json_file.close()
    json_file=open(json_str,"w")
    infos.update(default_dict)
    json.dump(infos, json_file)
    json_file.close()
    return infos

def initializeJson(instance: str, folder: str, collection_home: str, jsons_home: str):

    # get the name of the instance
    instance_without_extension = instance[:-len(".aux")]

    # make the directories if they do not exists and get the new path for the json which will be created by the stats_writer
    instanceJson = jsons_home+folder[len(collection_home):]
    os.makedirs(instanceJson, exist_ok=True)
    instanceJson += "/"+instance_without_extension+".json"

    # let the stats_writer initialize the json of the current instance
    process = Popen(["./stats_writer", "-i", folder+"/" +
                    instance_without_extension, "-c", instanceJson])
    exit_code = process.wait()
    return instanceJson, instance_without_extension


def create_default_jsons(collection_home: str, jsons_home: str):
    complete_dictionary:dict={}
    for folder, _, instances in os.walk(collection_home, topdown=True):
        for instance in instances:
            if instance.endswith(".aux"):
                instanceJson, instance_without_extension = initializeJson(
                    instance, folder, collection_home, jsons_home)

                # string which includes further default informations
                class_type_folder = folder[len(
                    collection_home+"mip-mip/"):].split("/")
                class_information = class_type_folder[0]
                type_information = class_type_folder[1]

                dictionary_of_instance=addToJson(instanceJson, {
                          "Instance": instance_without_extension,"Type": type_information, "Class": class_information })
                complete_dictionary[instance_without_extension]=dictionary_of_instance
    return complete_dictionary



if __name__ == "__main__":
    collection_home = input("Path: .../collection/ ")
    jsons_home = input("Path for initialized jsons ")
    complete_dictionary=create_default_jsons(collection_home, jsons_home)
    json_file=open(jsons_home+"all_instances.json","w")
    json.dump(complete_dictionary, json_file)
    json_file.close()

