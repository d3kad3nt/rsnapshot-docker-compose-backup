from rsnapshot_docker_compose_backup.docker import docker


def test_docker_connection():
    assert docker.get_version() == "27.0.3"
