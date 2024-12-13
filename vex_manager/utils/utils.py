import hou

import os
import re


def is_valid_file_name(file_name: str) -> bool:
    pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
    match = re.match(pattern, file_name)

    return bool(match)


def get_settings_path() -> str:
    home_path = os.path.expandvars('$HOME')
    houdini_version = hou.applicationVersionString()
    major, minor, patch = houdini_version.split('.')
    houdini_folder_path = os.path.join(home_path, f'houdini{major}.{minor}')

    settings_path = os.path.join(houdini_folder_path, 'vexmanager.json')

    return settings_path
