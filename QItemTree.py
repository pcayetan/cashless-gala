from QItemModel import *

from PyQt5.QtCore import pyqtSignal
from QNFC import QCardObserver
from smartcard.util import toHexString

import copy
import json

from Client import *


class QItemSelector(QWidget):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(parent)

        # Definitions
        self.mainVBoxLayout = QVBoxLayout()

        self.treeModel = QItemSelectorModel(headers, data)
        self.treeView = QSuperTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

        # Link
        self.mainVBoxLayout.addWidget(self.treeView)
        self.setLayout(self.mainVBoxLayout)

        # Allow animation while expanding tree
        self.treeView.setAnimated(True)


class QBasket(QWidget):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(parent)

        # Definitions
        self.mainVBoxLayout = QVBoxLayout()

        self.treeModel = QBasketModel(headers, data)
        self.treeView = QSuperTreeView()
        self.totalRowInfo = QRowInfo()

        self.quantityButtonList = []
        self.delButtonList = []
        self.basket = {}

        self.editable = True

        # Settings

        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)
        self.totalRowInfo.addRow("Total", euro(0))
        self.totalPrice = 0

        # Link
        self.treeView.setModel(self.treeModel)

        self.mainVBoxLayout.addWidget(self.treeView)
        self.mainVBoxLayout.addWidget(self.totalRowInfo)
        self.setLayout(self.mainVBoxLayout)

        self.treeModel.priceChanged.connect(self.updateBasket)

    def clearBasket(self):

        buttonList = copy.copy(self.delButtonList)
        for button in buttonList:
            self.deleteItem(button)

    def resizeEvent(self, event):
        """Resize the buttons when the whole window is resized"""
        view = self.treeView

        view.setColumnWidth(3, 48)

    def forceRefresh(self):

        model = self.treeModel
        view = self.treeView
        view.setColumnWidth(0, 100)  # Ultimate force resizing.. it seems that whithout this, resizeColumnToContents does not work every time
        for i in reversed(range(model.columnCount(QModelIndex()))):
            view.resizeColumnToContents(i)  # TODO: FIX THIS SHITY HACK ! I use this because without this the button is not correctly placed
            # UPDATE: ACCORDING TO THIS LINK https://stackoverflow.com/questions/8364061/how-do-you-set-the-column-width-on-a-qtreeview
            # THE SIZE OF THE TREEVIEW MAYBE UPDATED WITH setModel FUNCTION, NOT TRIED YET

    def updateBasket(self):
        self.basket = {}
        totalPrice = 0
        model = self.treeModel
        for row in range(model.rowCount(QModelIndex())):
            index = model.index(row, 2)
            value = index.internalPointer().data["price"]
            uid = index.internalPointer().data["uid"]
            try:
                qte = int(self.quantityButtonList[row].quantityEditLine.text())
            except:
                qte = 0

            totalPrice += value * qte
            model.setData(index, euro(value * qte), Qt.EditRole)
            self.basket[uid] = qte

        self.totalRowInfo.setRow(0, 1, euro(totalPrice))  # Display the total price
        self.totalPrice = totalPrice  # store the total price as a number

        self.forceRefresh()

    def hasProductUID(self, uid):

        index = self.treeModel.index(-1, -1, QModelIndex())
        model = self.treeModel
        n_child = model.rootItem.childCount()
        n_column = model.columnCount(index)

        for i in range(0, n_child):
            if model.index(i, 0).internalPointer().data["uid"] == uid:
                return i

        return -1

    def selectItem(self, item):
        data = item.internalPointer().getText()
        if len(data) > 1:  # If that's an end node (category don't have price)
            if data[1] != "":
                model = self.treeModel

                if self.hasProductUID(item.internalPointer().data["uid"]) == -1:  # if the selected item already exist in the basket
                    if not model.insertRow(0, QModelIndex()):  # Create a new item at the top
                        return

                    # Definitions of  delete button

                    delButton = QDelButton()
                    self.delButtonList.insert(0, delButton)

                    # Definition of quantity button

                    quantityButton = QQuantity()
                    self.quantityButtonList.insert(0, quantityButton)

                    # Get the item we just created above
                    child = model.index(0, 0)
                    child.internalPointer().data["price"] = item.internalPointer().data["price"]
                    child.internalPointer().data["uid"] = item.internalPointer().data["uid"]
                    price = euro(quantityButton.quantity * item.internalPointer().data["price"])
                    child.internalPointer().data["text"] = [item.internalPointer().getText(0), "", price]

                    quantityButton.quantityChanged.connect(self.updateBasket)
                    delButton.deleted[QToolButton].connect(self.deleteItem)

                    self.treeView.setIndexWidget(model.index(0, 1), quantityButton)
                    self.treeView.setIndexWidget(model.index(0, 3), delButton)

                    self.forceRefresh()
                else:
                    row = self.hasProductUID(item.internalPointer().data["uid"])
                    self.quantityButtonList[row].incQuantity()

                self.updateBasket()

    def loadBasket(self, basket):

        model = self.treeModel

        for item in basket:

            if not model.insertRow(0, QModelIndex()):  # Create a new item at the top
                return

            # Definitions of  delete button

            delButton = QDelButton()
            self.delButtonList.insert(0, delButton)

            # Definition of quantity button

            quantityButton = QQuantity()
            quantityButton.setQuantity(basket[item])
            self.quantityButtonList.insert(0, quantityButton)

            # Get the item we just created above
            child = model.index(0, 0)
            child.internalPointer().data["price"] = item["price"]
            child.internalPointer().data["uid"] = item
            price = euro(quantityButton.quantity * item["price"])
            child.internalPointer().data["text"] = [item["name"], "", price]

            quantityButton.quantityChanged.connect(self.updateBasket)
            delButton.deleted[QToolButton].connect(self.deleteItem)

            self.treeView.setIndexWidget(model.index(0, 1), quantityButton)
            self.treeView.setIndexWidget(model.index(0, 3), delButton)

        self.forceRefresh()

    def deleteItem(self, delButton):

        index = self.delButtonList.index(delButton)
        model = self.treeModel

        self.quantityButtonList.pop(index)
        self.delButtonList.pop(index)
        model.removeRow(index, QModelIndex())

        self.updateBasket()

    def setEditable(self, tof):
        self.editable = tof

    def keyPressEvent(self, event):
        try:
            # TODO: Set multiple selection/deletion possible
            if event.key() == Qt.Key_Delete:
                row = self.treeView.selectedIndexes()[0].row()
                button = self.delButtonList[row]
                self.deleteItem(button)
        except:
            print("Delete item: No item selected")


