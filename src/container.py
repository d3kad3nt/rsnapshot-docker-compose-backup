from typing import NoReturn

import os
from config import ContainerConfig


class Container:
    folder: str
    name: str
    config: ContainerConfig

    def __init__(self, folder: str, name: str = None):
        self.folder = folder
        if name:
            self.name = name
        else:
            self.name = os.path.basename(os.path.normpath(folder))
        self._read_config()

    def _read_config(self) -> NoReturn:
        file_name = os.path.join(self.folder, "backup.ini")
        self.config = ContainerConfig(file_name, self.name)

    def backup(self) -> NoReturn:
        print(f"backup\t{self.folder}/docker-compose.yml\tdocker/{self.name}")
        self.config.output()
        print("\n")
