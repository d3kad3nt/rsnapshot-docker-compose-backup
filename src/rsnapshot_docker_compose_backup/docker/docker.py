from concurrent import futures
from dataclasses import dataclass
from enum import Enum, auto
import json
import os
from pathlib import Path
import re
import socket
from typing import Any, Optional
import urllib.parse
from rsnapshot_docker_compose_backup.structure.container import Container
from rsnapshot_docker_compose_backup.utils import command
from rsnapshot_docker_compose_backup.structure.volume import Volume


def inspect(container: str) -> Any:
    # converts docker inspect to json and return only first container,
    # because this works only with one container
    return json.loads(command("docker inspect {}".format(container)).stdout)[0]


class ContainerState(Enum):
    CREATED = auto()
    RESTARTING = auto()
    RUNNING = auto()
    REMOVING = auto()
    PAUSED = auto()
    EXITED = auto()
    DEAD = auto()

    @staticmethod
    def get_value(value: str) -> "ContainerState":
        for member in ContainerState:
            if member.name.lower() == value.lower():
                return member
        raise ValueError("Unknown Value: " + value)


@dataclass
class docker_inspect:
    id: str
    names: list[str]
    image: str
    imageId: str
    state: ContainerState
    mounts: list[str]


@dataclass
class docker_ps:
    container_info: list[docker_inspect]


def ps(container_id: Optional[str] = None) -> docker_ps:
    parameter = {"all": "true"}
    if container_id is not None:
        parameter["filters"] = '{"id": ["' + container_id + '"]}'
    response = Api().get("/containers/json", query_parameter=parameter)
    container_info_list: list[docker_inspect] = []
    for container_info in response.json_body:
        container_info_list.append(
            docker_inspect(
                id=container_info["Id"],
                names=container_info["Names"],
                image=container_info["Image"],
                imageId=container_info["ImageID"],
                state=ContainerState.get_value(container_info["State"]),
                mounts=container_info["Mounts"],
            )
        )
    return docker_ps(container_info=container_info_list)


def volumes(container_id: str) -> list[Volume]:
    result: list[Volume] = []
    container_info = inspect(container_id)
    for mount in container_info["Mounts"]:
        if mount["Type"] == "volume":
            result.append(Volume(mount["Name"], mount["Source"]))
    return sorted(result)


def image(container_id: str) -> str:
    container_info: docker_ps = ps(container_id)
    return container_info.container_info[0].image


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
            chunk = sock.recv(1)
            message_start = message_start + chunk
        lines: list[str] = message_start.decode("utf-8").splitlines()
        status_line = lines[0]
        protocol_version = status_line.split(" ")[0]
        status_code = int(status_line.split(" ")[1])
        status_text = " ".join(status_line.split(" ")[2:])
        if status_code >= 400:
            print(sock.recv(100))
            raise ValueError(status_text)
        headers: dict[str, str] = {}
        for line in lines[1:]:
            split = line.split(":")
            if len(split) == 2:
                headers[split[0]] = split[1]
        body_length = int(headers["Content-Length"])
        body = sock.recv(body_length).decode("utf-8")
        return HttpResponse(
            protocol_version=protocol_version,
            status_code=status_code,
            status_text=status_text,
            headers=headers,
            json_body=json.loads(body),
        )


def get_version() -> str:
    return str(Api().get("/version").json_body["Version"])


def get_binary() -> str:
    if command("docker compose").returncode == 0:
        return "docker compose"
    if command("docker-compose").returncode == 0:
        return "docker-compose"

    raise Exception("Docker Compose is not installed")


def get_container_id(service_name: str, path: Path) -> str:
    return command(
        "{} ps --all -q {}".format(get_binary(), service_name), path=path
    ).stdout[:12]


def get_container_name(service_name: str, path: Path) -> str:
    stdout = command(
        "{} config --format json {}".format(get_binary(), service_name),
        path=path,
    ).stdout
    # print(f"stdout: {stdout} (End)")
    return str(json.loads(stdout)["services"][service_name]["container_name"])


def container_stopped(container_id: str) -> bool:
    status = command(
        [
            "docker",
            "ps",
            "-a",
            "--format",
            "{{ .Status }}",
            "-f",
            f"id={container_id}",
        ]
    )
    # print(status.stdout)
    return status.stdout.startswith("Exited")


def find_container(root_folder: Path) -> list[Container]:
    all_container: list[Container] = []
    docker_dirs: list[Path] = find_docker_dirs(root_folder)
    with futures.ProcessPoolExecutor() as pool:
        for service_list, directory in pool.map(get_services, docker_dirs):
            # container_list: list[str] = get_services(output)
            for container_info in service_list:
                if container_info.container_id:
                    all_container.append(
                        Container(
                            folder=directory,
                            service_name=container_info.service_name,
                            container_name=container_info.container_name,
                            container_id=container_info.container_id,
                            running=not container_stopped(container_info.container_id),
                        )
                    )
    return all_container


@dataclass
class ContainerInfo:
    service_name: str
    container_name: str
    container_id: str


def get_services(path: Path) -> tuple[list[ContainerInfo], Path]:
    service_name: list[str] = command(
        "{} config --services".format(get_binary()), path=path
    ).stdout.splitlines()
    # Docker doesn't return it always in the same order
    service_name.sort()
    # print(service_name)
    services: list[ContainerInfo] = []
    for service in service_name:
        container_id = get_container_id(service, path)
        container_name = get_container_name(service, path)
        services.append(ContainerInfo(service, container_name, container_id))
    return services, path


def find_docker_dirs(root_folder: Path = Path(os.getcwd())) -> list[Path]:
    """Finds all docker-compose dirs in current sub folder
    :returns: a list of all folders"""
    dirs: list[Path] = []
    docker_compose_files = [
        "compose.yaml",
        "compose.yml",
        "docker-compose.yaml",
        "docker-compose.yml",
    ]
    for tree_element in os.walk(root_folder):
        for docker_compose_file in docker_compose_files:
            if docker_compose_file in tree_element[2]:
                dirs.append(Path(tree_element[0]))
                break
    return dirs


def get_running_container(ps_out: str) -> list[str]:
    return get_container(ps_out, state="UP")


def get_column(column_nr: int, input_str: str) -> str:
    return re.sub(r"\s\s+", "  ", input_str).split("  ")[column_nr]


def get_container(ps_out: str, state: Optional[str] = None) -> list[str]:
    all_container: list[str] = ps_out.splitlines()[2:]
    container: list[str] = []
    if not all_container:
        return []
    for line in all_container:
        up = get_column(2, line).upper()
        if not state or up == state.upper():
            container.append(get_column(0, line))
    return container
