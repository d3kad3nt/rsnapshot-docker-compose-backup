#This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

#Imports for typing
from typing import List
from typing import NoReturn

#Other imports
import os

from container import Container
from config import Config
import dockerCompose

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

def main() -> NoReturn:
    dockerCompose.findContainer()
    dockerContainer: List[Container] = findDockerDirs() 
    for container in dockerContainer:
        container.backup()

if __name__ == "__main__":
    main()

