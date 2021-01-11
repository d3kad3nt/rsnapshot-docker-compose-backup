from typing import NoReturn

import os

from config import Config

class Container:
    folder:str
    name:str
    config: Config

    def __init__(self, folder:str, name:str = None ):
        self.folder = folder
        if name:
            self.name = name
        else:
            self.name = os.path.basename(os.path.normpath(folder))
        self.__readConfig()

    def __readConfig(self)-> NoReturn:
        fileName =  os.path.join(self.folder,"backup.ini")
        self.config = Config(fileName,self)

    def backup(self) -> NoReturn:
        print(f"backup\t{self.folder}/docker-compose.yml\tdocker/{self.name}")
        self.config.output()
        print("\n")