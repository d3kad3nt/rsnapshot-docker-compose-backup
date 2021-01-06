#This Script is used to create a config file for rsnapshot that can be used to backup different docker-compose container.

#Imports for typing
from __future__ import annotations
from typing import List
from typing import NoReturn

#Other imports
import os
import configparser


class Config:

    backupSteps = [
        "RuntimeBackup",
        "PreStop",
        "Stop",
        "PreBackup",
        "Backup",
        "PostBackup",
        "Restart",
        "PostRestart",
    ]

    configFile: configparser.ConfigParser
    vars = {}

    def __init__(self, configFile: configparser.ConfigParser, container: Container = None):
        self.configFile = configFile
        self.container = container
        if container:
            self.vars["$volumeRootDir"] = defaultConfig.setting("volumeRootDir")
            self.vars["$containerName"] = self.container.name
            self.vars["$containerConfigDir"] = self.container.folder

    def output(self) -> NoReturn:
        for section in self.configFile.sections():
            for step in self.backupSteps:
                if self.configFile.has_option(section,step):
                    print(f"#{step}")
                    for line in self.configFile.get(section,step).splitlines():
                        print(self.__parse(line))

    def __parse(self, cmd: str)-> str:
        cmd = self.__resolveVars(cmd)
        cmd = self.__resolveCommands(cmd)
        return cmd
 
    def __resolveVars(self, cmd: str) -> str:
        for var in self.vars:
            cmd = cmd.replace(var,self.vars[var])
        return cmd

    def __resolveCommands(self, cmd: str) -> str:
        if cmd.startswith("cmd"):
            cmd = "backup-script\t" + cmd[3:].strip()
            cmd = cmd + "\t/dev/null"
        return cmd 

    def setting(self, name: str) -> str:
        return self.configFile.get(settingSection,name)

class Container:
    folder:str
    name:str
    config: Config

    def __init__(self, folder:str):
        self.folder = folder
        self.name = os.path.basename(os.path.normpath(folder))
        self.__readConfig()

    def __readConfig(self)-> NoReturn:
        fileName =  os.path.join(self.folder,"backup.ini")
        configParser = configparser.ConfigParser()
        if os.path.isfile(fileName):
            configParser.read([defaultConfigName,fileName])
            if not configParser.sections():
                raise Exception("The Config for {} has no Sections".format(self.name))
        else:
            print("#No config for {}.".format(self.name))
        
        self.config = Config(configParser,self)

    def backup(self) -> NoReturn:
        print(f"backup\t{self.folder}/docker-compose.yml\tdocker/{self.name}")
        self.config.output()


defaultConfigName  = "backup.ini"
settingSection = "settings"
defaultActions  = "defaultActions"
defaultConfig: Config
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

def loadConfig(name: str) -> Config:
    config = configparser.ConfigParser()
    config.read(defaultConfigName)
    return Config(config)

def createDefaultConfig() -> Config:
    defaultConfig = configparser.ConfigParser()

    defaultConfig[settingSection] = {}
    defaultConfig[settingSection]["volumeRootDir"] = "/var/lib/docker/volumes/"
    defaultConfig[defaultActions] = {}
    defaultConfig[defaultActions]["PreBackup"] = "cmd docker-compose stop"
    defaultConfig[defaultActions]["Backup"] = "backup    $volumes    $backupPrefixFolder/$containerName/$volumes"
    defaultConfig[defaultActions]["PostBackup"] = "cmd docker-compose start"
    with open(defaultConfigName,'w') as configfile:
        defaultConfig.write(configfile)
    return Config(defaultConfig)

def testDefaultConfig() -> NoReturn:
    global defaultConfig
    if os.path.isfile(defaultConfigName):
        defaultConfig = loadConfig(defaultConfigName) 
    else:
        defaultConfig = createDefaultConfig()

def main() -> NoReturn:
    testDefaultConfig()
    dockerContainer: List[Container] = findDockerDirs()
    print(defaultConfig)
    for container in dockerContainer:
        backup(container)

if __name__ == "__main__":
    main()

