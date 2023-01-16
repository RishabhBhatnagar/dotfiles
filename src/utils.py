import enum
import platform


class Constants:
    FIELD_NAME_required_vars = 'required_vars'
    FIELD_NAME_out_dir = 'out_dir'
    FIELD_NAME_platform_windows = 'windows'

    PATH_INPUT_config_dir_name = 'config_template'
    PATH_OUTPUT_config_dir_name = 'config'
    PATH_OUTPUT_git_config_fname = 'git.yaml'
    PATH_OUTPUT_shell_config_fname = 'shell.yaml'
    PATH_OUTPUT_cache_file_name = '.secrets'

    DESCRIPTION_out_dir = 'directory path where all the config files will be stored'


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
