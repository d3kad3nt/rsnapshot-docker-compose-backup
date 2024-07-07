from pathlib import Path
from typing import List

import os

from rsnapshot_docker_compose_backup.config.container_config import ContainerConfig
from rsnapshot_docker_compose_backup.structure.volume import Volume


class Container:

    def __init__(
        self,
        *,
        folder: Path,
        service_name: str,
        container_name: str,
        container_id: str,
        running: bool,
        volumes: List[Volume],
        image: str,
        docker_compose_file: Path,
    ):
        self.folder: Path = folder
        self.service_name = service_name
        self.container_name = container_name
        self.container_id = container_id
        self.project_name = os.path.basename(folder)
        self.image = image
        self.backup_config: Path = self.folder / "backup.ini"
        self.volumes = volumes
        self.is_running = running
        self.docker_compose_file: Path = docker_compose_file

    def backup(self) -> str:
        result: List[str] = []
        config = ContainerConfig(
            {
                "$serviceName": self.service_name,
                "$containerID": self.container_id,
                "$containerName": self.container_name,
                "$projectFolder": str(self.folder),
                "$volumes": self.volumes,
                "$image": self.image,
                "$projectName": self.project_name,
                "$dockerComposeFile": str(self.docker_compose_file),
            },
            is_running=self.is_running,
            service_name=self.service_name,
            config_file=self.backup_config,
        )
        output = config.output()
        if output is None:
            # print("output is none")
            return ""
        result.append(
            "##Start backup for compose project {} - service {}".format(
                self.project_name, self.service_name
            )
        )
        result.append(output)
        result.append(
            "##End backup for compose project {} - service {}".format(
                self.project_name, self.service_name
            )
        )
        result.append("")
        return "\n".join(result)

    def __str__(self) -> str:
        return "Container {} in folder {}".format(self.service_name, self.folder)

    def __repr__(self) -> str:
        return "Container {} in folder {}".format(self.service_name, self.folder)

    def __lt__(self, other: "Container") -> bool:
        if self.project_name != other.project_name:
            return self.project_name < other.project_name
        return self.service_name < other.service_name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Container):
            return False
        if self.backup_config != other.backup_config:
            return False
        if self.container_id != other.container_id:
            return False
        if self.container_name != other.container_name:
            return False
        if self.docker_compose_file != other.docker_compose_file:
            return False
        if self.folder != other.folder:
            return False
        if self.image != other.image:
            return False
        if self.is_running != other.is_running:
            return False
        if self.project_name != other.project_name:
            return False
        if self.service_name != other.service_name:
            return False
        if self.volumes != other.volumes:
            return False
        return True
