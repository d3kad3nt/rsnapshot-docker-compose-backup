from rsnapshot_docker_compose_backup.docker import docker


def test_version() -> None:
    assert docker.get_version() == "27.0.3"


def test_ps() -> None:
    print(docker.ps(container_id="81b7284e70d9"))
    assert False
