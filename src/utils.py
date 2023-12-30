from glob import glob


def get_js_file(ts_filepath: str):
    if ts_filepath:
        js_glob_path = "public" + "/" + ts_filepath.replace(".ts", ".*.js")
        return glob(js_glob_path)[0]
    raise ValueError("Must provide ts_filepath relative to templates/views directory")
