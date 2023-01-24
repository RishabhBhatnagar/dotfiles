import logging
import os
import pathlib
from logging import getLogger

from src import cache_manager
from src import parser
from src.utils import Constants, get_cache_file_path, get_out_config_path, \
    get_in_config_path, get_requirement, create_config_files

logging.basicConfig(level=logging.DEBUG)
logger = getLogger(__file__)


def get_previous_cache(cache_file_path):
    with open(cache_file_path, 'r') as fh:
        return eval(fh.read())


def fix_path(path, base_path=None):
    """
    file paths could be absolute or relative.
    if the path is a relative one, it must be prefixed with the base_path
    """
    if base_path is None or os.path.isabs(path):
        return path
    return os.path.join(base_path, path)


def get_out_dir(from_cache=True, cache_file_path=None, base_path=None):
    if from_cache and cache_file_path is not None:
        return fix_path(cache_manager.read_cache(cache_file_path)[
                            Constants.FIELD_NAME_out_dir], base_path)

    out_dir = get_requirement(
        Constants.FIELD_NAME_out_dir,
        Constants.DESCRIPTION_out_dir,
        cacheable=False,
        from_cache=from_cache,
        out_dir=None
    )
    out_dir = os.path.expanduser(out_dir)
    return pathlib.Path(fix_path(out_dir, base_path))


def prepare_out_dir(base_path):
    """Create the directory where all the output files will be written"""
    # create out_dir if it doesn't exist
    out_dir_path = get_out_dir(from_cache=False, base_path=base_path)
    out_dir_path.mkdir(exist_ok=True, parents=True)
    cache_manager.write_to_cache(Constants.FIELD_NAME_out_dir,
                                 out_dir_path.__str__(),
                                 get_cache_file_path(out_dir_path))
    return fix_path(out_dir_path, base_path)


def setup_new(base_path):
    """
    curr_path (string): path where all the scripts and config_templates are stored
    """
    out_dir_path = prepare_out_dir(base_path)

    # write repository path to the cache
    cache_manager.write_to_cache(
        Constants.FIELD_NAME_repo_path,
        base_path,
        get_cache_file_path(out_dir_path)
    )

    config_input_dir = get_in_config_path(base_path)
    config_output_dir = get_out_config_path(out_dir_path)
    pathlib.Path(config_output_dir).mkdir(parents=True, exist_ok=True)
    create_config_files(config_input_dir, config_output_dir, out_dir_path)
    return out_dir_path


def main():
    curr_dir_path = os.path.dirname(os.path.abspath(__file__))
    out_dir = setup_new(curr_dir_path)
    parser.parse_config_files(config_dir_path=get_out_config_path(out_dir),
                              out_dir=out_dir)
    logger.info("parsed the config files successfully")


if __name__ == '__main__':
    main()
