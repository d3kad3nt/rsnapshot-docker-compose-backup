folder: str
config_file: str


def set_folder(path: str) -> None:
    # pylint: disable=global-statement
    global folder
    folder = path


def set_config_file(file: str) -> None:
    # pylint: disable=global-statement
    global config_file
    config_file = file
