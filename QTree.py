import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

from QUtils import *


class TreeItem:
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.data = {}

        self.data["text"] = []

        if isinstance(data, list):
            self.data["text"] = data
        else:
            self.data["text"] = [data]

        self.childItems = []

    def appendChild(self, child):
        self.childItems.append(child)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.data["text"])

    def getText(self, column=None):
        try:
            if column is None:
                return self.data["text"]
            else:
                return self.data["text"][column]
        except IndexError:
            return None

    def getData(self, key=None):
        try:
            return self.data[key]
        except:
            return self.data

    def row(self):  # ChildNumber in the Qt5 exemple
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def parent(self):
        return self.parentItem

    # Usefull method for dynamic Tree

    def insertChildren(self, position, count, columns):

        if position < 0 or position > len(self.childItems):
            return False

        for i in range(0, count):
            data = [QVariant()] * columns
            item = TreeItem(data, self)
            self.childItems.insert(position, item)

        return True

    def insertColumns(self, position, columns):
        if position < 0 or position > len(self.data["text"]):
            return False

        for i in range(0, columns):  # /!\ check Qt5 exemple
            self.data["text"].insert(position, QVariant())

        for child in self.childItems:
            child.insertColumns(position, columns)

        return True

    def removeChildren(self, position, count):
        if position < 0 or position > len(self.childItems):
            return False

        for i in range(0, count):  # I think this may create a segfault if count is incorrect
            self.childItems.pop(position)

        return True

    def removeColumns(self, position, columns):
        pass

    def childNumber(self):  # Pointless but use the same name as the Qt5 exemple
        return self.row()

    def setText(self, column, data):
        if column < 0 or column >= len(self.data["text"]):
            return False

        self.data["text"][column] = str(data)

        return True


class QTreeModel(QAbstractItemModel):
    def __init__(self, headers, data=None, parent=None):

        super(QTreeModel, self).__init__(parent)
        self.rootItem = TreeItem(headers)
        self.itemList = []
        if data is not None:
            self.setupModelData(data, self.rootItem)

    def data(self, index, role):

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.getText(index.column())

    def rowCount(self, parent):

        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent):

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

    def setupModelData(self, data, parent):
        raise NotImplementedError()

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
        result = item.setText(index.column(), value)

        if result:
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

        return result

    # Tool

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem


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
