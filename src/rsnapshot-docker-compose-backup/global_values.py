folder: str
config_file: str


def set_folder(path: str) -> None:
    global folder
    folder = path


def set_config_file(file: str) -> None:
    global config_file
    config_file = file
