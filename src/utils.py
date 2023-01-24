import enum
import os
import platform
from functools import reduce
from typing import Iterable

from src import cache_manager


class Constants:
    POSSIBLE_RC_FILENAMES = ['.zshrc', '.bashrc']

    FIELD_NAME_required_vars = 'required_vars'
    FIELD_NAME_out_dir = 'out_dir'
    FIELD_NAME_platform_windows = 'windows'
    FIELD_NAME_rc_path = 'rc_path'
    FIELD_NAME_repo_path = 'repository_path'

    PATH_INPUT_config_dir_name = 'config_template'
    PATH_OUTPUT_config_dir_name = 'config'
    PATH_OUTPUT_git_config_fname = 'git.yaml'
    PATH_OUTPUT_shell_config_fname = 'shell.yaml'
    PATH_OUTPUT_cache_file_name = '.secrets'
    PATH_OUTPUT_main_config = 'main.sh'

    DESCRIPTION_out_dir = 'directory path where all the config files will be stored'
    DESCRIPTION_rc_file = 'path of the rc file (~/.bashrc for example)'


class Platform(enum.Enum):
    Windows = enum.auto()
    Linux = enum.auto()
    Mac = enum.auto()


def get_platform():
    system = platform.system().lower()
    if system.__eq__('darwin'):
        return Platform.Mac
    elif system.__eq__('windows'):
        return Platform.Windows
    else:
        return Platform.Linux


class TextMode(enum.Enum):
    NORMAL = 0
    BOLD = 1
    ITALIC = 3
    UNDERLINE = 4


def _set_mode(text: str, mode: TextMode):
    assert isinstance(mode, TextMode)
    return f'\033[{mode.value}m{text}\033[0m'


def format_text(modes: Iterable[TextMode], text: str) -> str:
    return reduce(_set_mode, modes, text)


def get_cache_file_path(out_dir):
    return os.path.join(out_dir, Constants.PATH_OUTPUT_cache_file_name)


def get_out_config_path(out_dir_path):
    return os.path.join(out_dir_path, Constants.PATH_OUTPUT_config_dir_name)


def get_in_config_path(repo_path):
    return os.path.join(repo_path, Constants.PATH_INPUT_config_dir_name)


def get_requirement(key, description, cacheable, from_cache, out_dir):
    if from_cache and key in (
            cache := cache_manager.read_cache(get_cache_file_path(out_dir))):
        return cache[key]
    val = input(f"Please enter {description}: ")
    if cacheable:
        cache_manager.write_to_cache(key, val, get_cache_file_path(out_dir))
    return val
