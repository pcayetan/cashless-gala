import copy
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QMovie

# Project specific imports
import logging

# copy is mandatory because of the init of path
# indeed ... A= [X,Y]
#           B=A
# A and B are now sharing the same memory !


class QUIManagerSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QUIManagerSingleton, cls).__call__()
        return cls._instance[cls]


class QUIManager(QObject, metaclass=QUIManagerSingleton):
    balanceUpdated = pyqtSignal()  # Update balance
    historyUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "default"
        self.themePath = Path("ressources/themes") / self.theme

        self.iconPath = self.themePath / "ui-icons"
        self.windowIconPath = self.themePath / "window-icons"
        self.animationPath = self.themePath / "animation"

    def getIcon(self, iconName):
        """Return the QIcon according to 'iconName'. None if no icon is found"""
        # iconPath = self.__relPath(self.iconRelPath)
        # fileList = os.listdir(self.iconPath)
        fileList = Path(self.iconPath).iterdir()
        icon = None
        for file in fileList:
            name = file.stem
            if name == iconName:
                try:
                    icon = QIcon(str(file))
                except:
                    log.error("Unable to load the ressource {}".format(file))

        return icon

    def getWindowIcon(self, iconName):
        """Return the QIcon according to 'iconName'. None if no icon is found"""
        # iconPath = self.__relPath(self.windowIconRelPath)
        fileList = Path(self.windowIconPath).iterdir()
        icon = None
        for file in fileList:
            name = file.stem
            if name == iconName:
                try:
                    icon = QIcon(str(file))
                except:
                    log.error("Unable to load the ressource {}".format(file))

        return icon

    def getAnimation(self, animationName):
        """Return the QIcon according to 'iconName'. None if no icon is found"""
        # animationPath = self.__relPath(self.animationRelPath)
        fileList = Path(self.animationPath).iterdir()
        movie = None
        for file in fileList:
            name = file.stem
            if name == animationName:
                try:
                    movie = QMovie(str(file))
                except:
                    log.error("Unable to load the ressource {}".format(file))

        return movie


#    def updateBalance(self):
#        self.emit(self.balanceUpdated)
