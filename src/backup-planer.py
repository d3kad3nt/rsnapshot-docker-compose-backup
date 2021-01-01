#This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.
from typing import List
import os

backup_dir: str = "/mount/backup"

class Container:
    folder:str
    name:str = "test"

    def __init__(self, folder:str):
        self.folder = folder

"""Finds all docker-compose dirs in current subfolders
:returns: a list of all folders
"""
def findDockerDirs() -> List[Container]:
    dirs: List[Container] = [] 
    cwd: str = os.getcwd()
    for treeElement in os.walk(cwd):
        if ("docker-compose.yml" in treeElement[2]):
            dirs.append(Container(treeElement[0]))
    print(dirs)
    return dirs

def backup(container:Container):
    backupYAML(container)

def backupYAML(container:Container):
    print(f"backup\t{container.folder}/docker-compose.yml\t{backup_dir}/{container.name}")

def main():
    dockerContainer: List[Container] = findDockerDirs()
    for container in dockerContainer:
        backup(container)

if __name__ == "__main__":
    main()

