import json

def dump_json_to_file(filename: str, value):
    with open(filename+".json", 'w') as json_file:
        json.dump(value, json_file, indent=4)
