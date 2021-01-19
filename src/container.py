from typing import NoReturn, List

import os

from src import docker
from src.ContainerConfig import ContainerConfig
from src.volume import Volume


class Container:
    folder: str
    name: str
    config: ContainerConfig
    volumes: List[Volume]

    def __init__(self, folder: str, name: str):
        self.folder = folder
        self.name = name
        self.file_name = os.path.join(self.folder, "backup.ini")
        self.volumes = docker.volumes(name)
        self.config = ContainerConfig(self)

    def backup(self) -> NoReturn:
        print("#{}".format(self.name))
        print(f"backup\t{self.folder}/docker-compose.yml\tdocker/{self.name}")
        self.config.output()
        print("\n")

    def __str__(self):
        return "Container {} in folder {}".format(self.name, self.folder)

    def __repr__(self):
        return "Container {} in folder {}".format(self.name, self.folder)
