from QTree import *

from PyQt5.QtCore import pyqtSignal
from QNFC import QCardObserver
from smartcard.util import toHexString


class Item(TreeItem):
    def __init__(self, data, parent=None):
        super().__init__(data, parent)
        if "price" not in self.data:
            self.data["price"] = 0
        if "uid" not in self.data:
            self.data["uid"] = ""
        if "icon" not in self.data:
            self.data["icon"] = ""

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childItems):
            return False

        for i in range(0, count):
            data = [QVariant()] * columns
            item = Item(data, self)
            self.childItems.insert(position, item)

        return True


class QUserHistoryModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers)
        self.rootItem = Item(headers)
        self.itemList = []

        buyItem = Item(["Achats", ""], self.rootItem)
        transactionItem = Item(["Transactions", ""], self.rootItem)

        self.rootItem.appendChild(buyItem)
        self.rootItem.appendChild(transactionItem)
        try:
            for i in data:
                i["transactionUID"] = i["id"]

                i["cardUID"] = i["user_UID"]
                i["basket"] = {"Objet": 1}
                if i["shopping_cart"] == []:  # It's a transaction
                    i["text"] = [str(i["id"]), euro(i["amount"])]
                    i["price"] = i["amount"]
                    child = Item(i, transactionItem)
                    transactionItem.appendChild(child)
                else:  # It's a buy
                    i["text"] = [str(i["id"]), euro(-i["amount"])]
                    i["price"] = -i["amount"]
                    child = Item(i, buyItem)
                    buyItem.appendChild(child)
                # self.transactionList[i["id"]] = i
        except:
            pass


class QItemSelectorModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        # super(QTreeModel,self).__init__(parent) #Weird but seems ok
        super().__init__(headers)  # Weird but seems ok

        self.rootItem = Item(headers)
        self.itemList = []  # List of Item
        # self.itemDict = {}  # Dictionary of final node only classed by id item : DEPRECIATED

        if data is not None:
            self.setupModelData(data, self.rootItem)
        # self.__disp(self.rootItem)

        itemRegister = QItemRegister()
        itemRegister.priceUpdated[QVariant].connect(self.updatePrice)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role == Qt.DecorationRole:
            if index.column() == 0:
                try:
                    return QPixmap("ressources/icones/" + index.internalPointer().getText(0) + ".png")
                except:
                    pass  # No picture found
        if role == Qt.ToolTipRole:
            try:
                return index.internalPointer().data["uid"]
            except:
                pass

        if role == Qt.ForegroundRole:
            try:
                item = index.internalPointer()
                uid = item.getData("uid")
                itemRegister = QItemRegister()
                if item.getData()["price"] != itemRegister.getItems(uid)["defaultPrice"]:
                    if index.column() > 0:
                        return QColor(88, 231, 167)
            except:
                pass

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.getText(index.column())

    def setupModelData(self, data, parent):

        if isFinalNode(data) is False:
            for i in data:
                text = len(self.rootItem.getText()) * [""]  # Create an array as as self.rootItem.getData()
                text[0] = i
                item = Item(text, parent)
                item.data["name"] = i
                parent.appendChild(item)
                self.setupModelData(data[i], item)
        else:
            uid = data["uid"]
            price = data["defaultPrice"]

            parent.data["uid"] = uid
            parent.data["price"] = price
            parent.data["text"] = [parent.data["name"], euro(price)]

            # self.itemDict[uid] = {"price": price, "name": parent.data["name"]} # Depreciated

            # newParent = copy.deepcopy(parent) #?
            self.itemList.append(parent)

    def __disp(self, parent):

        for child in parent.childItems:
            print(child.getText(0))
            self.__disp(child)

    def updatePrice(self, uid):
        try:
            itemRegister = QItemRegister()
            itemDict = itemRegister.getItems()
            model = self
            index = model.index(-1, -1)  # get root item
            n_row = model.rowCount(QModelIndex())

            indexList = []
            self.__getFinalIndexes(QModelIndex(), indexList)

            for child in indexList:
                if child.internalPointer().data["uid"] == uid:

                    child.internalPointer().data["price"] = itemDict[uid]["currentPrice"]
                    child.internalPointer().data["text"][1] = euro(itemDict[uid]["currentPrice"])
                    model.setData(model.index(0, 1, child.parent()), euro(child.internalPointer().data["text"][1]), Qt.EditRole)

            # self.treeView.doubleClicked[QModelIndex].connect(self.selectItem)
        except:
            pass

    def __getFinalIndexes(self, parent, indexList):

        model = self
        index = model.index(0, 0, parent)
        n_row = model.rowCount(index.parent())

        for i in range(n_row):
            child = model.index(i, 0, parent)
            if child.internalPointer().getData("uid") != "":
                indexList.append(child)
            else:
                self.__getFinalIndexes(child, indexList)