class QAbstractHistory(QWidget):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(parent)

        # Definitions

        self.transactionInfo = QBuyInfoDialog  # Not instancied on purpose

        self.mainVBoxLayout = QVBoxLayout()

        self.treeView = QSuperTreeView()

        self.transactionList = {}
        self.historyFileName = "defaultHistory.json"

        self.recoverHistory()

        # Settings

        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

        # Link
        self.treeView.setModel(self.treeModel)
        self.mainVBoxLayout.addWidget(self.treeView)
        self.setLayout(self.mainVBoxLayout)

        observer = QCardObserver()
        observer.cardInserted.connect(self.forceRefresh)
        observer.cardRemoved.connect(self.forceRefresh)

        self.treeView.doubleClicked[QModelIndex].connect(self.showTransactionInfo)

    def showTransactionInfo(self, modelIndex):

        if modelIndex.internalPointer().childCount() == 0:

            self.transactionInfo = QBuyInfoDialog(modelIndex)
            self.transactionInfo.cancelButton.clicked.connect(self.removeSelectedTransaction)

            # self.transactionInfo.setWindowTitle("Information transaction")
            self.transactionInfo.forceRefresh()

            self.transactionInfo.show()
            center(self.transactionInfo)

    def removeSelectedTransaction(self):

        model = self.treeModel
        index = self.transactionInfo.selectedIndex
        connector = QConnector()
        try:
            if self.transactionInfo.cancelTransaction() is False:
                return
            uid = index.internalPointer().data["transactionUID"]
            try:
                del self.transactionList[uid]
                with open(self.historyFileName, "w") as file:
                    json.dump(self.transactionList, file)
            except:
                pass
            if not model.removeRows(index.row(), 1, index.parent()):
                connector.statusBarshowMessage("Échec de suppression de la transaction")
            else:
                connector.statusBarshowMessage("Suppression de la transaction")

        except:
            popUp = QErrorDialog("Échec de l'opération", "Transaction introuvable", "Il semble que cette transaction ait déjà été annulée")
            center(popUp)
            popUp.exec()
            print("ERROR: Unable to remove transaction")

    def forceRefresh(self):

        model = self.treeModel
        view = self.treeView
        view.setColumnWidth(0, 100)  # Ultimate force resizing.. it seems that whithout this, resizeColumnToContents does not work every time
        for i in reversed(range(model.columnCount(QModelIndex()))):
            view.resizeColumnToContents(i)  # TODO: FIX THIS SHITY HACK ! I use this because without this the button is not correctly placed
            # UPDATE: ACCORDING TO THIS LINK https://stackoverflow.com/questions/8364061/how-do-you-set-the-column-width-on-a-qtreeview
            # THE SIZE OF THE TREEVIEW MAYBE UPDATED WITH setModel FUNCTION, NOT TRIED YET


