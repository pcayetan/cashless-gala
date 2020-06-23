from PyQt5.QtCore import pyqtSignal
from QItemModel import *

from QAtoms import *
from QDataManager import QDataManager
from QUtils import *
import copy #Need to copy Atoms as they are transfered from a tree to another


class QAutoSelectLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)

    def setText(self, string):
        super().setText(str(string))


class QSuperTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAnimated(True) #Because animation looks cool ~

    def focusOutEvent(self, event):
        #This condition was needed because trees loose their selection with right click popup ...
        if event.reason() != Qt.PopupFocusReason:
            self.setCurrentIndex(QModelIndex())


class QItemTree(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        #Definition
        self.mainLayout = QVBoxLayout()
        self.treeView = QTreeView()
        self.treeModel = None

    def contextMenuEvent(self, event):
        uim = QUIManager()
        indexes = self.treeView.selectedIndexes()
        if len(indexes) > 0: #If an index is actually selected
            qProduct = indexes[0].internalPointer().getData()
            if isinstance(qProduct,QProduct):
                contextMenu = QMenu(self)
                qActions = []
                actionDict = qProduct.getActionDict()
                for actionName in actionDict:
                    try:
                        icon = uim.getIcon(actionDict[actionName]['icon'])
                        if icon:
                            action = contextMenu.addAction(icon, actionName)
                        else:
                            action = contextMenu.addAction(actionName)
                    except KeyError:
                        action = contextMenu.addAction(actionName)
                        printW('No icon key for this product')

                    action.triggered.connect(actionDict[actionName]['fct'])
                    
                selectedAction = contextMenu.exec_(self.mapToGlobal(event.pos()))

    def forceRefresh(self):
        model = self.treeModel
        view = self.treeView
        view.setColumnWidth(0, 100)  # Ultimate force resizing.. it seems that whithout this, resizeColumnToContents does not work every time
        for i in reversed(range(model.columnCount(QModelIndex()))):
            view.resizeColumnToContents(i)  # TODO: FIX THIS SHITY HACK ! I use this because without this the button is not correctly placed
            # UPDATE: ACCORDING TO THIS LINK https://stackoverflow.com/questions/8364061/how-do-you-set-the-column-width-on-a-qtreeview
            # THE SIZE OF THE TREEVIEW MAYBE UPDATED WITH setModel FUNCTION, NOT TRIED YET

class QProductSelector(QItemTree):

    itemSelected = pyqtSignal(Product)
    def __init__(self, parent=None):
        super().__init__(parent)

        dm = QDataManager()

        #Definition
        self.mainLayout = QVBoxLayout()
        self.treeView = QSuperTreeView()
        self.treeModel = QProductSelectorModel(["Produits","Prix"], dm.productDict)

        
        #Layout
        self.mainLayout.addWidget(self.treeView)
        self.setLayout(self.mainLayout)

        #Settings
        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()

        self.treeView.doubleClicked[QModelIndex].connect(self.clicked)

    def clicked(self,index):
        qAtom = index.internalPointer().getData()
        if isinstance(qAtom,QProduct):
            atom = qAtom.getAtom()
            self.itemSelected.emit(atom)



class QBasket(QItemTree):
    def __init__(self,parent=None):
        super().__init__(parent)

        #Definition

        self.mainLayout = QVBoxLayout()
        self.treeView = QSuperTreeView()
        self.treeModel = QBasketModel(["Article","Quantité","Prix",""])
        


        #Layout
        self.mainLayout.addWidget(self.treeView)
        self.treeView.setModel(self.treeModel)
        self.setLayout(self.mainLayout)

        self.treeModel.modelChanged.connect(self.forceRefresh)

    def addProduct(self, product:Product):
        newProduct = copy.deepcopy(product)
        #newProduct = copy.deepcopy(product) #Create a deep copy of the atoms, otherwise the initial one is modified
        newProduct.setTexts(['@name','','@quantity * price','']) #The price should be handled inside basket model
        self.treeModel.addProduct(newProduct, self.treeView) #Insert the atom to the top. (No choice but give the treeview to add indexWidget...)
        self.forceRefresh() #Resize column to content for each columns
