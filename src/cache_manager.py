import pathlib


def read_cache(cache_file_path):
    create_cache_if_not_exists(cache_file_path)
    with open(cache_file_path, 'r') as fh:
        return eval(fh.read())


def create_cache_if_not_exists(cache_file_path):
    if pathlib.Path(cache_file_path).exists():
        return
    with open(cache_file_path, 'w') as fh:
        fh.write('{}')


def _overwrite_cache(curr_cache, cache_file_path):
    with open(cache_file_path, 'w') as fh:
        fh.write(curr_cache.__str__())


def write_to_cache(key, value, cache_file_path):
    create_cache_if_not_exists(cache_file_path)
    curr_cache = read_cache(cache_file_path)
    curr_cache[key] = value
    _overwrite_cache(curr_cache, cache_file_path)
