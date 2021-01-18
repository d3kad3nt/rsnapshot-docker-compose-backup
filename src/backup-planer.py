# This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

# Imports for typing
from typing import List
from typing import NoReturn

import dockerCompose
from container import Container

# Other imports

"""Finds all docker-compose dirs in current subfolders
:returns: a list of all folders
"""


def main() -> NoReturn:
    docker_container: List[Container] = dockerCompose.find_running_container()
    for container in docker_container:
        container.backup()


if __name__ == "__main__":
    main()
