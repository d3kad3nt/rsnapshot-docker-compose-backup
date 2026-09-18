#!/usr/bin/env python3

# This Script is used to create a config file for rsnapshot that can be used to backup
# different docker-compose container.


import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from rsnapshot_docker_compose_backup import docker

# Other imports
from rsnapshot_docker_compose_backup.global_values import set_config_file, set_folder

if TYPE_CHECKING:
    from rsnapshot_docker_compose_backup.structure.container import Container


@dataclass
class ProgramArgs:
    folder: Path
    config: Path | None
    socket: str | None


def parse_arguments() -> ProgramArgs:
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
        default=None,
    )
    ap.add_argument(
        "-s",
        "--socket",
        required=False,
        help="Path to the docker socket, if it isn't in the default location",
        default=None,
    )
    args = vars(ap.parse_args())
    if args["config"] is not None:
        config_file = Path(args["config"])
    else:
        config_file = None
    return ProgramArgs(
        folder=Path(args["folder"]), config=config_file, socket=args["socket"]
    )


def run(args: ProgramArgs) -> str:
    set_folder(args.folder)
    set_config_file(args.config)
    docker_container: list[Container] = docker.get_compose_container(
        args.folder, socket_connection=args.socket
    )
    result: list[str] = []
    for container in docker_container:
        container_result = container.backup()
        if container_result:
            result.append(container_result)
    return "\n".join(result)


def main() -> None:
    args: ProgramArgs = parse_arguments()
    print(run(args))  # noqa: T201


if __name__ == "__main__":
    main()
