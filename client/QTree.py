from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

from QUtils import *
from QAtoms import *
from Console import *
from QDataManager import QDataManager
from QUIManager import QUIManager

import copy

class TreeItem:
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.childItems = []

        if isinstance(data, QAtom) is True:
            self.data = data
        else:
            self.data = QAtom()
            if isinstance(data,list) is True:
                # /!\ We don't check if data can be interpreted as string
                self.data.setTexts(data)


        self.__formatText()
        #self.__parseMagicString()


    def appendChild(self, child):
        self.childItems.append(child)

    def child(self, row):
        return self.childItems[row]

    def getChild(self): #TODO: remplace it by getChildren ...
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

    def setData(self, data):
        if isinstance(data,Atom):
            self.data = data
            self.__formatText()
            return True
        else:
            return False

    def row(self):  # ChildNumber in the Qt5 exemple
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def parent(self): #TODO: Standartize this into getParent()
        return self.parentItem

    # Usefull method for dynamic Tree
    def insertChildren(self, position, count, columns):

        if position < 0 or position > len(self.childItems):
            return False

        for i in range(0, count):
            # note: According the Qt Doc, in TreeModel, items must have the same amount of columns.
            #data = [QVariant()] * columns
            data = QAtom()
            data.setTexts([""]*columns)
            item = type(self)(data, self) # the type(self) is usefull to get dynamically the type of class
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

    # never tested, should works ....
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
       #EXPERIMENTAL: AUTO ADJUST COLUMN (SO TEXT) LENGTH 
       #Seems to work ...
       #Format text format according to the parent
        if self.parentItem:
            currentText = self.data.getTexts()
            while len(currentText) < self.parentItem.columnCount():
                currentText.append("")
            while len(currentText) > self.parentItem.columnCount():
                del(currentText[-1])
            self.data.setTexts(currentText) #Not necessary because of python shity behavior but clearer this way
        #ensure data can be printed
        texts = self.data.getTexts()
        for index,text in enumerate(texts):
            texts[index] = str(text)

    def __parseMagicString(self):

        atomDict = vars(self.data)  #python built-in function to turn an object into dictionary
        texts = self.data.getTexts()
        parsedTextList = copy.deepcopy(texts)
        for index,text in enumerate(texts):
            if len(text)>0:
                if '=' == text[0] or '@' == text[0]: # I can't decide I like both ... T_T
                    expression = text.replace('=','').replace('@','')
                    try:
                        parsedTextList[index] = str(eval(expression,atomDict)) #no rage still pythoninc <3
                    except:
                        printW("Failed to parse the expression {}".format(expression))
        return parsedTextList


class QTreeModel(QAbstractItemModel):
    def __init__(self, headers, data=None, parent=None):

        super().__init__(parent)
        self.rootItem = TreeItem(headers)

    def data(self, index, role):

        uim = QUIManager()
        if not index.isValid():
            return None
        item = index.internalPointer()
        data = item.getData()
        if role == Qt.DecorationRole:
            #only show icons in first column
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

    def setupModelData(self, atomList):
        for atom in atomList:
            self.insertAtom(0,atom)

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

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        item = self.getItem(index)

        if isinstance(value, str):
            result = item.setText(index.column(), value)
        else:
            result = item.setData(value) #Value should be QAtomic

        if result:
            parent = index.parent()
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return result

    # Tool

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def insertAtom(self, position, Atom, parent=QModelIndex()):
        self.insertRow(position,QModelIndex())
        newIndex = self.index(position,0)
        self.setData(newIndex,Atom)

    def searchQAtom(self, qAtom:QAtom, parent = QModelIndex()):
        n_row = self.rowCount()
        for i in range(n_row):
            item = self.getItem(self.index(i,0,parent))
            data = item.getData()
            if data == qAtom: # == means same id
                return self.index(i,0),item,data

    def getQAtomList(self,parent=QModelIndex()):
        qAtomList = []
        n_row = self.rowCount()
        for i in range(n_row):
            item = self.getItem(self.index(i,0,parent))
            data = item.getData()
            qAtomList.append(data)
        return qAtomList



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
