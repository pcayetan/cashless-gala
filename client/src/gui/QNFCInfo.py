from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
from src.utils.Euro import Eur
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager
from src.managers.Client import Client

from src.gui.widgets.QForms import QRowInfo

from src.trees.QItemTree import QUserHistory
from src.atoms.Atoms import User


class QNFCInfo(QWidget):
    def __init__(self, parent=None):
        nfcm = QNFCManager()
        # uim = QUIManager()
        super().__init__(parent)

        # Definition
        self.mainLayout = QVBoxLayout()

        self.groupBox = QGroupBox()
        self.groupBoxLayout = QVBoxLayout()
        self.rowInfo = QRowInfo()
        self.userHistoryButton = QPushButton()

        self.user = User()
        self.userHistory = None

        # Layout

        self.groupBox.setLayout(self.groupBoxLayout)
        self.groupBoxLayout.addWidget(self.rowInfo)
        self.groupBoxLayout.addWidget(self.userHistoryButton)

        # main layout
        self.mainLayout.addWidget(self.groupBox)
        self.setLayout(self.mainLayout)

        # Settings
        self.rowInfo.addRow("UID", nfcm.getCardUID())
        self.rowInfo.addRow("Solde", Eur(0))
        self.userHistoryButton.setText("Historique utilisateur")
        self.groupBox.setTitle("Info utilisateur")

        nfcm.cardInserted.connect(self.cardInserted)
        nfcm.cardRemoved.connect(self.cardRemoved)
        self.userHistoryButton.clicked.connect(self.showUserInfo)

    def cardInserted(self):
        nfcm = QNFCManager()
        client = Client()
        cardUID = nfcm.getCardUID()
        balance = client.requestUserBalance(customer_id=cardUID)
        self.rowInfo.setRow(1, 1, balance)
        self.rowInfo.setRow(0, 1, cardUID)
        self.user.setId(cardUID)
        self.user.setBalance(balance)

    def cardRemoved(self):
        self.rowInfo.setRow(1, 1, Eur(0))
        self.rowInfo.setRow(0, 1, "00 00 00 00")
        self.user.setId("00 00 00 00")
        self.user.setBalance(Eur(0))

    def update(self):
        nfcm = QNFCManager()
        client = Client()
        cardUID = nfcm.getCardUID()
        balance = client.requestUserBalance(customer_id=cardUID)
        self.rowInfo.setRow(1, 1, balance)
        self.user.setId(cardUID)
        self.user.setBalance(balance)

    def showUserInfo(self):
        nfcm = QNFCManager()
        if nfcm.hasCard():
            uim = QUIManager()
            self.userHistory = QUserHistory(self.user)
            self.userHistory.setWindowIcon(uim.getIcon("group"))
            self.userHistory.setWindowTitle("Information utilisateur")
            self.userHistory.setFixedSize(800, 600)
            self.userHistory.show()
