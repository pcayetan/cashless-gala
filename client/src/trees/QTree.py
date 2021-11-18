import copy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
import logging
from src.atoms.QAtoms import *
from src.managers.QDataManager import QDataManager
from src.managers.QUIManager import QUIManager


# Basicaly, this file is the heart of the GUI since there are trees everywhere
# The tree model/view paradigm is NOT easy to handle at first, but the most difficult
# functions are already implemented...

# The key to understand what's going here is to check the Qt's Model/View paradigm
# https://doc.qt.io/qt-5/model-view-programming.html
# It's a really powerfull way to handle trees in UIs

# IN A FEW WORDS
# The main idea behind model/view paradigm, is break the tree into two main parts:
# The model (What's inside my tree ?) and View (How does it look ?)
# Both are completly INDEPENDENTS and exchange information through some standards functions
# It's a client/server relationship, the tree ask elements to the model and the model respond
# Because both are independants, you can use the same model for different treeView or the other way

# Pay attention to the object you're handling, basicaly there are three layers from the UI to the data:
# QModelIndex index  -> What the view (and the model) handle
# ItemTree    item   -> What the model (and only the model) handle internally
# QAtom      qAtom   -> What the user handle (and the dev)


class TreeItem:
    """This class is is in charge to store the architecture/data inside the QT Tree Model.
    It behave like a basic chained list where each node is a QAtom"""

    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.childItems = []

        if isinstance(data, QAtom) is True:
            self.data = data
        else:
            self.data = QAtom()
            if isinstance(data, list) is True:
                # /!\ We don't check if data can be interpreted as string
                self.data.setTexts(data)

        self.__formatText()
        # self.__parseMagicString()

    def appendChild(self, child):
        self.childItems.append(child)

    def child(self, row):
        return self.childItems[row]

    def getChild(self):  # TODO: remplace it by getChildren ...
        return self.childItems

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.data.getTexts())

    def getText(self, column=None):
        parsedTextList = self.__parseMagicString()
        try:
            if column is None:
                return None
            else:
                return parsedTextList[column]
        except IndexError:
            return None

    def getData(self):
        return self.data

    def setData(self, data: QAtom):
        if isinstance(data, QAtom):
            self.data = data
            self.__formatText()
            return True
        else:
            return False

    def row(self):  # ChildNumber in the Qt5 exemple
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def parent(self):  # TODO: Standartize this into getParent()
        return self.parentItem

    # Usefull method for dynamic Tree
    def insertChildren(self, position, count, columns):

        if position < 0 or position > len(self.childItems):
            return False

        for i in range(0, count):
            # note: According the Qt Doc, in TreeModel, items must have the same amount of columns.
            # data = [QVariant()] * columns
            data = QAtom()
            data.setTexts([""] * columns)
            item = TreeItem(data, self)
            self.childItems.insert(position, item)

        return True

    def insertColumns(self, position, columns):
        if position < 0 or position > len(self.data.getTexts()):
            return False

        for i in range(0, columns):  # /!\ check Qt5 exemple
            texts = self.data.getTexts()
            texts.insert(position, "")
            self.data.setTexts(texts)

        for child in self.childItems:
            child.insertColumns(position, columns)

        return True

    def removeChildren(self, position, count):
        if position < 0 or position > len(self.childItems):
            return False

        for i in range(
            0, count
        ):  # I think this may create a segfault if count is incorrect
            self.childItems.pop(position)

        return True

    # remove n_columns from position
    def removeColumns(self, position, n_columns):
        if position < 0 or position + n_columns > len(self.data.getTexts()):
            return False
        for i in range(n_columns):
            texts = self.data.getTexts()
            del texts[position]
            self.data.setTexts(texts)

        for child in self.childItems:
            child.removeColumns(position, n_columns)
        return True

    def childNumber(self):  # Pointless but use the same name as the Qt5 exemple
        return self.row()

    def setText(self, column, data):
        if column < 0 or column >= len(self.data.getTexts()):
            return False

        self.data.setText(str(data), column)
        return True

    def __formatText(self):
        # EXPERIMENTAL: AUTO ADJUST COLUMN (SO TEXT) LENGTH
        # Seems to work ...
        # Format text format according to the parent
        if self.parentItem:
            currentText = self.data.getTexts()
            while len(currentText) < self.parentItem.columnCount():
                currentText.append("")
            while len(currentText) > self.parentItem.columnCount():
                del currentText[-1]
            self.data.setTexts(
                currentText
            )  # Not necessary because of python shity behavior but clearer this way
        # ensure data can be printed
        texts = self.data.getTexts()
        for index, text in enumerate(texts):
            texts[index] = str(text)

    def __parseMagicString(self):
        """Magic strings are strings that must be evaluated as a mathematical expressions
        All magic strings start with either '=' or '@'
        The variable used in the expression must be part of the QAtoms's attributes
        for instance with a product '@ (2*price)**2' return (2 x price)² where price is
        an a property existing in the product."""

        atomDict = vars(
            self.data
        )  # python built-in function to turn an object into dictionary
        texts = self.data.getTexts()
        parsedTextList = copy.deepcopy(texts)
        for index, text in enumerate(texts):
            if len(text) > 0:
                if (
                    "=" == text[0] or "@" == text[0]
                ):  # I can't decide I like both ... T_T
                    expression = text.replace("=", "").replace("@", "")
                    try:
                        parsedTextList[index] = str(
                            eval(expression, atomDict)
                        )  # no rage still pythoninc <3
                        # eval(expr,dict), basically it searchs variable defined in 'dict' and replace them in expr.
                    except ValueError:
                        log.warning(
                            "Failed to parse the expression {}".format(expression)
                        )
        return parsedTextList


