from importlib import resources
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Generator

import pytest

from rsnapshot_docker_compose_backup import backup_planer


@pytest.fixture(name="setup_containers")
def fixture_setup_containers() -> Generator[TemporaryDirectory[str], Any, None]:
    temp_dir = TemporaryDirectory()
    yield temp_dir
    temp_dir.cleanup()


@pytest.fixture(name="setup_and_start_containers")
def fixture_setup_and_start_containers() -> (
    Generator[TemporaryDirectory[str], Any, None]
):
    temp_dir = TemporaryDirectory()
    start_containers(Path(temp_dir.name))
    yield temp_dir
    remove_containers(Path(temp_dir.name))
    temp_dir.cleanup()


def start_containers(root_folder: Path):
    subfolders: list[Path] = [
        Path(f.path) for f in os.scandir(root_folder) if f.is_dir()
    ]
    for subfolder in subfolders:
        subprocess.run("docker compose up -d", cwd=subfolder, check=True)


def stop_containers(root_folder: Path):
    subfolders: list[Path] = [
        Path(f.path) for f in os.scandir(root_folder) if f.is_dir()
    ]
    for subfolder in subfolders:
        subprocess.run("docker compose stop", cwd=subfolder, check=True)


def remove_containers(root_folder: Path):
    subfolders: list[Path] = [
        Path(f.path) for f in os.scandir(root_folder) if f.is_dir()
    ]
    for subfolder in subfolders:
        subprocess.run(
            "docker compose rm --force --stop --volumes ", cwd=subfolder, check=True
        )


def test_running_containers(setup_and_start_containers: TemporaryDirectory[str]):
    args = backup_planer.ProgramArgs(
        folder=setup_and_start_containers.name,
        config=load_config_path("default_config"),
    )
    assert load_expected_output("empty") == backup_planer.run(args)


def test_not_started_containers(setup_containers: TemporaryDirectory[str]):
    args = backup_planer.ProgramArgs(
        folder=setup_containers.name, config=load_config_path("default_config")
    )
    assert load_expected_output("empty") == backup_planer.run(args)


def load_expected_output(name: str) -> str:
    return resources.read_text(package="tests.output", resource=f"{name}.log")


def load_config_path(name: str) -> Path:
    curr_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    return curr_dir / Path("config") / Path("name")
