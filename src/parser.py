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
import logging
import os.path

import yaml

from src.utils import Platform, get_platform, Constants


class Processor(abc.ABC):
    def process_git_config(self, git_config: dict):
        pass

    def process_shell_config(self, shell_config, out_dir):
        pass


class NixProcessor(Processor):
    def process_git_config(self, git_config):
        """
        Git config is a one time run thing. Once set, it will stay as-is with
        every new terminal instance
        """
        def _generate_git_stmts():
            for scope, section_vars in git_config.items():
                for section, git_alias in section_vars.items():
                    for abbrev, cmd in git_alias.items():
                        cmd = cmd.replace('"', '\\"')
                        scope_option = '--' + scope if scope else ''
                        yield f'git config {scope_option} {section}.{abbrev} "{cmd}"'

        for stmt in _generate_git_stmts():
            logging.debug(f'running: {stmt}')
            os.system(stmt)

    def process_shell_config(self, shell_config, out_dir):
        pass


class WindowsProcessor(Processor):
    process_git_config = NixProcessor.process_git_config

    def process_shell_config(self, shell_config, out_dir):
        def _get_win_specific_aliases(win_cfg):
            win_cfg = shell_config.get('windows', {})
            if not win_cfg or not win_cfg.get('alias'):
                # nothing to be processed
                logging.debug("got a null win alias config")
                return {}
            return win_cfg.get('alias')

        general_aliases = shell_config.get('alias', {})
        win_specific_aliases = _get_win_specific_aliases(shell_config)
        all_aliases = general_aliases
        all_aliases.update(win_specific_aliases)
        for key, cmd in all_aliases.items():
            with open(os.path.join(out_dir, key + '.bat'), 'w') as fh:
                fh.write(cmd)
        set_path_cmd = f'setx path "%PATH%;{out_dir}"'
        logging.debug('adding out_dir to cmd using following command: ' + set_path_cmd)
        os.system(set_path_cmd)


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
    processor.process_shell_config(shell_config, out_dir)
