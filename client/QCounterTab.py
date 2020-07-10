import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from QDataManager import QDataManager
from QNFCManager import QNFCManager
from QUIManager import QUIManager
from Client import Client


from QUtils import *
from QItemTree import *





class QAutoCompleteLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QCompleter()
        self.setCompleter(self.completer)
        self.model = QStringListModel()
        self.completer.setModel(self.model)


class QSearchBar(QWidget):
    """Fast Search Bar"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Definition
        self.mainHBoxLayout = QHBoxLayout()
        self.inputLine = QAutoCompleteLineEdit()
        self.pushButton = QPushButton()

        self.wordList = []

        # Link
        self.setLayout(self.mainHBoxLayout)
        self.mainHBoxLayout.addWidget(self.inputLine)
        self.mainHBoxLayout.addWidget(self.pushButton)

        # Settings

        # self.inputLine.resize(300,50)
        self.pushButton.setText("OK")

    def clearText(self):
        self.inputLine.setText("")


class QCounterTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        dm = QDataManager()

        #Definition
        self.mainLayout = QHBoxLayout()

        #Left pannel
        self.productSelectionLayout = QVBoxLayout()
        self.searchBar = QSearchBar()
        self.itemSelector = QProductSelector(dm.productDict)

        #Mid pannel
        self.basket =  QBasket()
        
        #Right pannel
        self.rightPannelLayout = QVBoxLayout() # find a better name ~
        self.systemInfo = None
        self.nfcInfo = QNFCInfo()
        self.history = None
        self.validateButtonLayout = QHBoxLayout()
        self.multiUserButton = QPushButton()
        self.singleUserButton = QPushButton()

        #Layout
        #left pannel
        self.productSelectionLayout.addWidget(self.searchBar)
        self.productSelectionLayout.addWidget(self.itemSelector)

        #Mid pannel
        
        #Right pannel

        self.rightPannelLayout.addWidget(self.systemInfo)
        self.rightPannelLayout.addWidget(self.nfcInfo)
        self.rightPannelLayout.addWidget(self.history)
        self.rightPannelLayout.addLayout(self.validateButtonLayout)

        self.validateButtonLayout.addWidget(self.multiUserButton)
        self.validateButtonLayout.addWidget(self.singleUserButton)

        #main layout
        self.mainLayout.addLayout(self.productSelectionLayout)
        self.mainLayout.addWidget(self.basket)
        self.mainLayout.addLayout(self.rightPannelLayout)
        self.setLayout(self.mainLayout)

        #Settings
        #Left pannel
        #Mid pannel
        #Right pannel
        self.singleUserButton.setText("Valider et payer") 
        self.multiUserButton.setText("Plusieurs clients")
        

        #signals
        self.itemSelector.itemSelected[Product].connect(self.basket.addProduct)



