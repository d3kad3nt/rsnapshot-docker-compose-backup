# This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

# Imports for typing
from typing import List
from typing import NoReturn
import argparse

import dockerCompose
from container import Container

# Other imports
from src.DefaultConfig import DefaultConfig

"""Finds all docker-compose dirs in current subfolders
:returns: a list of all folders
"""


def main() -> NoReturn:
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--folder", required=False, help="Path to the root folder of all docker-compose folders")
    args = vars(ap.parse_args())
    DefaultConfig.defaultConfigFolder = args["folder"]
    docker_container: List[Container] = dockerCompose.find_running_container(args["folder"])
    for container in docker_container:
        container.backup()


if __name__ == "__main__":
    main()
