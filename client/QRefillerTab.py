import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

from QNFC import *
from QUtils import *
from QItemTree import *

from Client import *


class QRefillerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class QAbstractPayement(QGroupBox):

    credited = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paiement par carte de crédit")
        self.warningDialog = None

    def credit(self):

        osbserver = QCardObserver()
        cardUID = osbserver.cardUID

        currentText = self.inputLine.text()
        currentText = (
            currentText.replace("€", "").replace(",", ".").replace(" ", "").strip()
        )

        mantissas = currentText.split(".")
        isFormatValid = True

        if len(mantissas) == 2:
            mantissas = mantissas[1]
            if len(mantissas) <= 2:
                isFormatValid = True  # useless but visual
            else:
                isFormatValid = False

                self.warningDialog = QMessageBox(
                    QMessageBox.Warning,
                    "Format invalide",
                    "Format invalide, veuillez saisir au plus deux chiffres après la virgule",
                    QMessageBox.Ok,
                )
                self.warningDialog.setWindowIcon(
                    self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                )
                self.warningDialog.show()
                center(self.warningDialog)

        if isFormatValid is True:
            try:
                amount = float(currentText)
                self.inputLine.setText(euro(0))
                if amount > 0:
                    self.credited.emit(amount)
                else:
                    self.warningDialog = QMessageBox(
                        QMessageBox.Warning,
                        "Format invalide",
                        "Format invalide, veuillez saisir un nombre strictement positif",
                        QMessageBox.Ok,
                    )
                    self.warningDialog.setWindowIcon(
                        self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                    )
                    self.warningDialog.show()
                    center(self.warningDialog)
            except:
                self.warningDialog = QMessageBox(
                    QMessageBox.Warning,
                    "Format invalide",
                    "Format invalide, veuillez saisir un nombre",
                    QMessageBox.Ok,
                )
                self.warningDialog.setWindowIcon(
                    self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                )
                self.warningDialog.show()
                center(self.warningDialog)


class QCreditCardPayement(QAbstractPayement):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Definitions

        self.setTitle("Paiement par carte de crédit")

        self.mainVBoxLayout = QVBoxLayout()
        self.mainGridLayout = QGridLayout()

        self.label = QLabel()
        self.inputLine = QAutoSelectLineEdit()
        self.okButton = QPushButton()

        # Settings

        self.label.setText("Credit:")
        self.okButton.setText("OK")
        self.inputLine.setMaximumWidth(150)
        self.inputLine.setAlignment(Qt.AlignCenter)
        self.inputLine.setText(euro(0))

        # Link

        self.mainGridLayout.addWidget(self.label, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.inputLine, 0, 1, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.okButton, 1, 0, Qt.AlignLeft)

        self.mainVBoxLayout.addLayout(self.mainGridLayout)
        self.mainVBoxLayout.addStretch(1)

        self.setLayout(self.mainVBoxLayout)

        self.inputLine.editingFinished.connect(self.formatInputLine)
        self.okButton.clicked.connect(self.credit)
        self.inputLine.returnPressed.connect(self.credit)

    def formatInputLine(self):
        currentText = self.inputLine.text()
        currentText = (
            currentText.replace("€", "").replace(",", ".").replace(" ", "").strip()
        )
        self.inputLine.blockSignals(True)
        try:
            self.inputLine.setText(euro(currentText))
        except:
            self.inputLine.setText(euro(0))

        self.inputLine.blockSignals(False)


