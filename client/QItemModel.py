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