class QBarHistoryModel(QItemSelectorModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers)
        self.rootItem = TreeItem(headers)

    def data(self, index, role):
        observer = QCardObserver()
        cardUID = observer.cardUID

        if not index.isValid():
            return None

        if role == Qt.ToolTipRole:
            text = ""
            basket = index.internalPointer().data["basket"]
            text += str(index.internalPointer().data["transactionUID"]) + "\n"
            for i in basket:
                text += str(i) + (1 + int(5 / len(str(i)))) * "\t" + str(basket[i]) + "\n"

            # TODO: Find a better way to format this text (Align item with qty)

            text = text[:-1]  # Delete the last '\n'
            return text

        try:
            #         if role == Qt.ForegroundRole and toHexString(cardUID) == index.internalPointer().data["cardUID"]:
            #             return QColor(Qt.white)

            if role == Qt.BackgroundColorRole and toHexString(cardUID) == index.internalPointer().data["cardUID"]:
                # return QColor(Qt.green)
                return QColor(88, 231, 167)
        except:
            pass

        if role != Qt.DisplayRole:
            return None
        item = index.internalPointer()
        return item.getText(index.column())


class QTransactionHistoryModel(QItemSelectorModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers)
        self.rootItem = TreeItem(headers)

    def data(self, index, role):
        observer = QCardObserver()
        cardUID = observer.cardUID

        if not index.isValid():
            return None

        if role == Qt.ToolTipRole:
            text = ""
            text += str(index.internalPointer().data["transactionUID"])
            return text

        try:
            #         if role == Qt.ForegroundRole and toHexString(cardUID) == index.internalPointer().data["cardUID"]:
            #             return QColor(Qt.white)

            if role == Qt.BackgroundColorRole and toHexString(cardUID) == index.internalPointer().data["cardUID"]:
                # return QColor(Qt.green)
                return QColor(88, 231, 167)
        except:
            pass

        if role != Qt.DisplayRole:
            return None
        item = index.internalPointer()
        return item.getText(index.column())


class QBuyInfoModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        # super(QTreeModel,self).__init__(parent) #Weird but seems ok
        super().__init__(headers)  # Weird but seems ok

        self.rootItem = TreeItem(headers)
        self.itemList = []  # List of Item
        # self.itemDict = {}  # Dictionary of final node only classed by id item : DEPRECIATED

        if data is not None:
            self.setupModelData(data, self.rootItem)
        # self.__disp(self.rootItem)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.getText(index.column())

    def setupModelData(self, data, parent):

        for i in data["basket"]:
            name = i
            quantity = data["basket"][i]
            text = [name, quantity]
            child = TreeItem(text, parent)
            child.data["text"] = text
            parent.appendChild(child)
            self.itemList.append(child)


class QBasketModel(QItemSelectorModel):

    priceChanged = pyqtSignal()

    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data, parent)
        self.basket = {}

    def data(self, index, role):

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.getText(index.column())

    def updatePrice(self, uid):
        try:
            itemRegister = QItemRegister()
            itemDict = itemRegister.getItems()
            model = self
            index = model.index(-1, -1)  # get root item
            n_row = model.rowCount(QModelIndex())

            indexList = []
            self.__getIndexes(indexList)
            for child in indexList:
                if child.internalPointer().data["uid"] == uid:
                    child.internalPointer().data["price"] = itemDict[uid]["currentPrice"]
            self.priceChanged.emit()
        except:
            pass

    def __getIndexes(self, indexList):
        model = self
        n_row = model.rowCount(QModelIndex())

        for i in range(n_row):
            indexList.append(model.index(i, 0))
