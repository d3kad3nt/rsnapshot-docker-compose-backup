from __future__ import annotations

from typing import NoReturn

import os
import configparser

class Config:

    defaultConfig: Config = None

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

    def __init__(self, configPath: str, container = None):
        self.configFile = configparser.ConfigParser()
        if os.path.isfile(configPath):
            self.configFile.read([defaultConfigName,configPath])
            if not self.configFile.sections():
                raise Exception("The Config for {} has no Sections".format(container.name))
        else:
            print("#No specific config for {}.".format(container.name))
            self.configFile.read(defaultConfigName)
        self.container = container
        if container:
            self.vars["$volumeRootDir"] = self.defaultConfig.setting("volumeRootDir")
            self.vars["$containerName"] = self.container.name
            self.vars["$containerConfigDir"] = self.container.folder

    def output(self) -> NoReturn:
        for section in self.configFile.sections():#TODO if there are multiple container in a compose file but only one section the other container are not backuped.
            #TODO goes throu all sections also settings and defaultActions
            print("#{}".format(self.container.name))
            for step in self.backupSteps:
                action = None
                if self.configFile.has_option(section,step):
                    action = self.configFile.get(section,step)
                elif self.configFile.has_option(defaultConfigName,step):
                    action = self.configFile.get(defaultConfigName,step)
                if action:
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
            cmd = "backup_exec\t" + cmd[3:].strip()
        return cmd 

    def setting(self, name: str) -> str:
        return self.configFile.get(settingSection,name)


defaultConfigName = "backup.ini"
settingSection = "settings"
defaultActions  = "defaultActions"

def loadConfig(name: str) -> Config:
    return Config(defaultConfigName)

def createDefaultConfig() -> Config:
    defaultConfig = configparser.ConfigParser()

    defaultConfig[settingSection] = {}
    defaultConfig[settingSection]["volumeRootDir"] = "/var/lib/docker/volumes/"
    defaultConfig[settingSection]["backupPrefixFolder"] = "/var/lib/docker/volumes/"
    defaultConfig[defaultActions] = {}
    defaultConfig[defaultActions]["PreBackup"] = "cmd docker-compose stop"
    defaultConfig[defaultActions]["Backup"] = "backup    $volumes    $backupPrefixFolder/$containerName/$volumes"
    defaultConfig[defaultActions]["PostBackup"] = "cmd docker-compose start"
    with open(defaultConfigName,'w') as configfile:
        defaultConfig.write(configfile)
    return Config(defaultConfig)

def getDefaultConfig() -> Config:
    if os.path.isfile(defaultConfigName):
        return loadConfig(defaultConfigName) 
    else:
        return createDefaultConfig()

Config.defaultConfig = getDefaultConfig()