class QUserHistory(QAbstractHistory):
    def __init__(self, headers, data=None, parent=None):
        self.treeModel = QUserHistoryModel(headers, data)
        super().__init__(headers, data, parent)
        self.treeView.expandAll()
        self.forceRefresh()
        self.setWindowTitle("Historique utilisateur")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))

    def recoverHistory(self):
        pass

    def showTransactionInfo(self, modelIndex):

        if modelIndex.internalPointer().childCount() == 0:

            if modelIndex.parent().row() == 0:  # If it's in the buy section

                self.transactionInfo = QBuyInfoDialog(modelIndex)
                self.transactionInfo.cancelButton.clicked.connect(self.removeSelectedTransaction)

                self.transactionInfo.forceRefresh()
                self.transactionInfo.setWindowTitle("Information transaction")

                self.transactionInfo.show()
                center(self.transactionInfo)
            elif modelIndex.parent().row() == 1:  # If it's a transaction (refilling)

                self.transactionInfo = QTransactionInfoDialog(modelIndex)
                self.transactionInfo.cancelButton.clicked.connect(self.removeSelectedTransaction)

                self.transactionInfo.setWindowTitle("Information transaction")
                if self.transactionInfo.treeModel:
                    self.transactionInfo.forceRefresh()

                self.transactionInfo.show()
                center(self.transactionInfo)


class QBarHistory(QAbstractHistory):
    def __init__(self, headers, data=None, parent=None):

        self.treeModel = QBarHistoryModel(headers, data)  # Must be set before super
        super().__init__(headers, data, parent)

        # Definitions
        config = MachineConfig()
        self.historyFileName = "counterHistory.json"

    def showTransactionInfo(self, modelIndex):

        observer = QCardObserver()

        self.transactionInfo = QBuyInfoDialog(modelIndex)
        self.transactionInfo.cancelButton.clicked.connect(self.removeSelectedTransaction)

        self.transactionInfo.setWindowTitle("Information transaction")
        self.transactionInfo.forceRefresh()

        self.transactionInfo.show()
        center(self.transactionInfo)

    def recoverHistory(self, historyFile=None):

        response = requestComputerHistory(MAC, -1)

        if response:
            print("History downloaded")
            history = {}
            for i in response:
                if i["amount"] < 0:  # if it's a buy
                    basket = {}
                    for j in i["shopping_cart"]:
                        basket[j["product_code"]] = j["quantity"]

                    # TODO: Serialize the time on the SERVER OR use the standard function for parse string-> datetime parsing
                    # Please close your eyes here ...
                    time = i["time"].split(" ")[4]
                    history[i["id"]] = {"cardUID": i["user_UID"], "basket": basket, "price": -i["amount"], "time": time}
                else:  # if it's a refilling
                    pass
        else:
            print("Local history loaded")
            if historyFile is None:
                historyFile = self.historyFileName
            try:
                with open(historyFile, "r") as file:
                    history = json.load(file)
            except:
                print("WARNING: Can't read the file", historyFile)

        try:
            for i in history:
                self.addTransaction(i, history[i])
        except:
            pass

    def addTransaction(self, uid, transaction):

        model = self.treeModel

        self.transactionList[uid] = transaction  # {"cardUID:0","basket:{"objet":qte,...},"price":0"}
        with open(self.historyFileName, "w") as file:
            json.dump(self.transactionList, file)

        if not model.insertRow(0, QModelIndex()):
            return

        child = model.index(0, 0)
        cardUID = transaction["cardUID"]
        price = transaction["price"]
        child.internalPointer().data["basket"] = transaction["basket"]
        child.internalPointer().data["cardUID"] = cardUID
        child.internalPointer().data["transactionUID"] = uid
        child.internalPointer().data["price"] = price
        # TODO: Ask the transaction time to the server, else if the client has to reboot, the printed time will be wrong
        h, m, s = QTime.currentTime().hour(), QTime.currentTime().minute(), QTime.currentTime().second()
        child.internalPointer().data["time"] = transaction["time"]
        child.internalPointer().data["text"] = [cardUID.replace(" ", ""), euro(price), ""]
        self.forceRefresh()


