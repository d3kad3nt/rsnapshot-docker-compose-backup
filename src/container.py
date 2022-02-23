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

    def __init__(self, folder: str, name: str, container_id: str):
        self.folder = folder
        self.name = name
        self.container_id = container_id
        self.project_name = os.path.basename(folder)
        self.image = docker.image(container_id)
        self.file_name = os.path.join(self.folder, "backup.ini")
        self.volumes = docker.volumes(container_id)
        self.config = ContainerConfig(self)

    def backup(self) -> NoReturn:
        print("#Start {}".format(self.name))
        self.config.output()
        print("\n")

    def __str__(self):
        return "Container {} in folder {}".format(self.name, self.folder)

    def __repr__(self):
        return "Container {} in folder {}".format(self.name, self.folder)
