import json
import os
import sys

import pyfiglet


def info(file_path="data/json/info.json"):
    with open(file_path, "r") as file:
        return json.load(file)


def app_banner(app_name: str) -> str:
    return pyfiglet.figlet_format(app_name, font="slant")


def title(app_info: dict):
    banner = app_banner(app_info["title"])
    print(banner.center(80))


def cmd(app_info: dict):
    title_text = f"{app_info['title']} by @{app_info['publisher']['contact']['telegram'][13:]}"
    if os.name == 'nt':
        os.system(f"title {title_text}")
    else:
        sys.stdout.write(f"\x1b]2;{title_text}\x07")
