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
import pathlib

import yaml

from src.utils import Platform, get_platform, Constants, TextMode, \
    format_text, get_requirement


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
        def _generate_shell_stmt():
            for abbr, cmd in all_aliases.items():
                cmd = cmd.replace('"', '\\"')
                yield f'alias {abbr}="{cmd}"'

        def _add_file_to_rc(cmd):
            def _detect_rc_file():
                home_dir = pathlib.Path('~').expanduser()
                rc_file_names = Constants.POSSIBLE_RC_FILENAMES
                detected_path = None
                for fname in rc_file_names:
                    if (curr_rc_fname := home_dir.joinpath(fname)).exists():
                        logging.debug("found a rc file: " + str(curr_rc_fname))
                        detected_path = str(curr_rc_fname.absolute())
                        break
                if detected_path is None:
                    return None

                # confirm from user if the detected rc file path is correct
                print(format_text([TextMode.BOLD], detected_path),
                      'is the detected path of rc file')
                choice = get_requirement('confirmation_rc_path',
                                         'y if you want to change the rc file path (any other key to continue)',
                                         False, False, out_dir)
                if choice.lower() == 'y':
                    return None
                return detected_path

            def _get_rc_file_path():
                rc_file_path = _detect_rc_file()
                if rc_file_path is None:
                    rc_file_path = get_requirement(Constants.FIELD_NAME_rc_path,
                                                   Constants.DESCRIPTION_rc_file,
                                                   True, False,
                                                   out_dir)
                return os.path.realpath(os.path.expanduser(rc_file_path))

            rc_file_path = _get_rc_file_path()
            # create the rc file if it doesn't exist
            pathlib.Path(rc_file_path).touch()

            # return if the command is already in the rc file
            with open(rc_file_path) as fh:
                if cmd in fh.read().split('\n'):
                    logging.debug(
                        "Command already found in the current rc file")
                    return

            # cmd is not present in the rc file
            logging.debug("The command was not found in the rc file. Adding it")
            with open(rc_file_path, 'a') as fh:
                fh.write(f'\n{cmd}\n')

        general_alias = shell_config.get('alias', {})
        nix_alias = shell_config.get('nix', {}).get('alias', {})
        all_aliases = {**general_alias, **nix_alias}

        out_file_path = os.path.join(out_dir, Constants.PATH_OUTPUT_main_config)
        with open(out_file_path, 'w') as fh:
            fh.write('\n'.join(_generate_shell_stmt()))
        logging.info(
            f'created a file {format_text([TextMode.BOLD], out_file_path)} that stores all the remaining config')

        cmd = f'. {out_file_path}'
        _add_file_to_rc(cmd)
        logging.info("Output config file: " + format_text(
            [TextMode.BOLD, TextMode.ITALIC, TextMode.UNDERLINE],
            out_file_path))


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
        all_aliases = {**general_aliases, **win_specific_aliases}
        for key, cmd in all_aliases.items():
            with open(os.path.join(out_dir, key + '.bat'), 'w') as fh:
                fh.write(cmd)
        set_path_cmd = f'setx path "%PATH%;{out_dir}"'
        logging.debug(
            'adding out_dir to cmd using following command: ' + set_path_cmd)
        os.system(set_path_cmd)


class ProcessorFactory:
    @staticmethod
    def get() -> Processor:
        if get_platform() == Platform.Windows:
            logging.debug("detected a \033[1mWindows\033[0;m system")
            return WindowsProcessor()
        logging.debug("detected a \033[1m*NIX\033[0;m system")
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
    with open(os.path.join(config_dir_path,
                           Constants.PATH_OUTPUT_shell_config_fname)) as fh:
        shell_config = yaml.safe_load(fh.read())

    with open(os.path.join(config_dir_path,
                           Constants.PATH_OUTPUT_git_config_fname)) as fh:
        print(os.path.join(config_dir_path,
                           Constants.PATH_OUTPUT_git_config_fname))
        git_config = yaml.safe_load(fh.read())

    processor.process_git_config(git_config)
    processor.process_shell_config(shell_config, out_dir)
