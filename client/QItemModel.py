from QDataManager import QDataManager
from QTree import *

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import *
from Euro import *


class QProductSelectorModel(QTreeModel):

    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data=data, parent=parent)
        dm = QDataManager()
        self.qProductList =  []
        if data is not None:
            self.setupModelData(data)
        dm.priceUpdated[Product].connect(self.updatePrice)

    def setupModelData(self, data):
        dm = QDataManager()
        #print(data)
        # productDict look like this {"root":{"cat1:{"Product":[]}","Product":[]},"Product":[]}
        def exploreDict(productDict, parent:TreeItem):
            # add new categories
            for key in productDict:
                if key != "Product":
                    atom = Atom([key],key)
                    child = TreeItem( QAtom(atom),parent)
                    parent.appendChild(child)
                    exploreDict(productDict[key],child)
            # add products
            for product in productDict["Product"]:
                product.setTexts([product.getName(),product.getPrice()])
                #print(product.getCode())
                qProduct = QProduct(product)
                self.qProductList.append(qProduct)
                child = TreeItem(qProduct,parent)
                parent.appendChild(child)
        
        exploreDict(dm.productDict, self.rootItem)

    def updatePrice(self, product): 
        #We could play with memory tricks so that when it's updated in the manager it's updated here but Master Foo's Zen says:
        # explicit is better that implicit ...
        # So the manager will explicity send update signals to Widgets...
        qProduct = QProduct(product)
        index = self.qProductList.index(qProduct)
        # ???


class QBasketModel(QTreeModel):
    modelChanged = pyqtSignal()
    newProductInserted = pyqtSignal(int,Product) #row product

    def __init__(self, headers, data=None, parent = None):
        super().__init__(headers, data=data, parent=parent)

    def addProduct(self, product:Product,treeView, parent=QModelIndex()):
        
        qProduct = QProduct(product)  #Create qProduct
        childList = self.rootItem.getChild()
        #get the list of all product already included in the basket
        productList = []
        for child in childList:
            productList.append(child.getData())
        #if the product is already in the basket
        if product in productList:
            #I use my own reseach function because the 'match' function from Qt bases it research on the text field
            #by default, I should reimplement 'match', but I prefer use my own search function
            index,item,data = self.searchQAtom(qProduct)
            data.incQuantity()


            #Tell to Qt that the data changed, since Qt think with column, we need to refresh the whole line
            row =index.row()
            n_column = self.columnCount(parent)
            index0 = self.index(row,0,parent) #WITH THIS, THE DISPLAY IS CORRECTLY REFRESH, BUT I DON'T KNOW WHY IT WAS NOT WORKING BEFORE !!!
            indexN = self.index(row,n_column,parent)
            self.dataChanged.emit(index0, indexN, [Qt.DisplayRole, Qt.EditRole])
            
        else:
            #self.productDict[product.getId()] = {'atom':product, 'qAtom':qProduct}
            #Creation of the QAtom
            self.insertRow(0,QModelIndex()) #We insert a row at the top 

            #Configuration of the new row
            quantityPannel = qProduct.getQuantityPannel()
            qProduct.getActionDict()["Supprimer"]={'fct':qProduct.delete,'icon':'delete'}
            treeView.setIndexWidget(self.index(0,1),quantityPannel)
            delButton = qProduct.getDelButton()
            treeView.setIndexWidget(self.index(0,3),delButton)

            newIndex = self.index(0,0)
            self.setData(newIndex,qProduct)

            qProduct.updated.connect(self.update)
            qProduct.deleted.connect(self.removeProduct)

    def update(self):
        self.modelChanged.emit()

    def removeProduct(self, qProduct=None):

        if qProduct:
            pass
        else:
            qProduct = self.sender()
        index,item,data = self.searchQAtom(qProduct)
        self.removeRow(index.row())

class QUserModel(QTreeModel):

    def __init__(self, headers, data =None, parent = None):
        super().__init__(headers, data, parent)
        

class QHistoryModel(QTreeModel):

    def __init__(self, headers, data = None, parent = None):
        super().__init__(headers, data, parent)
    
    def addOperation(self, operation):
        if isinstance(operation, Refilling):
            qRefilling= QRefilling(operation)
            self.insertAtom(0,qRefilling)
        else:
            pass

    def setupModelData(self):
        pass


    
