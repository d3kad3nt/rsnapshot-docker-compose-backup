import json
from typing import List

from src.utils import command


def inspect(container: str) -> json:
    # converts docker inspect to json and return only first container, because this works only with one container
    return json.loads(command("docker inspect {}".format(container)).stdout)[0]


def volumes(container: str) -> List[str]:
    result: List[str] = []
    container_info: json = inspect(container)
    for mount in container_info["Mounts"]:
        result.append(mount['Source'])
    return result
