# This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

import argparse
# Imports for typing
import os
from typing import List
from typing import NoReturn

import dockerCompose
from container import Container

# Other imports
from src import DefaultConfig

"""Finds all docker-compose dirs in current subfolders
:returns: a list of all folders
"""


def main() -> NoReturn:
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--folder", required=False, help="Path to the root folder of all docker-compose folders",
                    default=os.getcwd())
    args = vars(ap.parse_args())
    DefaultConfig.set_folder(args["folder"])
    docker_container: List[Container] = dockerCompose.find_running_container(args["folder"])
    for container in docker_container:
        container.backup()


if __name__ == "__main__":
    main()
