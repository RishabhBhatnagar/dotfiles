import os.path
import pathlib
import sys

from main import create_config_files
from src import cache_manager, parser
from src.utils import get_cache_file_path, get_in_config_path, \
    get_out_config_path, Constants


def main():
    if len(sys.argv) < 2:
        raise ValueError("Expected a path to the out-dir")
    out_dir = os.path.abspath(sys.argv[1])

    cache_path = get_cache_file_path(out_dir)
    assert pathlib.Path(cache_path).exists()

    cache = cache_manager.read_cache(cache_path)

    repo_path = os.path.abspath(cache[Constants.FIELD_NAME_repo_path])
    assert os.path.exists(repo_path)

    config_input_dir = get_in_config_path(repo_path)
    config_output_dir = get_out_config_path(out_dir)
    create_config_files(config_input_dir, config_output_dir, out_dir)
    parser.parse_config_files(config_output_dir, out_dir)


if __name__ == '__main__':
    main()