class QTransactionHistory(QAbstractHistory):
    def __init__(self, headers, data=None, parent=None):

        self.treeModel = QTransactionHistoryModel(headers, data)  # Must be set before super
        super().__init__(headers, data, parent)
        self.historyFileName = "transactionHistory.json"

        # Definitions
        config = MachineConfig()
        self.historyFileName = "transactionHistory.json"

    def showTransactionInfo(self, modelIndex):

        observer = QCardObserver()

        self.transactionInfo = QTransactionInfoDialog(modelIndex)
        self.transactionInfo.cancelButton.clicked.connect(self.removeSelectedTransaction)

        self.transactionInfo.setWindowTitle("Information transaction")
        if self.transactionInfo.treeModel:
            self.transactionInfo.forceRefresh()

        self.transactionInfo.show()
        center(self.transactionInfo)

    def recoverHistory(self, historyFile=None):

        response = requestComputerHistory(MAC, -1)

        if response:
            print("History downloaded")
            history = {}
            for i in response:
                if i["amount"] > 0:  # if it's a credit
                    basket = {}
                    for j in i["shopping_cart"]:
                        basket[j["product_code"]] = j["quantity"]
                    history[i["id"]] = {"cardUID": i["user_UID"], "price": i["amount"]}
                else:  # if it's a refilling
                    pass
        else:
            print("Local history loaded")
            if historyFile is None:
                historyFile = self.historyFileName
            try:
                with open(historyFile, "r") as file:
                    history = json.load(file)
            except:
                print("WARNING: Can't read the file", historyFile)

        try:
            for i in history:
                self.addTransaction(i, history[i])
        except:
            pass

    def addTransaction(self, uid, transaction):

        model = self.treeModel

        self.transactionList[uid] = transaction  # {"cardUID:0","basket:{"objet":qte,...},"price":0"}
        with open(self.historyFileName, "w") as file:
            json.dump(self.transactionList, file)

        if not model.insertRow(0, QModelIndex()):
            return

        child = model.index(0, 0)
        cardUID = transaction["cardUID"]
        price = transaction["price"]
        child.internalPointer().data["cardUID"] = cardUID
        child.internalPointer().data["transactionUID"] = uid
        child.internalPointer().data["price"] = price
        child.internalPointer().data["text"] = [cardUID.replace(" ", ""), euro(price), ""]
        self.forceRefresh()


class QAbstractInfoDialog(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)

        self.selectedIndex = index
        self.transaction = index.internalPointer().getData()
        # Definitions

        self.treeView = None
        self.treeModel = None

        self.mainGridLayout = QGridLayout()

        self.infoGroupBox = QGroupBox()
        self.infoVBoxLayout = QVBoxLayout()
        self.info = QRowInfo()
        self.cancelButton = QPushButton()

        # Settings

        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.infoGroupBox.setTitle("Informations transaction")

        self.cancelButton.setText("Annuler transaction")

        # Link

        self.infoVBoxLayout.addWidget(self.info)
        self.infoVBoxLayout.addWidget(self.cancelButton)
        self.infoGroupBox.setLayout(self.infoVBoxLayout)

        self.mainGridLayout.addWidget(self.infoGroupBox, 0, 1)
        self.setLayout(self.mainGridLayout)

    #        self.cancelButton.clicked.connect(self.cancelTransaction)

    def cancelTransaction(self):

        config = MachineConfig()
        observer = QCardObserver()
        connector = QConnector()

        if toHexString(observer.cardUID) == self.transaction["cardUID"]:
            response = requestRefund(self.transaction["transactionUID"], config.counterID, MAC)
            connector.updateBalanceInfo(response["user_balance"])
            print("Transaction canceled, new balance ", euro(response["user_balance"]))

            self.hide()
            if response:
                return True
            else:
                return False
        else:
            self.transactionInfoWarning = QMessageBox(QMessageBox.Information, "Authentification requise", "Veuillez présenter la carte concernée par la transaction", QMessageBox.Ok)
            self.transactionInfoWarning.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
            self.transactionInfoWarning.button(QMessageBox.Ok).clicked.connect(self.transactionInfoWarning.hide)
            self.transactionInfoWarning.show()
            center(self.transactionInfoWarning)
            return False


