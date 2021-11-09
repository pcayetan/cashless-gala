from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
from src.utils.Euro import Eur
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager
from src.managers.Client import Client


# def euro(price):
#    return format_currency(price, "EUR", locale="fr_FR")


def center(self):
    """Centerize the window"""
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


class QNotImplemented(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("NOT IMPLEMENTED")


class QVirtualCard(QWidget):
    virtualCardInserted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        uim = QUIManager()
        nfcm = QNFCManager()

        # Definition
        self.mainLayout = QGridLayout()
        self.inputLine = QLineEdit()
        self.showCardButton = QPushButton()
        self.removeCardButton = QPushButton()

        # Layout
        self.mainLayout.addWidget(self.inputLine, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.showCardButton, 1, 0, 1, 1)
        self.mainLayout.addWidget(self.removeCardButton, 1, 1, 1, 1)
        self.setLayout(self.mainLayout)
        center(self)

        self.showCardButton.clicked.connect(self.virtualCardInsert)
        self.virtualCardInserted[str].connect(nfcm.virtualCardInsert)
        self.removeCardButton.clicked.connect(nfcm.virtualCardRemove)

        # Setup
        self.inputLine.setText("00 01 02 03")
        self.showCardButton.setText("Lire carte")
        self.removeCardButton.setText("Retirer carte")
        self.setWindowIcon(uim.getWindowIcon("nfc-card"))
        self.setWindowTitle("Carte NFC Virtuelle")
        self.setFixedSize(300, 100)

    def virtualCardInsert(self):
        self.virtualCardInserted.emit(self.inputLine.text())
