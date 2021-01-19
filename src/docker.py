import json
from typing import List

from src.utils import command
from src.volume import Volume


def inspect(container: str) -> json:
    # converts docker inspect to json and return only first container, because this works only with one container
    return json.loads(command("docker inspect {}".format(container)).stdout)[0]


def volumes(container: str) -> List[Volume]:
    result: List[Volume] = []
    container_info: json = inspect(container)
    for mount in container_info["Mounts"]:
        if mount['Type'] == "volume":
            result.append(Volume(mount['Name'], mount['Source']))
    return result
