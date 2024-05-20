# content of test_sample.py
from rsnapshot_docker_compose_backup import backup_planer
from importlib import resources
import os


def test_backup():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    container_dir = os.path.join(curr_dir, "container")
    args = backup_planer.ProgramArgs(folder=container_dir, config="")
    assert load_expected_output() == backup_planer.run(args)


def load_expected_output() -> str:
    return resources.read_text(package="tests", resource="expected_output.log")
