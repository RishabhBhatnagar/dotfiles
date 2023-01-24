import enum
import os
import pathlib
import platform
from functools import reduce
from typing import Iterable

import yaml

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
    Windows = 'windows'
    Linux = 'nix'
    Mac = 'mac'


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


def fetch_requirements(requirement_config: dict, out_dir):
    out = {}
    for key, requirement in requirement_config.items():
        out[key] = get_requirement(key, requirement['description'],
                                   requirement.get('cacheable'),
                                   requirement.get('from_cache'), out_dir)
    return out


def format_requirements(yaml_config: dict, requirements: dict) -> str:
    """
    Given a yaml config, fill unfilled keys with values with the details
    provided by the requirements dict
    """
    dup_yaml_config = yaml_config.copy()
    dup_yaml_config.pop(Constants.FIELD_NAME_required_vars, None)
    _filter_yaml_config(dup_yaml_config)
    return yaml.safe_dump(dup_yaml_config).format(**requirements)


def _filter_yaml_config(yaml_config: dict):
    # filter the yaml config to have settings pertaining to the current OS only
    curr_platform = get_platform()
    other_platforms = [p for p in Platform if p != curr_platform]
    nix_platforms = {Platform.Linux, Platform.Mac}
    if curr_platform in nix_platforms:
        other_platforms = [p for p in other_platforms if p not in nix_platforms]
    for p in other_platforms:
        yaml_config.pop(p.value, None)


def parse_config_file_content(file_content: str, out_dir) -> str:
    config = yaml.safe_load(file_content)
    required_vars: dict = config.get(Constants.FIELD_NAME_required_vars, {})
    req = fetch_requirements(required_vars, out_dir)
    return format_requirements(config, req)


def create_config_files(config_input_dir, config_output_dir, out_dir_path):
    """
    config_input_dir: directory path where all the input config template files are stored
    config_output_dir: directory path where all the filled config files will be stored
    out_dir_path: working directory path where all the out files can be written by the program
    """

    def _get_config_fnames(dir_path):
        """All the yaml in the config directory path are the config files"""
        return filter(lambda fname: fname.endswith('.yaml'),
                      os.listdir(dir_path))

    pathlib.Path(config_output_dir).mkdir(exist_ok=True)

    for file_name in _get_config_fnames(config_input_dir):
        config_in_file_path = os.path.join(config_input_dir, file_name)
        config_out_file_path = os.path.join(config_output_dir, file_name)

        # reading the config file and filling the required params
        with open(config_in_file_path) as fh:
            parsed_file_content = parse_config_file_content(fh.read(),
                                                            out_dir_path.__str__())

        # (?over)writing the parsed content to the output directory
        with open(config_out_file_path, 'w') as fh:
            fh.write(parsed_file_content)
