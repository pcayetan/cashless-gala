from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
from QNFCManager import QNFCManager
from QUIManager import QUIManager
from QUtils import QRowInfo, center
import QUtils  # For some reason, there is a namespace conflict with "center" and another Qt function
from QItemTree import *


class QNFCInfo(QWidget):
    def __init__(self, parent=None):
        nfcm = QNFCManager()
        uim = QUIManager()
        super().__init__(parent)

        # Definition
        self.mainLayout = QVBoxLayout()

        self.groupBox = QGroupBox()
        self.groupBoxLayout = QVBoxLayout()
        self.rowInfo = QRowInfo()
        self.userHistoryButton = QPushButton()

        self.user = QUser(User())

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
        uim.balanceUpdated.connect(self.update)
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

    def showUserInfo(self):
        nfcm = QNFCManager()
        if nfcm.hasCard():
            self.user.showInfoPannel()


class QBuyingInfo(QWidget):
    def __init__(self, qBuying, parent=None):
        super().__init__(parent)
        productList = qBuying.getBasketItems()
        # Définitons
        self.mainLayout = QGridLayout()
        self.productTree = QTree([],)

        self.userInfoGroupBox = QGroupBox()
        self.userInfoLayout = QVBoxLayout()
        self.userInfoTree = QUserList()

        self.buttonLayout = QHBoxLayout()
        self.editButton = QPushButton()
        self.deleteButton = QPushButton()
        self.okButton = QPushButton()

        # Layout
        self.userInfoGroupBox.setLayout(self.userInfoLayout)
        self.userInfoLayout.addWidget(self.userInfoTree)

        self.mainLayout.addWidget(self.productTree, 0, 0)
        self.mainLayout.addWidget(self.userInfoGroupBox, 0, 1)
        self.mainLayout.addLayout(self.buttonLayout, 1, 0, 1, 2)

        # self.userRowInfo.addRow("UID",)

        self.buttonLayout.addWidget(self.editButton)
        self.buttonLayout.addWidget(self.deleteButton)
        self.buttonLayout.addWidget(self.okButton)

        self.setLayout(self.mainLayout)

        # Settings
        self.userInfoGroupBox.setTitle("Clients")
        self.editButton.setText("Éditer")
        self.deleteButton.setText("Rembourser")
        self.okButton.setText("Retour")


class QUserInfo(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        uim = QUIManager()

        self.setWindowTitle("Informations utilisateur")
        self.setWindowIcon(uim.getIcon("group"))

        # Definition
        self.mainLayout = QVBoxLayout()
        self.userInfoGroupBox = QGroupBox()
        self.userInfoGroupBoxLayout = QVBoxLayout()
        self.historyTree = QUserHistory(user)
        self.userInfo = QRowInfo()

        # Layout
        self.userInfoGroupBoxLayout.addWidget(self.userInfo)
        self.mainLayout.addWidget(self.userInfoGroupBox)
        self.mainLayout.addWidget(self.historyTree)

        self.userInfoGroupBox.setLayout(self.userInfoGroupBoxLayout)

        # Settings

        self.userInfo.addRow("Solde:", user.getBalance())
        self.userInfo.addRow("UID:", user.getId())
        self.userInfoGroupBox.setTitle("Informations utilisateur")
        self.setLayout(self.mainLayout)

        # Window settings
        self.setFixedSize(500, 500)
        QUtils.center(self)
        self.setWindowTitle("Information utilisateur")
        self.setWindowIcon(uim.getWindowIcon("group"))


class QProductInfo(QWidget):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        uim = QUIManager()

        # Definition
        self.mainLayout = QVBoxLayout()
        self.rowInfo = QRowInfo()
        # Layout
        self.mainLayout.addWidget(self.rowInfo)
        self.setLayout(self.mainLayout)

        # Settings

        self.rowInfo.addRow("Prix", product.getPrice())
        self.rowInfo.addRow("Nom", product.getName())
        self.rowInfo.addRow("Code", product.getCode())
        self.rowInfo.addRow("Id", product.getId())
        self.setFixedSize(300, 100)

        self.setWindowTitle("Informations produit")
        self.setWindowIcon(uim.getWindowIcon("product"))
        QUtils.center(self)
