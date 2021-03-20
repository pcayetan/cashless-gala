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


class QMultiUserPannel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Definition
        self.mainLayout = QVBoxLayout()
        ## Progress bar
        self.progressBarGroupBox = QGroupBox()
        self.progressBarGroupBoxLayout = QVBoxLayout()
        self.progressBar = QProgressBar()

        ## multiUserTree
        self.infoLabel = QLabel()
        self.multiUserTree = QMultiUserTree()

        ## Buttons
        self.buttonLayout = QHBoxLayout()
        self.validateButton = QPushButton()
        self.resetButton = QPushButton()
        
        # Layout

        ## Progress bar
        self.progressBarGroupBoxLayout.addWidget(self.progressBar)
        self.progressBarGroupBox.setLayout(self.progressBarGroupBoxLayout)

        ## Buttons

        self.buttonLayout.addWidget(self.resetButton)
        self.buttonLayout.addWidget(self.validateButton)
        self.buttonLayout.addStretch()

        self.mainLayout.addWidget(self.infoLabel)
        self.mainLayout.addWidget(self.multiUserTree)
        self.mainLayout.addWidget(self.progressBarGroupBox)
        self.mainLayout.addLayout(self.buttonLayout)
        self.setLayout(self.mainLayout)

        # Settings
        uim = QUIManager()
        self.setWindowTitle("Commande groupée")
        self.setWindowIcon(uim.getIcon("group"))
        self.setFixedSize(1200, 800)
        self.infoLabel.setText("Présenter les cartes sur le lecteur pour les ajouter à la transaction")
        self.progressBarGroupBox.setTitle("Progression")
        self.validateButton.setText("Payer")
        self.resetButton.setText("RÀZ")

    def addUser(self):
        self.multiUserTree.addUser()
        


class QCounterTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        dm = QDataManager()

        # Definition
        self.mainLayout = QHBoxLayout()

        # Left pannel
        self.productSelectionLayout = QVBoxLayout()
        self.searchBar = QSearchBar()
        self.itemSelector = QProductSelector(dm.productDict)

        # Mid pannel
        self.basket = QBasket()

        # Right pannel
        self.rightPannelLayout = QVBoxLayout()  # find a better name ~
        self.systemInfo = None
        self.nfcInfo = QNFCInfo()
        self.history = QBuyingHistory()
        self.validateButtonLayout = QHBoxLayout()
        self.multiUserButton = QPushButton()
        self.singleUserButton = QPushButton()

        self.multiUserPannel: QMultiUserPannel = None

        # Layout
        # left pannel
        self.productSelectionLayout.addWidget(self.searchBar)
        self.productSelectionLayout.addWidget(self.itemSelector)

        # Mid pannel

        # Right pannel

        self.rightPannelLayout.addWidget(self.systemInfo)
        self.rightPannelLayout.addWidget(self.nfcInfo)
        self.rightPannelLayout.addWidget(self.history)
        self.rightPannelLayout.addLayout(self.validateButtonLayout)

        self.validateButtonLayout.addWidget(self.multiUserButton)
        self.validateButtonLayout.addWidget(self.singleUserButton)

        # main layout
        self.mainLayout.addLayout(self.productSelectionLayout)
        self.mainLayout.addWidget(self.basket)
        self.mainLayout.addLayout(self.rightPannelLayout)
        self.setLayout(self.mainLayout)

        # Settings
        # Left pannel
        # Mid pannel
        # Right pannel
        self.singleUserButton.setText("Valider et payer")
        self.multiUserButton.setText("Plusieurs clients")

        # signals
        self.itemSelector.itemSelected[Product].connect(self.basket.addProduct)
        self.singleUserButton.clicked.connect(self.showNFCDialog)
        self.multiUserButton.clicked.connect(self.showMultiUserPannel)

    def showMultiUserPannel(self):
        printI("Multi user button clicked")
        self.multiUserPannel = QMultiUserPannel()
        nfcm = QNFCManager()
        nfcm.cardInserted.connect(self.multiUserPannel.addUser)
        center(self.multiUserPannel)
        self.multiUserPannel.show()

    def showNFCDialog(self):
        nfcm = QNFCManager()
        if not nfcm.hasCard():
            nfcDialog = QNFCDialog()
            nfcDialog.setModal(True)
            nfcDialog.cardInserted.connect(self.singleUserPay)
            nfcDialog.exec_()
        else:
            self.singleUserPay()

    def singleUserPay(self):
        printI("Single user payment")
        client = Client()
        dm = QDataManager()
        nfcm = QNFCManager()

        productList = self.basket.getProductList()
        if len(productList) == 0:
            warningDialog = QWarningDialog("Aucun article sélectionné", "Aucun article sélectionné", "Veuillez sélectionner un ou plusieurs articles avant de procéder au paiement")
            center(warningDialog)
            warningDialog.exec()
            return

        totalPrice = Eur(0)
        for product in productList:
            totalPrice += product.getPrice() * product.getQuantity()

        distribution = Distribution()
        distribution.addUser(nfcm.getCardUID())
        distribution.addAmount(totalPrice)

        try:
            response = client.requestBuy(
                counter_id=dm.getCounter().getId(), device_uuid=dm.getUID(), payments=distribution, basket=productList,
            )
            if response:
                self.history.addBuying(response)
                self.nfcInfo.update()  # nb: this involve a new request, this is not necessary still the new balance is already in the reply
                # but this is much easier here ...
                self.basket.clear()
            else:
                warningDialog = QWarningDialog(
                    "Solde insuffisant", "Le solde utilisateur est insufisant", "Veuillez recharger votre carte",
                )
                warningDialog.exec_()

        except:
            printE("Something happen, transaction failed. Please try again")

    def multiUserPay(self, distribution):
        pass

