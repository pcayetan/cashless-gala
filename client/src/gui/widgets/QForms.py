from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Union, Optional

import logging
import re

# Project specific imports
from src.utils.Euro import Eur
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager

from src.gui.widgets.QDialogs import QErrorDialog
from src.gui.widgets.QInputs import QNumericLineEdit
from src.gui.QUtils import center

log = logging.getLogger()


class QQuantity(QWidget):

    quantityChanged = pyqtSignal()

    def __init__(self, product, parent=None):
        super().__init__(parent)

        # Definition
        self.mainHBoxLayout = QHBoxLayout()
        self.minusButton = QToolButton()
        self.quantityEditLine = QNumericLineEdit()
        self.plusButton = QToolButton()
        self.quantity = 0

        # Settings
        self.minusButton.setText("-")

        self.quantityEditLine.setText(str(self.quantity))
        self.quantityEditLine.setAlignment(Qt.AlignHCenter)
        self.quantityEditLine.setFixedWidth(50)
        self.quantityEditLine.autoSelect = True

        self.plusButton.setText("+")

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # Link

        self.mainHBoxLayout.addWidget(self.minusButton)
        self.mainHBoxLayout.addWidget(self.quantityEditLine)
        self.mainHBoxLayout.addWidget(self.plusButton)
        self.setLayout(self.mainHBoxLayout)

        self.plusButton.clicked.connect(self.incQuantity)
        self.minusButton.clicked.connect(self.decQuantity)
        # self.quantityEditLine.textChanged.connect(self.editingFinished)
        self.quantityEditLine.editingFinished.connect(self.editingFinished)
        self.quantityEditLine.returnPressed.connect(self.editingFinished)

    def incQuantity(self):
        self.quantity = self.quantity + 1
        self.quantityEditLine.setValue(self.quantity)
        self.quantityEditLine.editingFinished.emit()
        self.quantityChanged.emit()

    def decQuantity(self):
        self.quantity = self.quantity - 1
        self.quantityEditLine.setValue(self.quantity)
        self.quantityEditLine.editingFinished.emit()
        self.quantityChanged.emit()

    def editingFinished(self):
        quantity = None
        inputLineText = self.quantityEditLine.text()
        try:
            quantity = int(inputLineText)
        except ValueError:
            quantity = 0
            log.warning("`{}` can't be converted as integer".format(inputLineText))
        self.quantityEditLine.setText(str(quantity))
        self.quantity = quantity
        self.quantityChanged.emit()

    def setQuantity(self, qty: Union[int, str]):
        try:
            self.quantity = int(qty)
            self.quantityEditLine.setText(str(qty))
        except ValueError:
            log.warning("{} can't be converted as a number".format(qty))


class QAbstractInputDialog(QWidget):
    def __init__(self, questionText, parent=None):
        super().__init__(parent)
        # Definitions
        self.mainHBoxLayout = QHBoxLayout()
        self.questionLabel = QLabel()
        self.inputBar = QLineEdit()
        self.okButton = QPushButton()
        self.errorDialog = QErrorDialog(
            "Erreur de saisie", "Erreur de saisie", "Erreur"
        )

        # Settings
        self.questionLabel.setText(questionText)
        self.setWindowTitle(questionText)
        self.okButton.setText("OK")
        self.inputBar.setText("")

        # Links

        self.mainHBoxLayout.addWidget(self.questionLabel)
        self.mainHBoxLayout.addWidget(self.inputBar)
        self.mainHBoxLayout.addWidget(self.okButton)
        self.inputBar.returnPressed.connect(self.sendValue)
        self.okButton.clicked.connect(self.sendValue)

        self.setLayout(self.mainHBoxLayout)


class QSimpleNumberInputDialog(QAbstractInputDialog):
    valueSelected = pyqtSignal(float)

    def __init__(self, questionText, parent=None):
        super().__init__(parent)
        self.errorDialog = QErrorDialog(
            "Erreur de saisie", "Erreur de saisie", "Veuillez saisir un nombre réel."
        )
        self.inputBar.setText("2")

    def sendValue(self):
        try:
            self.valueSelected.emit(float(self.inputBar.text()))
            self.inputBar.setText("2")
            self.close()
        except ValueError:
            self.errorDialog.setWindowIcon(
                self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            )
            self.errorDialog.show()
            center(self.errorDialog)
            self.inputBar.setText("2")


class QIpInputDialog(QInputDialog):
    def __init__(self, defaultAddr="localhost:50051"):
        super().__init__()
        self.setInputMode(QInputDialog.TextInput)
        self.setLabelText("Veuillez entrer l'adresse du serveur")
        self.setTextValue(defaultAddr)

    def textValue(self):
        return super().textValue().replace(" ", "")

    @classmethod
    def isIPValid(cls, ip: str) -> bool:
        if not re.match("[A-z.0-9]+:[0-9]{2,5}", ip):
            return False

        _, port = ip.split(":")
        if int(port) > 65535:  # If superior to the maximum port available
            return False

        return True


class QRowInfo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Definition
        self.mainVBoxLayout = QVBoxLayout()

        # Link
        self.setLayout(self.mainVBoxLayout)

        # Settings
        # self.mainVBoxLayout.addStretch(1)

        #        self.row = np.array([])
        self.row = []

    def addRow(self, RowName, Value):

        self.layoutRow = QHBoxLayout()
        labelRowName = QLabel()
        labelRowName.setText(RowName)
        LabelValue = QLabel()
        LabelValue.setText(str(Value))
        try:
            self.row.append([labelRowName, LabelValue])
        except AttributeError:  # Is that event necessary ?
            self.row = [[labelRowName, LabelValue]]

        self.layoutRow.addWidget(labelRowName)
        self.layoutRow.addWidget(LabelValue)
        #        self.mainVBoxLayout.addLayout(self.layoutRow)
        self.mainVBoxLayout.insertLayout(
            self.mainVBoxLayout.count() - 1, self.layoutRow
        )

    def setRow(self, i, j, String):
        self.row[i][j].setText(str(String))
