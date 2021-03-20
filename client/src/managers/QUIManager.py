import os
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QMovie
from Console import *

# copy is mandatory because of the init of path
# indeed ... A= [X,Y]
#           B=A
# A and B are now sharing the same memory !
import copy

GMC_DIR = Path(os.environ['GMC_DIR'])


class QUIManagerSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QUIManagerSingleton, cls).__call__()
        return cls._instance[cls]


class QUIManager(QObject, metaclass=QUIManagerSingleton):
    balanceUpdated = pyqtSignal()  # Update balance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "default"
        self.themePath = GMC_DIR / "ressources" / "themes" / self.theme

        self.iconPath = self.themePath / "ui-icons"
        self.windowIconPath = self.themePath / "window-icons"
        self.animationPath = self.themePath / "animation"

    def getIcon(self, iconName):
        """Return the QIcon according to 'iconName'. None if no icon is found"""
        #iconPath = self.__relPath(self.iconRelPath)
        fileList = os.listdir(self.iconPath)
        icon = None
        for file in fileList:
            name = file.split(".")[0]  # [name, extention]
            if name == iconName:
                try:
                    icon = QIcon(str(self.iconPath / file))
                except:
                    printE("Unable to load the ressource {}".format(file))

        return icon

    def getWindowIcon(self, iconName):
        """Return the QIcon according to 'iconName'. None if no icon is found"""
        #iconPath = self.__relPath(self.windowIconRelPath)
        fileList = os.listdir(self.windowIconPath)
        icon = None
        for file in fileList:
            name = file.split(".")[0]  # [name, extention]
            if name == iconName:
                try:
                    icon = QIcon(str(self.windowIconPath / file))
                except:
                    printE("Unable to load the ressource {}".format(file))

        return icon

    def getAnimation(self, animationName):
        """Return the QIcon according to 'iconName'. None if no icon is found"""
        #animationPath = self.__relPath(self.animationRelPath)
        fileList = os.listdir(self.animationPath)
        movie = None
        for file in fileList:
            name = file.split(".")[0]  # [name, extention]
            if name == animationName:
                try:
                    movie = QMovie(str(self.animationPath / file))
                except:
                    printE("Unable to load the ressource {}".format(file))

        return movie