# This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

import argparse

# Imports for typing
import os
from typing import List

from src.container import Container

# Other imports
from src.global_values import set_folder, set_config_file
from src import docker_compose


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-f",
        "--folder",
        required=False,
        help="Path to the root folder of all docker-compose folders",
        default=os.getcwd(),
    )
    ap.add_argument(
        "-c",
        "--config",
        required=False,
        help="Path to the root config file, if it isn't in the root docker-compose folder",
        default="",
    )
    args = vars(ap.parse_args())
    set_folder(args["folder"])
    set_config_file(args["config"])
    docker_container: List[Container] = docker_compose.find_running_container(
        args["folder"]
    )
    for container in docker_container:
        container.backup()


if __name__ == "__main__":
    main()
