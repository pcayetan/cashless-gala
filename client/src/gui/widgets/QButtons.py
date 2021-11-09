from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
from src.utils.Euro import Eur
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager


class QDelButton(QToolButton):

    deleted = pyqtSignal(QToolButton)

    def __init__(self, parent=None):
        super().__init__(parent)

        uim = QUIManager()
        self.row = -1
        self.clicked.connect(self.delete)

        # So normally ui manager should be used here
        # but because of the cycle import problem I can't import the ui manager here unless
        # I merge QAtoms with QManager...
        #        self.setIcon(QIcon("ressources/themes/default/ui-icons/delete.png"))
        self.setIcon(uim.getIcon("delete"))
        self.setIconSize(QSize(32, 32))
        self.setFixedSize(QSize(48, 48))

    def setRow(self, row):
        self.row = row

    def getRow(self):
        return self.row

    def delete(self):
        self.deleted.emit(self)
