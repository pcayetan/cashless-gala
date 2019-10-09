import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

from QNFC import *
from QUtils import *
from QItemTree import *

from Client import *

import json

import copy

PWD = os.getcwd() + "/"


def setFont(Widget, Font):

    for child in Widget.children():
        try:
            child.setFont(Font)
            setFont(child, Font)
        except:
            pass
        # TODO: Find a better way to do this
        if isinstance(child, QTreeView):  # Dirty hack to correct oversizing
            child.resizeColumnToContents(0)


class QAutoCompleteLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QCompleter()
        self.setCompleter(self.completer)
        self.model = QStringListModel()
        self.completer.setModel(self.model)


class QInfoNFC(QGroupBox):
    """Display some basics info about the NFC card """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Definitions
        self.mainVBoxLayout = QVBoxLayout()
        #        self.frameGroupBox=QGroupBox()
        self.RowInfo = QRowInfo()

        # Link
        #        self.frameGroupBox.setLayout(self.mainVBoxLayout)
        self.setLayout(self.mainVBoxLayout)
        self.mainVBoxLayout.addWidget(self.RowInfo)

        # settings

        self.setTitle("Lecteur NFC")
        self.RowInfo.addRow("Solde", euro(0))
        self.RowInfo.addRow("UID", "00 00 00 00 00 00 00")

        nfcObserver = QCardObserver()
        #  print(nfcObserver)

        nfcObserver.cardInserted.connect(self.addCard)
        nfcObserver.cardRemoved.connect(self.removeCard)

    def addCard(self):
        observer = QCardObserver()
        if observer.cardUID[-2:] == [0x63, 0x00]:
            print("Erreur de lecture, veuillez réessayer")
        self.RowInfo.setRow(1, 1, toHexString(observer.cardUID))

    def removeCard(self):
        observer = QCardObserver()
        self.RowInfo.setRow(1, 1, toHexString(observer.cardUID))


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


