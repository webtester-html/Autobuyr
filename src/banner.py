import json
import os
import sys
from importlib import import_module

import pyfiglet


def info(file_path="data/json/info.json"):
    with open(file_path, "r") as file:
        return json.load(file)


def app_banner(app_name: str) -> str:
    return pyfiglet.figlet_format(app_name, font="slant")


def title(app_info: dict, language: str):
    banner = app_banner(app_info["title"])

    separator = "-" * 80
    description = f"Language: \033[1m{language}\033[0m | Build \033[92mv{app_info['version']}\033[0m | TG: @{app_info['publisher']['contact']['channel'][13:]}"

    banner_lines = banner.splitlines()
    centered_banner = "\n".join([line.center(80) for line in banner_lines])

    print(separator)
    print(centered_banner)
    print(separator)
    print(f"{description}".center(95))
    print(separator)


def cmd(app_info: dict):
    title_text = f"{app_info['title']} by @{app_info['publisher']['contact']['telegram'][13:]}"
    if os.name == 'nt':
        os.system(f"title {title_text}")
    else:
        sys.stdout.write(f"\x1b]2;{title_text}\x07")


def get_locale(lang: str):
    # Default to English if language code is not found
    if not lang:
        lang = 'EN'

    try:
        locale_module = import_module(f'locales.{lang.lower()}')
        return locale_module.LANG[3:], locale_module.CODE
    except ModuleNotFoundError:
        # print(f"\033[91m[ERROR]\033[0mLocale {language_code} not found, falling back to English.")
        locale_module = import_module('locales.en')
        return locale_module.LANG[3:], locale_module.CODE
