from QItemModel import *

from PyQt5.QtCore import pyqtSignal
from QNFC import QCardObserver
from smartcard.util import toHexString

import copy
import json

from Client import *
from QUtils import *


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
            popUp = QErrorDialog(
                "Erreur de saisie",
                "Quantité invalide",
                "Veuillez saisir un nombre entier positif non nul",
            )
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