class QCounter(QWidget):
    def __init__(self, parent=None):
        itemRegister = QItemRegister()
        super().__init__(parent)
        ###TOOLS###
        self.jsonFileName = "ItemModel.json"

        ###Definition###

        self.mainGridLayout = QGridLayout()
        # Order definition (left pannel)
        self.orderVBoxLayout = QVBoxLayout()
        self.orderGroupBox = QGroupBox()
        self.basketTree = QBasket(["Articles", "Quantité", "Prix total", ""])

        # ProductSelection definition (middle pannel)
        self.productSelectionVBoxLayout = QVBoxLayout()
        self.productSelectionGroupBox = QGroupBox()
        self.searchBar = QSearchBar()
        self.productTree = QItemSelector(["Articles", "Prix"], self.__getItemDictionary("ItemModel.json"))

        # infoNFC definition (right pannel)

        self.paymentVBoxLayout = QVBoxLayout()
        self.infoNFC = QInfoNFC()
        self.GroupBoxHistory = QGroupBox()
        self.historyTree = QBarHistory(["UID", "Prix"])
        self.NFCDialog = QNFCDialog()
        self.ButtonValidateOrder = QPushButton()

        ###Link###
        self.setLayout(self.mainGridLayout)

        # Order pannel

        self.orderVBoxLayout.addWidget(self.basketTree)
        self.orderGroupBox.setLayout(self.orderVBoxLayout)
        self.mainGridLayout.addWidget(self.orderGroupBox, 0, 0, 2, 1)

        # Product Selection pannel
        self.productSelectionVBoxLayout.addWidget(self.searchBar)
        self.productSelectionVBoxLayout.addWidget(self.productTree)
        self.productSelectionGroupBox.setLayout(self.productSelectionVBoxLayout)
        self.mainGridLayout.addWidget(self.productSelectionGroupBox, 0, 1, 2, 1)

        # self.productTree.setBasket(self.basketTree)

        self.searchBar.inputLine.returnPressed.connect(self.lineSelect)
        self.searchBar.pushButton.clicked.connect(self.lineSelect)

        self.productTree.treeView.doubleClicked[QModelIndex].connect(self.basketTree.selectItem)

        # Payment pannel

        self.GroupBoxHistory.setLayout(self.historyTree.layout())

        self.paymentVBoxLayout.addWidget(self.infoNFC)
        self.paymentVBoxLayout.addWidget(self.GroupBoxHistory, 2)
        self.mainGridLayout.addLayout(self.paymentVBoxLayout, 0, 2)
        self.mainGridLayout.addWidget(self.ButtonValidateOrder, 1, 2)
        self.ButtonValidateOrder.clicked.connect(self.OpenNFCDialog)

        self.NFCDialog.cardInserted.connect(self.payement)

        ###Settings###
        # Order pannel
        self.orderGroupBox.setTitle("Panier")

        # Product Selection pannel
        self.productSelectionGroupBox.setTitle("Sélection des articles")
        self.searchBar.inputLine.model.setStringList(self.__getItemList())

        # NFC & History space

        self.GroupBoxHistory.setTitle("Historique")

        self.ButtonValidateOrder.setText("Valider et payer")
        self.ButtonValidateOrder.setFixedHeight(50)

        # Payement
        self.NFCDialog.blockSignals(True)

    def lineSelect(self):  # Probably one of my ugliest functions... T_T
        itemName = self.searchBar.inputLine.text()
        basketModel = self.basketTree.treeModel
        productModel = self.productTree.treeModel

        n_row = basketModel.rootItem.childCount()
        index = -1
        for i in range(n_row):
            if basketModel.index(i, 0).internalPointer().data["uid"] == itemName.split(",", 1)[0]:
                index = i
                try:
                    currentValue = int(self.basketTree.quantityButtonList[i].quantityEditLine.text())
                    value = int(itemName.split(",", 1)[1])
                    self.basketTree.quantityButtonList[i].quantityEditLine.setText(str(currentValue + value))
                except:
                    self.basketTree.quantityButtonList[i].incQuantity()

        if index < 0:
            #                print(productModel.itemDict)
            try:
                itemName = itemName.split(",", 1)  # itemName is actualy an item ID

                #                    itemName=itemName.split('x',1)

                if len(itemName) > 1:
                    quantity = int(itemName[1])
                else:
                    quantity = 1

                itemName = itemName[0].strip()

                if quantity <= 0:
                    print('ERROR: quantity "' + str(quantity) + '" invalid')
                    QTimer.singleShot(10, self.searchBar.clearText)
                    # The timer is helpfull here because it ensure the text is set BEFORE clearing it
                    return None
                itemRegister = QItemRegister()
                itemRegister.getItems()[itemName]  # Trick to test if itemName exist
                basketModel.insertRow(0)
                child = basketModel.index(0, 1, QModelIndex())
                child.internalPointer().data["uid"] = itemName
                child.internalPointer().data["price"] = itemRegister.getItems()[itemName]["currentPrice"]
            except:
                print("ERROR: Item unknown")
                QTimer.singleShot(10, self.searchBar.clearText)
                # The timer is helpfull here because it ensure the text is set BEFORE clearing it
                return None

            delButton = QDelButton()
            # delButton.setText("x")
            delButton.setIcon(QIcon("ressources/icones/delete.png"))
            delButton.setIconSize(QSize(32, 32))
            delButton.setFixedSize(QSize(48, 48))

            quantityButton = QQuantity()
            #                currentQuantity=int(quantityButton.quantityEditLine.text())
            quantityButton.quantityEditLine.setText(str(quantity))

            self.basketTree.quantityButtonList.insert(0, quantityButton)
            self.basketTree.delButtonList.insert(0, delButton)

            quantityButton.quantityChanged.connect(self.basketTree.updateBasket)
            delButton.deleted[QToolButton].connect(self.basketTree.deleteItem)

            self.basketTree.treeView.setIndexWidget(child, quantityButton)
            self.basketTree.treeView.setIndexWidget(basketModel.index(0, 3), delButton)

            for column in range(basketModel.columnCount(QModelIndex())):  # TODO: This part a quiet DIRTY

                child = basketModel.index(0, column)
                if column == 0:
                    basketModel.setData(child, itemRegister.getItems()[itemName]["name"], Qt.EditRole)
                if column == 2:
                    basketModel.setData(child, euro(float(quantityButton.quantityEditLine.text()) * itemRegister.getItems()[itemName]["currentPrice"]), Qt.EditRole)

            self.basketTree.forceRefresh()

        QTimer.singleShot(10, self.searchBar.clearText)  # The timer is helpfull here because it ensure the text is set BEFORE clearing it
        self.basketTree.updateBasket()

    def __getItemList(self):
        itemList = []
        self.__parseDictionary(self.__getItemDictionary(self.jsonFileName), itemList)
        return itemList

    def __getItemDictionary(self, jsonFileName):
        try:
            with open(jsonFileName, "r") as file:
                return json.load(file)
        except:
            # rise some error:
            print("ERROR: Can't read the file", jsonFileName)

    def __parseDictionary(self, data, itemList):
        if isFinalNode(data) is False:
            for i in data:
                if isFinalNode(data[i]) is True:
                    data[i]["name"] = i
                self.__parseDictionary(data[i], itemList)
        else:
            itemList.append(data["uid"])

    def OpenNFCDialog(self):
        cardHandler = QCardObserver()
        if not self.NFCDialog.isVisible():
            if not cardHandler.hasCard():
                center(self.NFCDialog)
                self.NFCDialog.blockSignals(False)
                self.NFCDialog.show()
            else:
                self.payement()
                print("Carte déjà présente sur le lecteur")

        else:
            print("Widget déjà ouvert")

    def payement(self):
        observer = QCardObserver()
        cardUID = observer.cardUID
        print("payement:", MAC, toHexString(cardUID), self.basketTree.basket)
        success, uuid = requestBuy(MAC, cardUID, self.basketTree.basket)

        if success:
            print("Paiement effectué avec succes")
            transaction = {"cardUID": toHexString(cardUID), "basket": self.basketTree.basket, "price": self.basketTree.totalPrice}
            self.historyTree.addTransaction(uuid, transaction)
            self.basketTree.clearBasket()
        else:
            print("Paiement refusé")


