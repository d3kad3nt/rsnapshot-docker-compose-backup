#This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.
from typing import List
import os
import configparser

backupSteps = [
    ("RuntimeBackup",""),
    ("PreStop","")
    ("Stop","")
    ("PreBackup","")
    ("Backup","")
    ("PostBackup","")
    ("Restart","")
    ("PostRestart","")
]
class Container:
    folder:str
    name:str
    config: configparser.ConfigParser

    def __init__(self, folder:str):
        self.folder = folder
        self.name = os.path.basename(os.path.normpath(folder))
        self.readConfig()

    def readConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.folder + "backup.ini")

        pass

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
    for step in backupSteps:
        backupStep(step,container)

def backupYAML(container:Container):
    print(f"backup\t{container.folder}/docker-compose.yml\tdocker/{container.name}")

def testDefaultConfig():
    config = configparser.ConfigParser()
    config["defaultActions"]["PreBackup"] = "cmd docker-compose stop"
    config["defaultActions"]["Backup"] = ""#TODO add Backup command
    config["defaultActions"]["PostBackup"] = "cmd docker-compose start"

def main():
    testDefaultConfig()
    dockerContainer: List[Container] = findDockerDirs()
    for container in dockerContainer:
        backup(container)

if __name__ == "__main__":
    main()

