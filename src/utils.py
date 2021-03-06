import json
import os
import math


def printable(value):
    """ Returns value approximation that fits in 6 characters """

    if value > 10000:
        return "10^" + str(int(math.log(value) / math.log(10)))

    elif value > 100:
        return str(int(value))

    elif value > 0 and value < 0.001:
        return "10^-" + str(int(math.log(1 / value) / math.log(10)))

    else:
        return f"{value:.2f}"


def format_parameters():
    """ Modifies all parameter files at the same time """
    dir = "./parameters"
    files = [
        dir + "/" + x for x in os.listdir(dir) if os.path.isfile(os.path.join(dir, x))
    ]
    for file in files:
        if file[-5:] == ".json":
            print("Opening " + file)

            with open(file, "r") as outfile:
                json_data = json.load(outfile)

            ### your modification here : ###

            # for example we'll change names from camelCase to snake_case
            old_names = [
                "formulaRed",
                "formulaGreen",
                "formulaBlue",
                "colorMode",
                "randomModulation",
                "sValue",
                "vValue",
                "bwScale",
                "rgbScale",
            ]

            new_names = [
                "formula_red",
                "formula_green",
                "formula_blue",
                "color_model",
                "random_modulation",
                "s_value",
                "v_value",
                "bw_scale",
                "rgb_scale",
            ]

            dicts = [json_data, json_data["menu_parameters"]]
            for json_dict in dicts:
                for i in range(len(old_names)):
                    if old_names[i] in json_dict.keys():
                        json_dict[new_names[i]] = json_dict[old_names[i]]
                        del json_dict[old_names[i]]

            ### end of modification ###

            with open(file, "w") as outfile:
                json.dump(json_data, outfile, sort_keys=True, indent=4)