class QCreditCardPayement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Definitions

        self.setTitle("Paiement par carte de crédit")

        self.mainVBoxLayout = QVBoxLayout()
        self.mainGridLayout = QGridLayout()

        self.label = QLabel()
        self.inputLine = QLineEdit()
        self.okButton = QPushButton()

        # Settings

        self.label.setText("Credit:")
        self.okButton.setText("OK")
        self.inputLine.setMaximumWidth(150)
        self.inputLine.setAlignment(Qt.AlignCenter)
        self.inputLine.setText(euro(0))

        # Link

        self.mainGridLayout.addWidget(self.label, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.inputLine, 0, 1, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.okButton, 1, 0, Qt.AlignLeft)

        self.mainVBoxLayout.addLayout(self.mainGridLayout)
        self.mainVBoxLayout.addStretch(1)

        self.setLayout(self.mainVBoxLayout)

        self.inputLine.editingFinished.connect(self.formatInputLine)

    def formatInputLine(self):
        currentText = self.inputLine.text()
        currentText = currentText.replace("€", "").replace(",", ".").replace(" ", "").strip()
        self.inputLine.blockSignals(True)
        try:
            self.inputLine.setText(euro(currentText))
        except:
            self.inputLine.setText(euro(0))

        self.inputLine.blockSignals(False)


class QCashPayement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Paiement par espèce")


class QAEPayement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Paiement par compte AE")


class QNFCPayement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Transfert entre cartes NFC")


class QOtherPayement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Autres moyens de paiement")


