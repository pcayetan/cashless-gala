from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager
from src.gui.QUtils import center
from src.gui.widgets.QForms import QRowInfo

from src.atoms.Atoms import *

# Trees are no longer supported in QAtomWidgets due to circular dependices
# resulting in hard to maintain program.


class QBuyingInfo(QWidget):
    def __init__(self, buying: Buying, parent=None):
        super().__init__(parent)
        productList = buying.getBasketItems()
        # Définitons
        self.mainLayout = QGridLayout()
        self.productTree = QTree([])

        self.userInfoGroupBox = QGroupBox()
        self.userInfoLayout = QVBoxLayout()

        self.buttonLayout = QHBoxLayout()
        self.editButton = QPushButton()
        self.deleteButton = QPushButton()
        self.okButton = QPushButton()

        # Layout
        self.userInfoGroupBox.setLayout(self.userInfoLayout)

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
    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        uim = QUIManager()

        self.setWindowTitle("Informations utilisateur")
        self.setWindowIcon(uim.getIcon("group"))
        self.setFixedSize(800, 600)

        self.user = user

        # Definition
        self.mainLayout = QVBoxLayout()
        self.userInfoGroupBox = QGroupBox()
        self.userInfoGroupBoxLayout = QVBoxLayout()
        self.userInfo = QRowInfo()

        # Layout
        self.userInfoGroupBoxLayout.addWidget(self.userInfo)
        self.mainLayout.addWidget(self.userInfoGroupBox)

        self.userInfoGroupBox.setLayout(self.userInfoGroupBoxLayout)

        # Settings
        self.userInfo.addRow("Solde:", user.getBalance())
        self.userInfo.addRow("UID:", user.getId())
        self.userInfoGroupBox.setTitle("Informations utilisateur")
        self.setLayout(self.mainLayout)

        # Window settings
        # self.setFixedSize(500, 500)
        center(self)
        self.setWindowTitle("Information utilisateur")
        self.setWindowIcon(uim.getWindowIcon("group"))

    def updateUserBalance(self):
        client = Client()
        balance = client.requestUserBalance(customer_id=self.user.getId())
        self.user.setBalance(balance)
        self.userInfo.setRow(0, 1, balance)


class QProductInfo(QWidget):
    def __init__(self, product: Product, parent=None):
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
        center(self)
