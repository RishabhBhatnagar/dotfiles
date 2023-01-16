"""
parser package is responsible for providing functions to understand and consume
directions given via config files

When we are given the config files,there are two types of statements:
  1. One that needs to be set everytime a cmd instance is created.
        For example: bash alias. It resets with every instance.
  2. Config that is persistent.
        For example: git alias. Once set, it will stay as it is even with the
                     new terminal instance.
"""
import abc
import os.path

import yaml

from src.utils import Platform, get_platform, Constants


class Processor(abc.ABC):
    def process_git_config(self, git_config):
        pass

    def process_shell_config(self, shell_config):
        pass


class WindowsProcessor(Processor):
    def process_git_config(self, git_config):
        pass

    def process_shell_config(self, shell_config):
        pass


class NixProcessor(Processor):
    def process_git_config(self, get_config):
        pass

    def process_shell_config(self, shell_config):
        pass


class ProcessorFactory:
    @staticmethod
    def get() -> Processor:
        if get_platform() == Platform.Windows:
            return WindowsProcessor()
        return NixProcessor()


def parse_config_files(config_dir_path: str, out_dir: str):
    """
    Impure method that reads all the config files and delegates work of parsing
    those read files. This also sets the necessary shortcuts and things in
    place for the config to work.
    :param config_dir_path: file path where all the config files are stored
    :param out_dir: file path where the temp or external build &
                             config files will be stored.
    """
    processor = ProcessorFactory.get()
    with open(os.path.join(config_dir_path, Constants.PATH_OUTPUT_shell_config_fname)) as fh:
        shell_config = yaml.safe_load(fh.read())

    with open(os.path.join(config_dir_path, Constants.PATH_OUTPUT_git_config_fname)) as fh:
        git_config = yaml.safe_load(fh.read())

    processor.process_git_config(git_config)
    processor.process_shell_config(shell_config)
