from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import *

from src.managers.QDataManager import QDataManager
from src.trees.QTree import *

# from Euro import *
from src.managers.Client import Client

# Specialized models ...


class QProductSelectorModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data=data, parent=parent)
        dm = QDataManager()
        self.qProductList = []
        self.setupModelData()
        dm.priceUpdated[Product].connect(self.updatePrice)

    def setupModelData(self):
        dm = QDataManager()
        # print(data)
        # productDict look like this {"root":{"cat1:{"Product":[]}","Product":[]},"Product":[]}

        def exploreDict(productDict, parent: TreeItem):
            # add new categories
            for key in productDict:
                if key != "Product":
                    atom = Atom([key], key)
                    child = TreeItem(QAtom(atom), parent)
                    parent.appendChild(child)
                    exploreDict(productDict[key], child)
            # add products
            for product in productDict["Product"]:
                product.setTexts([product.getName(), product.getPrice()])
                # print(product.getCode())
                qProduct = QProduct(product)
                self.qProductList.append(qProduct)
                child = TreeItem(qProduct, parent)
                parent.appendChild(child)

        exploreDict(dm.productDict, self.rootItem)

    def updatePrice(self, product: Product):
        # We could play with memory tricks so that when it's updated in the manager it's updated here but Master Foo's Zen says:
        # explicit is better that implicit ...
        # So the manager will explicity send update signals to Widgets...
        qProduct = QProduct(product)
        index, item, qAtom = self.searchQAtom(qProduct)

        newPrice = product.getPrice()
        qAtom.setText(str(newPrice), 1)
        qAtom.setPrice(newPrice)

        index0 = self.index(index.row(), 0, index.parent())
        indexN = self.index(index.row(), self.columnCount(), index.parent())
        self.dataChanged.emit(index0, indexN)

    def data(self, index: QModelIndex, role):

        if role == Qt.ForegroundRole:
            # index (QModelIndex), index.internalPointer (TreeItem), --.getData (QAtom)
            qAtom = index.internalPointer().getData()
            if isinstance(qAtom, QProduct):
                qProduct: QProduct = qAtom
                happyHours = qProduct.getHappyHours()
                for happyHour in happyHours:
                    if happyHour.isActive():
                        return QColor(26, 123, 203)

        return super().data(index, role)


class QBasketModel(QTreeModel):
    newProductInserted = pyqtSignal(int, Product)  # row product

    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data=data, parent=parent)
        dm = QDataManager()
        dm.priceUpdated[Product].connect(self.updatePrice)

    def addProduct(self, product: Product, treeView, parent=QModelIndex()):

        qProduct = QProduct(product)  # Create qProduct
        childList = self.rootItem.getChild()
        # get the list of all product already included in the basket
        productList = []
        for child in childList:
            productList.append(child.getData())
        # if the product is already in the basket
        if qProduct in productList:
            # I use my own reseach function because the 'match' function from Qt bases it research on the text field
            # by default, I should reimplement 'match', but I prefer use my own search function
            index, item, data = self.searchQAtom(qProduct)
            data.incQuantity()
            # Tell to Qt that the data changed, since Qt works with column, we need to refresh the whole line
            row = index.row()
            n_column = self.columnCount(parent)
            # WITH THIS, THE DISPLAY IS CORRECTLY REFRESHED, BUT I DON'T KNOW WHY IT WAS NOT WORKING BEFORE !!!
            index0 = self.index(row, 0, parent)
            indexN = self.index(row, n_column, parent)
            self.dataChanged.emit(index0, indexN, [Qt.DisplayRole, Qt.EditRole])

        else:
            # self.productDict[product.getId()] = {'atom':product, 'qAtom':qProduct}
            # Creation of the QAtom
            self.insertRow(0, QModelIndex())  # We insert a row at the top

            # Configuration of the new row
            quantityPannel = qProduct.getQuantityPannel()
            qProduct.addAction("Supprimer", qProduct.delete, "delete")
            treeView.setIndexWidget(self.index(0, 1), quantityPannel)
            delButton = qProduct.getDelButton()
            treeView.setIndexWidget(self.index(0, 3), delButton)

            newIndex = self.index(0, 0)
            self.setData(newIndex, qProduct)

            qProduct.updated.connect(self.updatePrice)
            qProduct.deleted.connect(self.removeProduct)

    def updatePrice(self, product: Product = None):
        if product:
            qProduct = QProduct(product)
        else:
            qProduct = self.sender()
        result = self.searchQAtom(qProduct)
        if result:
            index, item, data = result
            data.setPrice(qProduct.getPrice())
            index0 = self.index(index.row(), 0)
            indexN = self.index(index.row(), self.columnCount())
            self.dataChanged.emit(index0, indexN, [Qt.DisplayRole, Qt.EditRole])
        # self.modelChanged.emit()

    def removeProduct(self, qProduct=None):

        if qProduct:
            pass
        else:
            qProduct = self.sender()
        index, item, data = self.searchQAtom(qProduct)
        self.removeRow(index.row())


class QUserListModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data, parent)
        if data:
            self.setupModelData(data)


class QBuyingHistoryModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data, parent)
        nfcm = QNFCManager()
        nfcm.cardInserted.connect(self.updateHighlight)
        nfcm.cardRemoved.connect(self.updateHighlight)

    def addBuying(self, buying):
        uim = QUIManager()
        qBuying = QBuying(buying)
        # qBuying.getActionDict()["Supprimer"] = {"fct": self.removeBuying, "icon": "delete"}
        qBuying.refounded.connect(self.removeBuying)
        self.insertQAtom(0, qBuying)
        uim.balanceUpdated.emit()

    def removeBuying(self, qBuying=None):
        uim = QUIManager()
        if qBuying:
            pass
        else:
            qBuying = self.sender()
        index, item, data = self.searchQAtom(qBuying)
        self.removeRow(index.row())
        uim.balanceUpdated.emit()

    def data(self, index: QModelIndex, role):

        if role == Qt.ForegroundRole:
            nfcm = QNFCManager()
            # index (QModelIndex), index.internalPointer (TreeItem), --.getData (QAtom)
            qAtom = index.internalPointer().getData()
            if isinstance(qAtom, QBuying):
                qBuying: QBuying = qAtom
                # check if the card on the nfc reader belongs to the transaction
                userList = qBuying.getDistribution().getUserList()
                if nfcm.getCardUID() in userList:
                    # TODO: Do not hardcode themes...
                    return QColor(88, 231, 167)

        return super().data(index, role)

    def updateHighlight(self):
        n_row = self.rowCount()
        n_column = self.columnCount()
        topLeft = self.index(0, 0)
        bottomRight = self.index(n_row, n_column)
        self.dataChanged.emit(topLeft, bottomRight)


class QRefillingHistoryModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data, parent)
        nfcm = QNFCManager()
        nfcm.cardInserted.connect(self.updateHighlight)
        nfcm.cardRemoved.connect(self.updateHighlight)

    def addRefilling(self, refilling):
        qRefilling = QRefilling(refilling)
        qRefilling.cancelled.connect(self.removeRefilling)
        self.insertQAtom(0, qRefilling)

    def removeRefilling(self, qRefilling: QRefilling = None):
        uim = QUIManager()
        if qRefilling:
            pass
        else:
            qRefilling = self.sender()
        index, item, data = self.searchQAtom(qRefilling)
        self.removeRow(index.row())
        uim.balanceUpdated.emit()

    def data(self, index: QModelIndex, role):

        if role == Qt.ForegroundRole:
            nfcm = QNFCManager()
            # index (QModelIndex), index.internalPointer (TreeItem), --.getData (QAtom)
            qRefilling: QRefilling = index.internalPointer().getData()
            # check if the card on the nfc reader belongs to the transaction
            if nfcm.getCardUID() in qRefilling.getCustomerId():
                return QColor(88, 231, 167)

        return super().data(index, role)

    def updateHighlight(self):
        n_row = self.rowCount()
        n_column = self.columnCount()
        topLeft = self.index(0, 0)
        bottomRight = self.index(n_row, n_column)
        self.dataChanged.emit(topLeft, bottomRight)


class QUserHistoryModel(QTreeModel):
    cancelled = pyqtSignal(QRefilling)
    refounded = pyqtSignal(QBuying)
    historyUpdated = pyqtSignal(QOperation)

    def __init__(self, headers, user: QUser, data=None, parent=None):
        super().__init__(headers, data, parent)

        text = [""] * len(headers)
        buyingsRootQAtom = QAtom()
        text[0] = "Achats"
        buyingsRootQAtom.setTexts(text)

        text = copy.deepcopy(text)
        refillingRootQAtom = QAtom()
        text[0] = "Rechargements"
        refillingRootQAtom.setTexts(text)

        self.insertQAtom(0, buyingsRootQAtom)
        self.insertQAtom(1, refillingRootQAtom)
        self.user = user

        client = Client()
        buyings, refillings = client.requestHistory(type=0, customer_id=user.getId())
        for buying in buyings:
            qBuying = QBuying(buying)
            qBuying.refounded.connect(self.refound)
            qBuying.refounded.connect(self.updateHistory)
            qBuying.setTexts(["@label", "@price", str(qBuying.getRefounded())])
            self.addOperation(qBuying)

        # Looks like the server can't handle the case where you want both buyings AND refillings
        # Hence this work around...
        buyings, refillings = client.requestHistory(type=1, customer_id=user.getId())
        for refilling in refillings:
            qRefilling = QRefilling(refilling)
            qRefilling.cancelled.connect(self.cancel)
            qRefilling.cancelled.connect(self.updateHistory)
            qRefilling.setTexts(["", "@amount", "@isRefounded"])
            self.addOperation(qRefilling)

    def addOperation(self, operation: QOperation):
        if isinstance(operation, QBuying):
            subRoot = self.index(0, 0, QModelIndex())
            self.insertQAtom(0, operation, subRoot)

        if isinstance(operation, QRefilling):
            subRoot = self.index(1, 0, QModelIndex())
            self.insertQAtom(0, operation, subRoot)

    def refound(self, buying: QBuying):
        self.refounded.emit(buying)

    def cancel(self, refilling: QRefilling):
        self.cancelled.emit(refilling)

    def updateHistory(self, operation: QOperation):
        if isinstance(operation, QBuying):
            modelIndex = self.index(0, 0)
        else:
            modelIndex = self.index(1, 0)
        index, treeItem, atom = self.searchQAtom(operation, modelIndex)
        operation.setText("@isRefounded", 2)
        self.setData(index, operation)

        self.historyUpdated.emit(operation)


class QMultiUserModel(QTreeModel):
    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data, parent)
