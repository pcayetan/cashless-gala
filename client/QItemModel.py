from QManager import *
from QTree import *

from PyQt5.QtCore import pyqtSignal
from QNFC import QCardObserver
from smartcard.util import toHexString
from Euro import *

class Item(TreeItem):
    def __init__(self, data: Atom, parent=None): #data should be an atom
        super().__init__(data, parent)


    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childItems):
            return False

        for i in range(0, count):
            data = [QVariant()] * columns
            item = Item(data, self)
            self.childItems.insert(position, item)

        return True


class QProductSelectorModel(QTreeModel):

    def __init__(self, headers, data=None, parent=None):
        super().__init__(headers, data=data, parent=parent)

    def setupModelData(self, data):
        dm = QDataManager()
        print(data)
        # productDict look like this {"root":{"cat1:{"prod":[]}","prod":[]},"prod":[]}
        def exploreDict(productDict, parent:TreeItem):
            # add new categories
            for key in productDict:
                if key != 'prod':
                    child = TreeItem([key],parent)
                    parent.appendChild(child)
                    exploreDict(productDict[key],child)
            # add products
            for product in productDict['prod']:
                product.setTexts([product.getName(),product.getPrice()])
                print(product.getCode())
                child = TreeItem(product,parent)
                parent.appendChild(child)
        
        exploreDict(dm.productDict,self.rootItem)
        

    
