import os
from pathlib import Path

folder: Path = Path(os.getcwd())
config_file: Path | None = None


def set_folder(path: Path) -> None:
    # pylint: disable=global-statement
    global folder  # noqa: PLW0603
    folder = path


def set_config_file(file: Path | None) -> None:
    # pylint: disable=global-statement
    global config_file  # noqa: PLW0603
    config_file = file
