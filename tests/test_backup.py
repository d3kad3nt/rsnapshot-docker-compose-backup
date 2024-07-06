from importlib import resources
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Generator
import shutil

import pytest

from rsnapshot_docker_compose_backup import backup_planer
from rsnapshot_docker_compose_backup.config.default_config import DefaultConfig

curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(name="setup_containers")
def fixture_setup_containers() -> Generator[Path, Any, None]:
    temp_dir = TemporaryDirectory()
    compose_dir = curr_dir / "container"
    temp_dir_path = Path(temp_dir.name) / "container"
    shutil.copytree(compose_dir, temp_dir_path)
    DefaultConfig.reset()
    yield temp_dir_path
    temp_dir.cleanup()


@pytest.fixture(name="setup_and_start_containers")
def fixture_setup_and_start_containers() -> Generator[Path, Any, None]:
    temp_dir = TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name) / "container"
    compose_dir = curr_dir / "container"
    shutil.copytree(compose_dir, temp_dir_path)
    start_containers(temp_dir_path)
    DefaultConfig.reset()
    yield temp_dir_path
    remove_containers(temp_dir_path)
    temp_dir.cleanup()


def start_containers(root_folder: Path) -> None:
    subfolders: list[Path] = [
        Path(f.path) for f in os.scandir(root_folder) if f.is_dir()
    ]
    for subfolder in subfolders:
        # print(subfolder)
        subprocess.run("docker compose up -d".split(), cwd=subfolder, check=True)


def stop_containers(root_folder: Path) -> None:
    subfolders: list[Path] = [
        Path(f.path) for f in os.scandir(root_folder) if f.is_dir()
    ]
    for subfolder in subfolders:
        subprocess.run("docker compose stop".split(), cwd=subfolder, check=True)


def remove_containers(root_folder: Path) -> None:
    subfolders: list[Path] = [
        Path(f.path) for f in os.scandir(root_folder) if f.is_dir()
    ]
    for subfolder in subfolders:
        subprocess.run(
            "docker compose rm --force --stop --volumes ".split(),
            cwd=subfolder,
            check=True,
        )


class TestRunningContainers:

    def test_default_config(self, setup_and_start_containers: Path) -> None:
        args = backup_planer.ProgramArgs(
            folder=setup_and_start_containers,
            config=load_config_path("default_config"),
        )
        output = backup_planer.run(args)
        assert (
            load_expected_output(
                "default_config_all_services", setup_and_start_containers
            )
            == output
        )


class TestStoppedContainers:

    def test_only_running_enabled(self, setup_and_start_containers: Path) -> None:
        stop_containers(setup_and_start_containers)
        args = backup_planer.ProgramArgs(
            folder=setup_and_start_containers,
            config=load_config_path("default_config"),
        )
        output = backup_planer.run(args)
        assert load_expected_output("empty", setup_and_start_containers) == output

    def test_only_running_disabled(self, setup_and_start_containers: Path) -> None:
        stop_containers(setup_and_start_containers)
        args = backup_planer.ProgramArgs(
            folder=setup_and_start_containers,
            config=load_config_path("not_running"),
        )
        output = backup_planer.run(args)
        # print(output)
        expected_output = load_expected_output(
            "default_config_all_services", setup_and_start_containers
        )
        assert expected_output == output


def test_not_started_containers(setup_containers: Path) -> None:
    args = backup_planer.ProgramArgs(
        folder=setup_containers, config=load_config_path("default_config")
    )
    assert load_expected_output("empty", setup_containers) == backup_planer.run(args)


def load_expected_output(name: str, container_folder: Path) -> str:
    return resources.read_text(package="tests.output", resource=f"{name}.log").replace(
        "${{container_folder}}", str(container_folder)
    )


def load_config_path(name: str) -> Path:
    return curr_dir / Path("config") / Path(f"{name}.ini")
