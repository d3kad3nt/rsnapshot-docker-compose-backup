from typing import NoReturn

import os
from src.ContainerConfig import ContainerConfig


class Container:
    folder: str
    name: str
    config: ContainerConfig

    def __init__(self, folder: str, name: str):
        self.folder = folder
        self.name = name
        self._read_config()

    def _read_config(self) -> NoReturn:
        file_name = os.path.join(self.folder, "backup.ini")
        self.config = ContainerConfig(file_name, self.name)

    def backup(self) -> NoReturn:
        print(f"backup\t{self.folder}/docker-compose.yml\tdocker/{self.name}")
        self.config.output()
        print("\n")

    def __str__(self):
        return "Container {} in folder {}".format(self.name, self.folder)

    def __repr__(self):
        return "Container {} in folder {}".format(self.name, self.folder)
