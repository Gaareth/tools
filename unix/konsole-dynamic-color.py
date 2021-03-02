# color:#383c4a;opacity:0.83;fill:#161925
import re
import argparse
import os
import sys
from collections import defaultdict
import random
import configparser

COLOR_SCHEME_DIRECTORY = f'{os.path.expanduser("~")}/.local/share/konsole/'
DYNAMIC_COLOR_SCHEME = f'{COLOR_SCHEME_DIRECTORY}dynamic-colors.colorscheme'
KONSOLERC = f'{os.path.expanduser("~")}/.config/konsolerc'
KWINRC = f'{os.path.expanduser("~")}/.config/kwinrc'


agree_options = ["yes", "y"]
disagree_options = ["no", "n"]

# TODO: replacing and splitting might not be the right way to manipulate the data. Maybe change to configparser


def hex_to_rgb(hex):
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


def replace_value(key, new_value, data):
    old_value = data.split(f"{key}")[1].split('=')[1].split("\n")[0]
    return re.sub(fr'{key}\s?=\s?{old_value}', f"{key}={new_value}", data)


def set_default_profile(profile_name):
    with open(KONSOLERC, "r") as f:
        data = f.read()
    data = replace_value("DefaultProfile", profile_name, data)
    with open(KONSOLERC, "w") as f:
        f.write(data)


def get_aurorae_theme():
    config = configparser.ConfigParser()
    config.read_file(open(KWINRC))
    return config['org.kde.kdecoration2']['theme'].split("__aurorae__svg__")[1]


def extract_color(theme_name, auto):
    theme_path = f'{os.path.expanduser("~")}/.local/share/aurorae/themes/{theme_name}/decoration.svg'
    if not os.path.isfile(theme_path):
        print(f"The theme '{theme_name}' could not be found! \n"
              f"Please check if a file named '{theme_path}' exists.")
        sys.exit(-1)

    with open(theme_path, "r") as f:
        data = f.read()

    pattern = r'opacity:\d.?\d{0,2};fill:#.{4,6}' if auto \
        else r'opacity:\d.?\d{0,2};?fill:#.{4,6};?|fill:#.{4,6};?fill-opacity:\d.?\d{0,2};?'
    matches = re.findall(pattern, data)

    found_opacity = matches[0].split("opacity:")[1].split(";")[0]

    found_colors = defaultdict(int)
    for match in matches:
        fill_color = match.split("fill:")[1].lstrip("#").split(";")[0]
        found_colors[fill_color] += 1
    # list(sorted(found_colors.items()))
    # print((sorted(found_colors.items(), key=lambda x: x[1],reverse=True)))
    found_colors = [c for c, t in list(sorted(found_colors.items(), key=lambda x: x[1], reverse=True))]

    return found_colors, found_opacity


def dynamic_color(theme_name=None, forced_opacity=None, auto=True):
    if theme_name is None:
        theme_name = get_aurorae_theme()

    found_colors, found_opacity = extract_color(theme_name, auto)
    fill_color = found_colors[0]
    opacity = forced_opacity or found_opacity

    if len(found_colors) > 1 and not auto:
        print(f"Multiple colors found: {[(c, i + 1) for i, c in enumerate(found_colors)]}")
        while True:
            print(f"Please specify a number between [1-{len(found_colors)}] "
                  f"(eg: '1' or '{random.randint(2, len(found_colors))}')")
            chosen_color = input("> ")

            if chosen_color in [str(i) for i in range(1, len(found_colors) + 1)]:
                break

        fill_color = list(found_colors)[int(chosen_color) - 1]
        print(f"> Chosen color: {fill_color}")

    if not os.path.isfile(DYNAMIC_COLOR_SCHEME):
        print(f"[!] The theme dynamic colorscheme file ({DYNAMIC_COLOR_SCHEME})could not be found [!]")

        while True:
            print("[?] Do you want to create a colorscheme file from a base file [?] \n(y/N)")
            create_base_scheme = input("> ")

            if create_base_scheme.lower() in agree_options:
                print("Please specify a base colorscheme file (Only the name)")

                base_color_scheme = input("> ")
                base_color_scheme_file_location = os.path.join(
                    f"{COLOR_SCHEME_DIRECTORY}", f"{base_color_scheme}.colorscheme"
                )
                if os.path.isfile(base_color_scheme_file_location):
                    base_color_scheme_file = open(base_color_scheme_file_location, "r")
                    base_color_data = base_color_scheme_file.read()
                    base_color_scheme_file.close()
                    base_color_data = replace_value("Description", "dynamic-colors", base_color_data)

                    with open(DYNAMIC_COLOR_SCHEME, "w") as f:
                        f.write(base_color_data)
                    print("> Successfully created dynamic colorscheme file!")
                    break

                else:
                    print(f"[!]Invalid colorscheme name[!]\n"
                          f"Could not find the file '{base_color_scheme}' in '{COLOR_SCHEME_DIRECTORY}'\n")

            else:
                sys.exit(-1)

    with open(DYNAMIC_COLOR_SCHEME, "r") as f:
        data = f.read()

    current_color = data.split("[Background]\nColor=")[1].split("\n")[0]
    new_color = str(hex_to_rgb(fill_color))[1:-1]

    print(f"Opacity: {opacity}")
    print(f"New color: {new_color} (#{fill_color})")

    data = data.replace(current_color, new_color)
    data = replace_value("Opacity", opacity, data)

    with open(DYNAMIC_COLOR_SCHEME, "w") as f:
        f.write(data)

    print("> Updated colorscheme")


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="The name of the aurorae theme which provides the base color. "
                                       "Automatically detects current theme if not specified.")
    parser.add_argument("-o", "--opacity", help="Force a specific opacity")
    parser.add_argument("--set_as_default", help="Set the dynamic profile as default", type=str2bool, default=True)
    parser.add_argument("-a", "--auto", help="Automatically chose the color of the titlebar. "
                                             "Disable if it produces the wrong results",
                        type=str2bool, default=True, nargs='?')

    # parser.add_argument("-r", "--restart", help="Restart konsole (Only works for kde konsole)")

    args = parser.parse_args()
    # print(args)

    dynamic_color(args.name, args.opacity, args.auto)
    if args.set_as_default:
        set_default_profile("Dynamic.profile")
    # if args.restart:
