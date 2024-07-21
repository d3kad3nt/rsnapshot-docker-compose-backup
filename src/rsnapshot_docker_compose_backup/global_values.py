import os
from pathlib import Path
from typing import Optional


folder: Path = Path(os.getcwd())
config_file: Optional[Path] = None


def set_folder(path: Path) -> None:
    # pylint: disable=global-statement
    global folder
    folder = path


def set_config_file(file: Optional[Path]) -> None:
    # pylint: disable=global-statement
    global config_file
    config_file = file
