from QItemModel import *

from PyQt5.QtCore import pyqtSignal
from QNFC import QCardObserver
from smartcard.util import toHexString

import copy
import json

from QManager import *
from QUtils import *



class QAutoSelectLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class QSuperTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAnimated(True) #Because animation looks cool ~

    def focusOutEvent(self, event):
        self.setCurrentIndex(QModelIndex())


class QProductSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        dm = QDataManager()

        #Definition
        self.mainLayout = QVBoxLayout()
        self.treeView = QSuperTreeView()
        self.treeModel = QProductSelectorModel(["Produits","Prix"],dm.productDict)
        
        #Layout
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)

        #Settings
        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
