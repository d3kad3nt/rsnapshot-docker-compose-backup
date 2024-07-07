from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

from rsnapshot_docker_compose_backup.structure.container import Container
from rsnapshot_docker_compose_backup.structure.volume import Volume
from rsnapshot_docker_compose_backup.utils.docker_api_client import Api


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
    name: str
    image: str
    image_id: str
    state: ContainerState
    mounts: List[DockerMount]
    labels: Dict[str, str]

    @staticmethod
    def from_json(json_data: Any) -> "DockerInspect":

        if "Names" in json_data:  # /containers/json format
            if len(json_data["Names"]) > 1:
                raise ValueError("Container has more than one name: " + json_data)
            name = json_data["Names"][0]
            image = json_data["Image"]
            image_id = json_data["ImageID"]
            state = ContainerState.from_str(json_data["State"])
            labels = json_data["Labels"]
        else:  # /containers/{id}/json format
            name = json_data["Name"]
            image_id = json_data["Image"]
            image = json_data["Config"]["Image"]
            state = ContainerState.from_str(json_data["State"]["Status"])
            labels = json_data["Config"]["Labels"]
        return DockerInspect(
            id=json_data["Id"],
            name=name[1:],
            image=image,
            image_id=image_id,
            state=state,
            mounts=[DockerMount.from_json(x) for x in json_data["Mounts"]],
            labels=labels,
        )


def inspect_container(
    container_id: str, socket_connection: Optional[str] = None
) -> DockerInspect:
    if socket_connection is None:
        api = Api()
    else:
        api = Api(socket_connection=socket_connection)
    response = api.get(f"/containers/{container_id}/json")
    return DockerInspect.from_json(response.json_body)


def get_container(socket_connection: Optional[str] = None) -> List[DockerInspect]:
    parameter = {"all": "true"}
    if socket_connection is None:
        api = Api()
    else:
        api = Api(socket_connection=socket_connection)
    response = api.get("/containers/json", query_parameter=parameter)
    return [DockerInspect.from_json(x) for x in response.json_body]


def _volumes(mounts: List[DockerMount]) -> List[Volume]:
    result: List[Volume] = []
    for mount in mounts:
        if mount.type == DockerMountType.VOLUME:
            assert mount.name is not None
            result.append(Volume(mount.name, mount.source))
    return sorted(result)


def get_compose_container() -> List[Container]:
    container_list: List[Container] = []
    for container in get_container():
        if "com.docker.compose.project" in container.labels:
            container_list.append(
                Container(
                    folder=Path(
                        container.labels["com.docker.compose.project.working_dir"]
                    ),
                    container_id=container.id,
                    container_name=container.name,
                    running=container.state != ContainerState.EXITED,
                    service_name=container.labels["com.docker.compose.service"],
                    volumes=_volumes(container.mounts),
                    image=container.image,
                    docker_compose_file=Path(
                        container.labels["com.docker.compose.project.config_files"]
                    ),  # TODO check if this can be multiple files
                )
            )
    return sorted(container_list)