class QTreeModel(QAbstractItemModel):
    """Base class for all tree models
    QTreeModel inherit from QAbstractItemModel which is a pure Qt class.
    Abstract means that we need to overload some standard function in order to make
    it works correctly.
    Most of the method implemented below are standard methods the TreeView need to work"""

    def __init__(self, headers, data=None, parent=None):
        super().__init__(parent)
        self.rootItem = TreeItem(headers)
        self._qAtomList = []

    def data(self, index, role):
        """A model don't store only the text to display, it can also store the colors,
        Icons etc...
        Depending on what the View want to know, the model must provide the correct information,
        hence the 'role'...
        """
        uim = QUIManager()
        if not index.isValid():
            return None
        item = index.internalPointer()
        data = item.getData()
        if role == Qt.DecorationRole:
            # only show icons in first column
            if index.column() == 0:
                return uim.getIcon(data.getIcon())
            else:
                return None

        if role == Qt.ToolTipRole:
            return data.getToolTip()

        if role != Qt.DisplayRole:
            return None

        return item.getText(index.column())

    def rowCount(self, parent=QModelIndex()):

        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):

        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.getText(section)

        return None

    def index(self, row, column, parent=QModelIndex()):
        """index is a Qt object that represent a particular node in the model.
        Despite a tree is technically a 2D object (row/column) an index has actually
        3 coordinates. The 3rd one is the parent of the node."""

        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)

        if childItem is not None:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def setupModelData(self, qAtomList):
        for qAtom in qAtomList:
            self.insertQAtom(0, atom)

    # Mandatory functions for editable tree

    def insertRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        if not parentItem:
            return False
        self.beginInsertRows(parent, position, position + rows - 1)
        sucess = parentItem.insertChildren(position, rows, self.rootItem.columnCount())
        self.endInsertRows()
        return sucess

    def insertColumns(self, position, columns, parent=QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self.rootItem.insertColumns(position, columns)
        self.endInsertColumns()

        return success

    def removeRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def removeColumns(self, position, columns, parent=QModelIndex()):
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success = self.rootItem.removeColumns(position, columns)
        self.endRemoveColumns()

        if self.rootItem.columnCount() == 0:
            self.removeRows(0, rowCount())

        return success

    def setHeaderData(self, section, orientation, value, role):
        if role != QtCore.Qt.EditRole or orientation != QtCore.Qt.Horizontal:
            return False

        result = self.rootItem.setText(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def setData(self, index: QModelIndex, value: QAtom, role=Qt.EditRole):
        """You should use this method as much as possible to modify your tree's contend.
        Notice the use of 'dataChanged.emit' this notify the 'view' that it should be updated.
        If you don't use this method, ensure that dataChanged is correctly emited, otherwise you'll never
        see anything"""

        if role != Qt.EditRole:
            return False

        item = self.getItem(index)

        if isinstance(value, str):
            result = item.setText(index.column(), value)
        else:
            result = item.setData(value)  # Value should be QAtomic

        if result:
            parent = index.parent()
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return result

    # Tool
    # Basicaly, all these functions are not required by Qt, but are requiered by our own needs..

    def getItem(self, index) -> TreeItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def insertQAtom(self, position, qAtom, parent=QModelIndex()):
        self.insertRow(position, parent)
        newIndex = self.index(position, 0, parent)
        self.setData(newIndex, qAtom)

    def searchQAtom(
        self, qAtom: QAtom, parent=QModelIndex()
    ) -> (QModelIndex, TreeItem, QAtom):

        n_row = self.rowCount(parent)
        n_col = self.columnCount(parent)
        for i in range(n_row):
            for j in range(n_col):
                index = self.index(i, j, parent)
                item = self.getItem(index)
                data = item.getData()
                if data == qAtom:  # == means same id
                    return index, item, data
                elif self.hasChildren(index):
                    result = self.searchQAtom(qAtom, index)
                    if result:
                        return result

    def getQAtomList(self, parent=QModelIndex()):
        self._qAtomList = []
        self._walk(parent)
        return self._qAtomList

        # qAtomList = []
        # n_row = self.rowCount(parent)
        # for i in range(n_row):
        #    item = self.getItem(self.index(i, 0, parent))
        #    data = item.getData()
        #    qAtomList.append(data)
        # return qAtomList

    def _walk(self, index=QModelIndex()):

        if index.isValid():
            item: TreeItem = index.internalPointer()
            qAtom = item.getData()
            if qAtom not in self._qAtomList:
                self._qAtomList.append(qAtom)

        if self.hasChildren(index):
            n_row = self.rowCount(index)
            n_col = self.columnCount(index)
            for i in range(n_row):
                for j in range(n_col):
                    self._walk(self.index(i, j, index))


class QTree(QWidget):
    def __init__(self, headers, data=None, parent=None):

        super().__init__(parent)
        # Definitions
        self.mainVBoxLayout = QVBoxLayout()

        self.treeModel = QTreeModel(headers, data)
        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

        # Link
        self.mainVBoxLayout.addWidget(self.treeView)
        self.setLayout(self.mainVBoxLayout)


class QSuperTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAnimated(True)  # Because animation looks cool ~

    def focusOutEvent(self, event):
        # This condition was needed because trees loose their selection with right click popup ...
        if event.reason() != Qt.PopupFocusReason:
            self.setCurrentIndex(QModelIndex())
