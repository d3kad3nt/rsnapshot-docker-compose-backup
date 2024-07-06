from dataclasses import dataclass
from enum import Enum, auto
import json
from pathlib import Path
import socket
from typing import Any, Optional
import urllib.parse
from rsnapshot_docker_compose_backup.structure.container import Container
from rsnapshot_docker_compose_backup.structure.volume import Volume


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


def inspect(container_id: str) -> DockerInspect:
    # converts docker inspect to json and return only first container,
    # because this works only with one container
    response = Api().get(f"/containers/{container_id}/json")
    return DockerInspect.from_json(response.json_body)


def ps(socket_connection: Optional[str] = None) -> list[DockerInspect]:
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


@dataclass
class HttpResponse:
    protocol_version: str
    status_code: int
    status_text: str
    headers: dict[str, str]
    json_body: Any


class Api:

    _docker_socket: Optional[socket.socket] = None

    def __init__(
        self, socket_connection: str = "unix:///run/docker.sock", version: str = "v1.46"
    ) -> None:
        self.docker_socket = self._open_socket(socket_connection)
        self.version = version

    def _open_socket(self, socket_connection: str) -> socket.socket:
        if socket_connection.startswith("unix://"):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socket_connection.removeprefix("unix://"))
            return sock
        if socket_connection.startswith("http://"):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            parts = socket_connection.removeprefix("http://").split(":")
            host = parts[0]
            port = 80
            if len(parts) == 2:
                port = int(parts[1])
            print(f"connect to {host}, {port}")
            sock.connect((host, port))
            return sock
        raise ValueError("Only Unix and http Sockets are supported")

    def get(
        self,
        endpoint: str,
        *,
        query_parameter: Optional[dict[str, str]] = None,
        header: Optional[dict[str, str]] = None,
    ) -> HttpResponse:
        path = f"/{self.version}{endpoint}"
        if query_parameter is not None:
            parameter: list[str] = []
            for name, value in query_parameter.items():
                parameter.append(f"{name}={urllib.parse.quote_plus(value)}")
            path = path + "?" + "&".join(parameter)
        request = [
            f"GET {path} HTTP/1.1",
            "Host:docker.sock",
        ]
        if header is not None:
            for name, value in header.items():
                request.append(f"{name}:{value}")
        request.append("\r\n")
        self.docker_socket.send("\r\n".join(request).encode("utf-8"))
        return self._parse_response(self.docker_socket)

    @staticmethod
    def _parse_response(sock: socket.socket) -> HttpResponse:
        message_start = b""
        while not message_start.endswith(b"\r\n\r\n"):
            message_start = message_start + sock.recv(1)
        lines: list[str] = message_start.decode("utf-8").splitlines()
        status_line = lines[0]
        protocol_version = status_line.split(" ")[0]
        status_code = int(status_line.split(" ")[1])
        status_text = " ".join(status_line.split(" ")[2:])
        if status_code >= 400:
            raise ValueError(status_text)
        headers: dict[str, str] = {}
        for line in lines[1:]:
            split = line.split(":")
            if len(split) == 2:
                headers[split[0]] = split[1].strip()
        if "Content-Length" in headers:
            body_length = int(headers["Content-Length"])
            body = sock.recv(body_length).decode("utf-8")
        elif (
            "Transfer-Encoding" in headers and headers["Transfer-Encoding"] == "chunked"
        ):
            body = ""
            while True:
                chunk = b""
                while not chunk.endswith(b"\r\n"):
                    chunk += sock.recv(1)
                length = int(chunk.decode("utf-8"), 16)
                if length == 0:
                    break
                body = body + sock.recv(length).decode("utf-8")
                sock.recv(2)  # Skip ending \r\n
        else:
            raise ValueError(headers)
        return HttpResponse(
            protocol_version=protocol_version,
            status_code=status_code,
            status_text=status_text,
            headers=headers,
            json_body=json.loads(body),
        )


def get_version(socket_connection: Optional[str] = None) -> str:
    if socket_connection is not None:
        api = Api(socket_connection=socket_connection)
    else:
        api = Api()
    response = api.get("/version")
    return str(response.json_body["Version"])


def find_container() -> list[Container]:
    container_list: list[Container] = []
    for container in ps():
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
