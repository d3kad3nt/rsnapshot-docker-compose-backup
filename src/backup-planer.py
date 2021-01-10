#This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

#Imports for typing
from __future__ import annotations
from typing import List
from typing import NoReturn

#Other imports
import os
import configparser

from container import Container
from config import Config

"""Finds all docker-compose dirs in current subfolders
:returns: a list of all folders
"""
def findDockerDirs() -> List[Container]:
    dirs: List[Container] = [] 
    cwd: str = os.getcwd()
    for treeElement in os.walk(cwd):
        if ("docker-compose.yml" in treeElement[2]):
            dirs.append(Container(treeElement[0]))
    return dirs

def backup(container:Container) -> NoReturn:
    container.backup()

def main() -> NoReturn:
    dockerContainer: List[Container] = findDockerDirs()
    for container in dockerContainer:
        backup(container)

if __name__ == "__main__":
    main()

