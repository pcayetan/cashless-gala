import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

from QManager import *
from QNFC import *
from QUtils import *
from QItemTree import *

from Client import *



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

        #Definition
        self.mainLayout = QHBoxLayout()

        #Left pannel
        self.productSelectionLayout = QVBoxLayout()
        self.searchBar = QSearchBar()
        self.itemSelector = QProductSelector()

        #Mid pannel
        self.basket = None
        
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


class QNFCInfo(QWidget):

    def __init__(self,parent=None):
        nfcm=QNFCManager()
        super().__init__(parent)
        
        #Definition
        self.mainLayout = QVBoxLayout()
        
        self.groupBox = QGroupBox()
        self.groupBoxLayout = QVBoxLayout()
        self.rowInfo = QRowInfo()
        self.userHistoryButton = QPushButton()

        #Layout

        self.groupBox.setLayout(self.groupBoxLayout)
        self.groupBoxLayout.addWidget(self.rowInfo)
        self.groupBoxLayout.addWidget(self.userHistoryButton)

        #main layout
        self.mainLayout.addWidget(self.groupBox)
        self.setLayout(self.mainLayout)

        #Settings
        self.rowInfo.addRow("UID",nfcm.getCardUID())
        self.rowInfo.addRow("Solde",Eur(0))
        self.userHistoryButton.setText("Historique utilisateur")
        self.groupBox.setTitle("Info utilisateur")