class QCashPayement(QAbstractPayement):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainGridLayout = QGridLayout()
        self.mainVBoxLayout = QVBoxLayout()

        self.moneyInLabel = QLabel()
        self.moneyIn = QAutoSelectLineEdit()
        self.moneyBackLabel = QLabel()
        self.moneyBack = QLabel()

        self.setTitle("Paiement par espèce")

        self.label = QLabel()
        self.inputLine = QAutoSelectLineEdit()
        self.okButton = QPushButton()

        # Settings

        self.label.setText("Credit:")
        self.okButton.setText("OK")
        self.inputLine.setMaximumWidth(150)
        self.inputLine.setAlignment(Qt.AlignCenter)
        self.inputLine.setText(euro(0))
        self.moneyBack.setText(euro(0))
        self.moneyBack.setAlignment(Qt.AlignCenter)
        self.moneyBackLabel.setText("Argent à rendre:")
        self.moneyIn.setText(euro(0))
        self.moneyIn.setAlignment(Qt.AlignCenter)
        self.moneyInLabel.setText("Argent reçu:")

        # Link

        self.mainGridLayout.addWidget(self.label, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.inputLine, 0, 1, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.moneyInLabel, 1, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.moneyIn, 1, 1, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.moneyBackLabel, 2, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.moneyBack, 2, 1, Qt.AlignLeft)

        self.mainGridLayout.addWidget(self.okButton, 3, 0, Qt.AlignLeft)

        self.mainVBoxLayout.addLayout(self.mainGridLayout)
        self.mainVBoxLayout.addStretch(1)

        self.setLayout(self.mainVBoxLayout)

        self.inputLine.editingFinished.connect(self.formatInputLine)
        self.okButton.clicked.connect(self.credit)
        self.inputLine.returnPressed.connect(self.credit)

    def formatInputLine(self):
        currentText = self.inputLine.text()

        try:
            creditAmount = float(self.inputLine.text())
            currentTextMoneyIn = self.moneyIn.text()
            currentTextMoneyIn = (
                currentTextMoneyIn.replace("€", "")
                .replace(",", ".")
                .replace(" ", "")
                .strip()
            )
            moneyInAmount = float(currentTextMoneyIn)
            self.moneyBack.setText(euro(moneyInAmount - creditAmount))
        except:
            creditAmount = 0
            currentTextMoneyIn = self.moneyIn.text()
            currentTextMoneyIn = (
                currentTextMoneyIn.replace("€", "")
                .replace(",", ".")
                .replace(" ", "")
                .strip()
            )
            moneyInAmount = float(currentTextMoneyIn)
            self.moneyBack.setText(euro(moneyInAmount - creditAmount))

        currentText = (
            currentText.replace("€", "").replace(",", ".").replace(" ", "").strip()
        )
        self.inputLine.blockSignals(True)
        try:
            self.inputLine.setText(euro(currentText))
        except:
            self.inputLine.setText(euro(0))

        self.inputLine.blockSignals(False)

    def formatMoneyIn(self):
        currentText = self.moneyIn.text()
        currentText = (
            currentText.replace("€", "").replace(",", ".").replace(" ", "").strip()
        )
        self.moneyIn.blockSignals(True)
        try:
            self.MoneyIn.setText(euro(currentText))
        except:
            self.moneyIn.setText(euro(0))

        self.moneyIn.blockSignals(False)


class QAEPayement(QCreditCardPayement):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Paiement par compte AE")


class QNFCPayement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Transfert entre cartes NFC")


class QOtherPayement(QCreditCardPayement):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Singularité")

    def credit(self):

        osbserver = QCardObserver()
        cardUID = osbserver.cardUID

        currentText = self.inputLine.text()
        currentText = (
            currentText.replace("€", "").replace(",", ".").replace(" ", "").strip()
        )

        mantissas = currentText.split(".")
        isFormatValid = True

        if len(mantissas) == 2:
            mantissas = mantissas[1]
            if len(mantissas) <= 2:
                isFormatValid = True  # useless but visual
            else:
                isFormatValid = False

                self.warningDialog = QMessageBox(
                    QMessageBox.Warning,
                    "Format invalide",
                    "Format invalide, veuillez saisir au plus deux chiffres après la virgule",
                    QMessageBox.Ok,
                )
                self.warningDialog.setWindowIcon(
                    self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                )
                self.warningDialog.show()
                center(self.warningDialog)

        if isFormatValid is True:
            try:
                amount = float(currentText)
                self.inputLine.setText(euro(0))
                self.credited.emit(amount)
            except:
                self.warningDialog = QMessageBox(
                    QMessageBox.Warning,
                    "Format invalide",
                    "Format invalide, veuillez saisir un nombre",
                    QMessageBox.Ok,
                )
                self.warningDialog.setWindowIcon(
                    self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                )
                self.warningDialog.show()
                center(self.warningDialog)
