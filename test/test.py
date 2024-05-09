#! /usr/bin/env python3
from testcontainers.compose import DockerCompose
import os
from src.rsnapshot_docker_compose_backup import backup_planer

script_dir = os.path.dirname(os.path.realpath(__file__))

with DockerCompose(
    os.path.join(script_dir, "docker-compose", "containerName"), pull=True
) as compose:
    backup_planer.main()
    stdout, stderr = compose.get_logs()
    if stdout:
        print("Stdout\n:{}".format(stdout))
    if stderr:
        print("Errors\n:{}".format(stderr))