class QTransaction(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Definitions

        # Payement type
        self.mainGridLayout = QGridLayout()

        self.payementTypeGroupBox = QGroupBox()
        self.payementTypeLayout = QVBoxLayout()

        self.cashRadio = QRadioButton()
        self.creditCardRadio = QRadioButton()
        self.aeAccountRadio = QRadioButton()
        self.nfcRadio = QRadioButton()
        self.otherRadio = QRadioButton()

        # Payement

        self.payementLayout = QStackedLayout()
        self.creditCardPayement = QCreditCardPayement()
        self.cashPayement = QCashPayement()
        self.nfcPayement = QNFCPayement()
        self.aePayement = QAEPayement()
        self.otherPayement = QOtherPayement()

        # History

        self.historyGroupBox = QGroupBox()
        self.historyLayout = QVBoxLayout()
        self.historyTree = QBarHistory(["UID", "Credit"])

        # settings

        # Payement type
        self.payementTypeGroupBox.setTitle("Moyen de paiement")
        self.cashRadio.setText("Espèces")
        self.creditCardRadio.setText("Carte de crédit")
        self.aeAccountRadio.setText("Compte AE")
        self.nfcRadio.setText("Transfert NFC")
        self.nfcRadio.setToolTip("Permet de transférer des fonds depuis une carte NFC vers une autre")
        self.otherRadio.setText("Autre")
        self.otherRadio.setToolTip("Moyens de paiements indéfinis, créditation pure, offre promo, en nature avec lae bar(maid/man) <3, etc..")

        self.creditCardRadio.setChecked(True)

        # Payement

        # History

        self.historyGroupBox.setTitle("Historique")

        # Link

        # Payement type
        self.payementTypeLayout.addWidget(self.creditCardRadio)
        self.payementTypeLayout.addWidget(self.cashRadio)
        self.payementTypeLayout.addWidget(self.aeAccountRadio)
        self.payementTypeLayout.addWidget(self.nfcRadio)
        self.payementTypeLayout.addWidget(self.otherRadio)

        self.payementTypeGroupBox.setLayout(self.payementTypeLayout)

        self.mainGridLayout.addWidget(self.payementTypeGroupBox, 0, 0)

        # Payement
        self.payementLayout.addWidget(self.creditCardPayement)
        self.payementLayout.addWidget(self.cashPayement)
        self.payementLayout.addWidget(self.aePayement)
        self.payementLayout.addWidget(self.nfcPayement)
        self.payementLayout.addWidget(self.otherPayement)

        self.mainGridLayout.addLayout(self.payementLayout, 1, 0, 2, 1)

        # History
        self.historyLayout.addWidget(self.historyTree)
        self.historyGroupBox.setLayout(self.historyLayout)
        self.mainGridLayout.addWidget(self.historyGroupBox, 0, 1, 3, 1)

        self.setLayout(self.mainGridLayout)

        self.cashRadio.toggled.connect(self.selectCash)
        self.creditCardRadio.toggled.connect(self.selectCreditCard)
        self.aeAccountRadio.toggled.connect(self.selectAE)
        self.nfcRadio.toggled.connect(self.selectNFC)
        self.otherRadio.toggled.connect(self.selectOther)

    def selectCreditCard(self):
        if self.creditCardRadio.isChecked():
            self.payementLayout.setCurrentWidget(self.creditCardPayement)

    def selectCash(self):
        if self.cashRadio.isChecked():
            self.payementLayout.setCurrentWidget(self.cashPayement)

    def selectAE(self):
        if self.aeAccountRadio.isChecked():
            self.payementLayout.setCurrentWidget(self.aePayement)

    def selectNFC(self):
        if self.nfcRadio.isChecked():
            self.payementLayout.setCurrentWidget(self.nfcPayement)

    def selectOther(self):
        if self.otherRadio.isChecked():
            self.payementLayout.setCurrentWidget(self.otherPayement)


class QMainTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        itemRegister = QItemRegister()
        itemRegister.loadItemFile("ItemModel.json")

        # Initialization
        self.TabCounter = QCounter()
        self.TabStock = QTransaction()
        self.TabStat = QWidget()

        # Add tabs
        self.addTab(self.TabCounter, "Comptoir")
        self.addTab(self.TabStock, "Transactions")
        self.addTab(self.TabStat, "Stats")

        self.resize(1200, 800)


class QNFCDialog(QWidget):

    cardInserted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowIcon(QIcon(PWD + "ressources/logoCarte.png"))
        self.mainVBoxLayout = QVBoxLayout()

        Movie = QMovie(PWD + "ressources/Animation2.gif")

        self.card = QLabel()
        self.card.setMovie(Movie)
        Movie.start()

        self.LabelInstruction = QLabel()
        self.LabelInstruction.setText("Veuillez présenter la carte devant le lecteur")

        self.button = QPushButton()
        self.button.setText("Annuler")

        self.mainVBoxLayout.addWidget(self.card)
        self.mainVBoxLayout.addWidget(self.LabelInstruction)
        self.mainVBoxLayout.addWidget(self.button)
        self.setLayout(self.mainVBoxLayout)
        self.setWindowTitle("Paiement")

        self.button.clicked.connect(self.Cancel)

        cardObserver = QCardObserver()
        cardObserver.cardInserted.connect(self.Payement)

    def Cancel(self):
        # Do stuff...
        print("Annuler")
        self.close()

    def Payement(self):
        print("QNFCDialog: Carte détectée")
        self.cardInserted.emit()
        self.blockSignals(True)
        # if(self.CardMonitor.countObservers() > 0):
        #    self.CardMonitor.deleteObserver(self.CardObserver)
        self.close()


class QFakeCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        cardObserver = QCardObserver()

        self.setWindowIcon(QIcon(PWD + "ressources/logoCarte.png"))
        self.mainVBoxLayout = QVBoxLayout()

        self.card = QLabel()
        self.card.setPixmap(QPixmap(PWD + "ressources/logoCarte.png"))

        self.GroupBoxFCEdit = QGroupBox()
        self.GroupBoxFCEdit.setTitle("UID en hexadécimal")
        hbox = QHBoxLayout()
        self.FCEdit = QLineEdit()
        self.FCEdit.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.FCEdit.resize(400, 50)
        hbox.addWidget(self.FCEdit)
        self.GroupBoxFCEdit.setLayout(hbox)

        self.buttonAddCard = QPushButton()
        self.buttonAddCard.setText("Présenter une carte sur le lecteur")
        self.buttonAddCard.clicked.connect(cardObserver.virtualCardInsert)

        self.buttonRemoveCard = QPushButton()
        self.buttonRemoveCard.setText("Enlever la carte du lecteur")
        self.buttonRemoveCard.clicked.connect(cardObserver.virtualCardRemove)

        self.mainVBoxLayout.addWidget(self.card)
        self.mainVBoxLayout.addWidget(self.GroupBoxFCEdit)
        self.mainVBoxLayout.addWidget(self.buttonAddCard)
        self.mainVBoxLayout.addWidget(self.buttonRemoveCard)
        self.setLayout(self.mainVBoxLayout)
        self.setWindowTitle("Simulation")

        self.NFCDialog = None

    def LinkWidget(self, Widget):
        self.LinkedWidget = Widget

    def CloseNFCDialog(self):
        self.LinkedWidget.Payement()


class QMainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gala.Manager.Core")
        self.resize(1200, 800)
        self.setWindowIcon(QIcon(PWD + "ressources/logo.png"))
        center(self)
        self.MainTab = QMainTab()
        self.setCentralWidget(self.MainTab)

        # NFC
        # self.NFCReader=getReaders()[0]

        self.CardMonitor = CardMonitor()
        self.CardObserver = QCardObserver()
        self.CardMonitor.addObserver(self.CardObserver)

        font = QFont()  # TODO: Dirty trick to set the whole app font size
        font.setPointSize(16)
        setFont(self, font)

        # self.CardObserver.cardInserted.connect(self.addCard)
        # self.CardObserver.cardRemoved.connect(self.removeCard)

        # self.MainTab.TabCounter.


class QFadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.Timer = QTimer()
        self.Duration = 250
        self.Interval = 2
        self.Timer.setInterval(self.Interval)
        self.Timer.setTimerType(PyQt5.QtCore.Qt.PreciseTimer)
        self.Timer.timeout.connect(self.Callback)
        self.setWindowOpacity(0)

        self.Timer.start()

        self.Opacity = 0
        self.Count = 0

    def Callback(self):
        self.Opacity = self.Count * self.Interval / self.Duration
        self.Count += 1
        # print(self.Opacity)
        if self.Opacity <= 1:
            self.setWindowOpacity(self.Opacity)
        else:
            self.setWindowOpacity(1)
            self.Timer.stop()
