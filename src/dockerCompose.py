from typing import List
from typing import NoReturn

import os
import subprocess
import re

from container import Container


def findContainer() -> List[Container]:
    
    allContainer: List[Container] = []
    dockerDirs: List[str] = findDockerDirs()
    for dir in dockerDirs:
        res = command("docker-compose ps", path = dir)
        containerList: List[str] = getRunningContainer(res.stdout)
        for container in containerList:
            allContainer.append(Container(dir,container))
    return allContainer

"""Finds all docker-compose dirs in current subfolders
:returns: a list of all folders
"""
def findDockerDirs() -> List[str]:
    dirs: List[Container] = [] 
    cwd: str = os.getcwd()
    for treeElement in os.walk(cwd):
        if ("docker-compose.yml" in treeElement[2]):
            dirs.append(treeElement[0])
    return dirs

def getRunningContainer(psOut: str) -> List[str]:
    return getContainer(psOut, state="UP")

def getContainer(psOut: str, state: str = None) -> List[str]:
    allContainer = psOut.splitlines()[2:]
    container = []
    if not allContainer:
        return []
    for line in allContainer:
        parts = re.sub(r"\s\s+", "  ", line).split("  ")
        up = parts[2].upper()
        if not state or up == state.upper():
            container.append(parts[0])
    return container

def command(cmd: str, path: str = ".")-> subprocess.CompletedProcess:
    res = subprocess.run(cmd.split(" "), cwd = path, encoding="UTF-8", capture_output = True)
    return res

findContainer()