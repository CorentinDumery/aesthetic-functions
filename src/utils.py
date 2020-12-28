import json
import os

def format_parameters():
    ''' Modifies all parameter files at once '''
    dir = "./parameters/ignore"
    files = [dir + "/" + x for x in os.listdir(dir) if os.path.isfile(os.path.join(dir, x))]
    for file in files:
        if file[-4:] != ".json":
            print("Opening "+file)

            with open(file, 'r') as outfile:
                json_data = json.load(outfile)

            ### your modification here ###

            ### --- ###

            with open(file, 'w') as outfile:
                json.dump(json_data, outfile, sort_keys=True, indent=4)

format_parameters()