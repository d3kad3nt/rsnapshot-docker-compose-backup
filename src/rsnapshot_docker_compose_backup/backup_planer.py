# This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

import argparse

# Imports for typing
import os
from typing import List

from rsnapshot_docker_compose_backup.container import Container

# Other imports
from rsnapshot_docker_compose_backup.global_values import set_folder, set_config_file
from rsnapshot_docker_compose_backup import docker_compose


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
