from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

from rsnapshot_docker_compose_backup.structure.container import Container
from rsnapshot_docker_compose_backup.structure.volume import Volume
from rsnapshot_docker_compose_backup.utils.dockerApiClient import Api


class ContainerState(Enum):
    CREATED = auto()
    RESTARTING = auto()
    RUNNING = auto()
    REMOVING = auto()
    PAUSED = auto()
    EXITED = auto()
    DEAD = auto()

    @staticmethod
    def from_str(value: str) -> "ContainerState":
        for member in ContainerState:
            if member.name.lower() == value.lower():
                return member
        raise ValueError("Unknown State: " + value)


class DockerMountType(Enum):
    VOLUME = auto()
    BIND = auto()
    NOT_SET = auto()

    @staticmethod
    def from_str(value: str) -> "DockerMountType":
        for member in DockerMountType:
            if member.name.lower() == value.lower():
                return member
        raise ValueError("Unknown Type: " + value)


@dataclass
class DockerMount:
    name: Optional[str]
    type: DockerMountType
    source: str
    destination: str
    driver: Optional[str]
    mode: str
    rw: bool
    propagation: str

    @staticmethod
    def from_json(json_data: Any) -> "DockerMount":
        if "Name" in json_data:
            name = json_data["Name"]
        else:
            name = None
        if "Driver" in json_data:
            driver = json_data["Driver"]
        else:
            driver = None
        if "Type" in json_data:
            mount_type = DockerMountType.from_str(json_data["Type"])
        else:
            mount_type = DockerMountType.NOT_SET
        return DockerMount(
            name=name,
            type=mount_type,
            source=json_data["Source"],
            destination=json_data["Destination"],
            driver=driver,
            mode=json_data["Mode"],
            rw=json_data["RW"],
            propagation=json_data["Propagation"],
        )


@dataclass
class DockerInspect:
    id: str
    names: list[str]
    image: str
    image_id: str
    state: ContainerState
    mounts: list[DockerMount]
    labels: dict[str, str]

    @staticmethod
    def from_json(json_data: Any) -> "DockerInspect":
        print(json_data["Names"])
        print(json_data["State"])
        return DockerInspect(
            id=json_data["Id"],
            names=[x.lstrip("/") for x in json_data["Names"]],
            image=json_data["Image"],
            image_id=json_data["ImageID"],
            state=ContainerState.from_str(json_data["State"]),
            mounts=[DockerMount.from_json(x) for x in json_data["Mounts"]],
            labels=json_data["Labels"],
        )


def inspect_container(container_id: str) -> DockerInspect:
    # converts docker inspect to json and return only first container,
    # because this works only with one container
    response = Api().get(f"/containers/{container_id}/json")
    return DockerInspect.from_json(response.json_body)


def get_container(socket_connection: Optional[str] = None) -> list[DockerInspect]:
    parameter = {"all": "true"}
    if socket_connection is None:
        api = Api()
    else:
        api = Api(socket_connection=socket_connection)
    response = api.get("/containers/json", query_parameter=parameter)
    return [DockerInspect.from_json(x) for x in response.json_body]


def _volumes(mounts: list[DockerMount]) -> list[Volume]:
    result: list[Volume] = []
    for mount in mounts:
        if mount.type == DockerMountType.VOLUME:
            assert mount.name is not None
            result.append(Volume(mount.name, mount.source))
    return sorted(result)


def get_compose_container() -> list[Container]:
    container_list: list[Container] = []
    for container in get_container():
        if "com.docker.compose.project" in container.labels:
            print(container.names[0])
            print(container.state)
            container_list.append(
                Container(
                    folder=Path(
                        container.labels["com.docker.compose.project.working_dir"]
                    ),
                    container_id=container.id,
                    container_name=container.names[0],  # TODO convert to list
                    running=container.state != ContainerState.EXITED,
                    service_name=container.labels["com.docker.compose.service"],
                    volumes=_volumes(container.mounts),
                    image=container.image,
                )
            )
    return sorted(container_list)
