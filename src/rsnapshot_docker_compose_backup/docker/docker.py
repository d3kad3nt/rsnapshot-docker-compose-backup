import json
import re
from typing import Any, Optional

from rsnapshot_docker_compose_backup.utils import command
from rsnapshot_docker_compose_backup.structure.volume import Volume


def inspect(container: str) -> Any:
    # converts docker inspect to json and return only first container,
    # because this works only with one container
    return json.loads(command("docker inspect {}".format(container)).stdout)[0]


def ps(container_id: Optional[str] = None) -> str:
    result = command("docker ps -a").stdout
    if container_id:
        for line in ps().splitlines():
            if line.startswith(container_id[:11]):
                return line
        return ""
    return result


def volumes(container_id: str) -> list[Volume]:
    result: list[Volume] = []
    container_info = inspect(container_id)
    for mount in container_info["Mounts"]:
        if mount["Type"] == "volume":
            result.append(Volume(mount["Name"], mount["Source"]))
    return sorted(result)


def get_column(column_nr: int, input_str: str) -> str:
    return re.sub(r"\s\s+", "  ", input_str).split("  ")[column_nr]


def image(container_id: str) -> str:
    container_info: str = ps(container_id)
    return get_column(1, container_info)