class QBuyInfoDialog(QAbstractInfoDialog):
    def __init__(self, index, parent=None):
        super().__init__(index, parent)
        # Definitions

        self.treeView = QSuperTreeView()
        self.treeModel = QBuyInfoModel(["Article", "Quantité"], self.transaction)

        # Settings
        self.info.addRow("UID transaction", self.transaction["transactionUID"])
        self.info.addRow("Prix du panier", euro(self.transaction["price"]))
        self.info.addRow("UID carte", self.transaction["cardUID"])
        self.info.addRow("Heure transaction", self.transaction["time"])

        # Link

        self.mainGridLayout.addWidget(self.treeView, 0, 0)
        self.treeView.setModel(self.treeModel)

    def forceRefresh(self):

        model = self.treeModel
        view = self.treeView
        view.setColumnWidth(0, 100)  # Ultimate force resizing.. it seems that whithout this, resizeColumnToContents does not work every time
        for i in reversed(range(model.columnCount(QModelIndex()))):
            view.resizeColumnToContents(i)  # TODO: FIX THIS SHITY HACK ! I use this because without this the button is not correctly placed
            # UPDATE: ACCORDING TO THIS LINK https://stackoverflow.com/questions/8364061/how-do-you-set-the-column-width-on-a-qtreeview
            # THE SIZE OF THE TREEVIEW MAYBE UPDATED WITH setModel FUNCTION, NOT TRIED YET


class QTransactionInfoDialog(QAbstractInfoDialog):
    def __init__(self, index, parent=None):
        super().__init__(index, parent)

        # Settings
        self.info.addRow("UID transaction", self.transaction["transactionUID"])
        self.info.addRow("Montant", euro(self.transaction["price"]))
        self.info.addRow("UID carte", self.transaction["cardUID"])


class QDelButton(QToolButton):

    deleted = pyqtSignal(QToolButton)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.row = -1
        self.clicked.connect(self.delete)

        self.setIcon(QIcon("ressources/icones/delete.png"))
        self.setIconSize(QSize(32, 32))
        self.setFixedSize(QSize(48, 48))

    def setRow(self, row):
        self.row = row

    def getRow(self):
        return self.row

    def delete(self):
        self.deleted.emit(self)


class QQuantity(QWidget):

    quantityChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Definition
        self.mainHBoxLayout = QHBoxLayout()
        self.minusButton = QToolButton()
        self.quantityEditLine = QAutoSelectLineEdit()
        self.plusButton = QToolButton()
        self.quantity = 1

        # Settings
        self.minusButton.setText("-")

        self.quantityEditLine.setText("1")
        self.quantityEditLine.setAlignment(Qt.AlignHCenter)
        self.quantityEditLine.setFixedWidth(50)

        self.plusButton.setText("+")

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # Link

        self.mainHBoxLayout.addWidget(self.minusButton)
        self.mainHBoxLayout.addWidget(self.quantityEditLine)
        self.mainHBoxLayout.addWidget(self.plusButton)
        self.setLayout(self.mainHBoxLayout)

        self.plusButton.clicked.connect(self.incQuantity)
        self.minusButton.clicked.connect(self.decQuantity)
        self.quantityEditLine.textChanged.connect(self.editingFinished)
        self.quantityEditLine.editingFinished.connect(self.__noBlank)

    def incQuantity(self):
        self.quantity += 1
        self.quantityEditLine.setText(str(self.quantity))
        self.quantityEditLine.editingFinished.emit()
        # self.quantityChanged.emit()

    def decQuantity(self):
        self.quantity -= 1
        if self.quantity > 0:
            self.quantityEditLine.setText(str(self.quantity))
            self.quantityEditLine.editingFinished.emit()
        else:
            self.quantity = 1

    def editingFinished(self):
        try:
            self.quantity = int(self.quantityEditLine.text())
        except:
            self.quantity = 1
            if self.quantityEditLine.text() != "":
                self.quantityEditLine.setText("1")

        if self.quantity >= 1:
            self.quantityChanged.emit()
        else:
            self.quantityEditLine.setText("1")
            self.quantity = 1
            popUp = QErrorDialog("Erreur de saisie", "Quantité invalide", "Veuillez saisir un nombre entier positif non nul")
            # center(popUp)
            popUp.exec()

    def __noBlank(self):
        stripedText = self.quantityEditLine.text().strip()
        self.quantityEditLine.setText(stripedText)

        if self.quantityEditLine.text() == "":
            self.quantity = 1
            self.quantityEditLine.setText("1")

    def setQuantity(self, qty):
        try:
            self.quantity = int(qty)
            self.quantityEditLine.setText(str(qty))
            self.quantityChanged.emit()
        except ValueError:
            print("ERROR: ", qte, " is not a number")


class QAutoSelectLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class QSuperTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusOutEvent(self, event):
        self.setCurrentIndex(QModelIndex())
