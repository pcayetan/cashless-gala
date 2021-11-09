import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging

# Project specific imports
from src.managers.QDataManager import QDataManager
from src.managers.QUIManager import QUIManager
from src.managers.QNFCManager import QNFCManager
from src.managers.Client import Client

from src.gui.QUtils import center
from src.gui.widgets.QInputs import QMoneyInputLine
from src.utils.Euro import Eur

from src.trees.QItemTree import QRefillingHistory
from src.gui.QNFCInfo import QNFCInfo
from src.gui.widgets.QDialogs import QWarningDialog

from src.managers.com.com_pb2 import PaymentMethod

log = logging.getLogger()


class QAbstractPayment(QGroupBox):

    credited = pyqtSignal(Eur)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paiement par carte de crédit")
        self.warningDialog = None
        self.paymentMethod = None
        self.strictPositive = True
        self.inputLine = QMoneyInputLine()
        self.okButton = QPushButton()

        self.inputLine.setMin(0)
        self.inputLine.maxDecimal = 2
        self.inputLine.autoSelect = True

        self.credited.connect(self.clear)

    def getPaymentMethod(self):
        return self.paymentMethod

    def credit(self):
        nfcm = QNFCManager()
        uim = QUIManager()
        if nfcm.hasCard():
            amount = self.inputLine.value
            self.credited.emit(amount)
            uim.balanceUpdated.emit()
        else:
            warningDialog = QWarningDialog(
                "Aucun utilisateur", "Veuillez placer le tag nfc sur le lecteur."
            )
            warningDialog.exec_()

    def clear(self):
        self.inputLine.setText(Eur(0))

    def setFocusOnOk(self):
        self.okButton.setFocus(7)


class QCreditCardPayment(QAbstractPayment):
    enterPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paymentMethod = PaymentMethod.CARD

        # Definitions

        self.setTitle("Paiement par carte de crédit")

        self.mainVBoxLayout = QVBoxLayout()
        self.mainGridLayout = QGridLayout()

        self.label = QLabel()

        # Settings

        self.label.setText("Credit:")
        self.okButton.setText("OK")
        self.inputLine.setMaximumWidth(150)
        self.inputLine.setAlignment(Qt.AlignCenter)
        self.inputLine.setText(Eur(0))

        # Link

        self.mainGridLayout.addWidget(self.label, 0, 0, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.inputLine, 0, 1, Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.okButton, 1, 0, Qt.AlignLeft)

        self.mainVBoxLayout.addLayout(self.mainGridLayout)
        self.mainVBoxLayout.addStretch(1)

        self.setLayout(self.mainVBoxLayout)

        #        self.inputLine.editingFinished.connect(self.formatInput)
        self.okButton.clicked.connect(self.credit)
        self.inputLine.returnPressed.connect(self.handleReturnPressed)

    def handleReturnPressed(self):
        self.setFocusOnOk()


class QCashPayment(QAbstractPayment):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Definition
        self.paymentMethod = PaymentMethod.CASH
        self.mainGridLayout = QGridLayout()
        self.mainVBoxLayout = QVBoxLayout()

        self.moneyInLabel = QLabel()
        self.moneyIn = QMoneyInputLine()
        self.moneyBackLabel = QLabel()
        self.moneyBack = QLabel()

        self.setTitle("Paiement par espèce")

        self.label = QLabel()

        # Settings

        self.label.setText("Credit:")
        self.okButton.setText("OK")
        self.inputLine.setMaximumWidth(150)
        self.inputLine.setAlignment(Qt.AlignCenter)
        self.inputLine.setValue(0)
        self.moneyBack.setText(str(Eur(0)))
        self.moneyBack.setAlignment(Qt.AlignCenter)
        self.moneyBackLabel.setText("Argent à rendre:")
        self.moneyIn.setValue(0)
        self.moneyIn.setAlignment(Qt.AlignCenter)
        self.moneyIn.autoSelect = True
        self.moneyInLabel.setText("Argent reçu:")

        # Layout

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

        #        self.inputLine.editingFinished.connect(self.formatInput)
        #        self.moneyIn.editingFinished.connect(self.formatInput)
        #        self.inputLine.returnPressed.connect(self.formatInput)
        self.okButton.clicked.connect(self.credit)
        self.inputLine.editingFinished.connect(self.updateMoneyBack)
        self.moneyIn.editingFinished.connect(self.updateMoneyBack)

    def updateMoneyBack(self):
        creditText = self.inputLine.text()
        moneyInText = self.moneyIn.text()
        # if self.formatValid(creditText) and self.formatValid(moneyInText):
        credit = self.inputLine.value
        moneyIn = self.moneyIn.value
        self.moneyBack.setText(str(moneyIn - credit))


class QAEPayment(QCreditCardPayment):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.paymentMethod = PaymentMethod.AE
        self.setTitle("Paiement par compte AE")


class QNFCPayment(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.paymentMethod = PaymentMethod.TRANSFER
        self.setTitle("Transfert entre cartes NFC")


class QOtherPayment(QCreditCardPayment):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Singularité")
        self.strictPositive = False
        self.paymentMethod = PaymentMethod.OTHER


class QCheckPayment(QCreditCardPayment):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paiement par chèque")
        self.strictPositive = False
        self.paymentMethod = PaymentMethod.CHECK


class QRefillerTab(QWidget):
    balanceUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uim = QUIManager()

        # Definitions
        self.mainLayout = QHBoxLayout()

        # Left pannel
        self.paymentMethodGroupBox = QGroupBox()
        self.paymentMethodLayout = QVBoxLayout()

        self.cashPaymentRadio = QRadioButton()
        self.cardPaymentRadio = QRadioButton()
        self.checkPaymentRadio = QRadioButton()
        self.aePaymentRadio = QRadioButton()
        self.transfertPayementRadio = QRadioButton()
        self.otherPaymentRadio = QRadioButton()
        # self.spacer = QSpacerItem(int, int)

        # Middle pannel
        self.paymentLayout = QStackedLayout()
        self.cashPayment = QCashPayment()
        self.cardPayment = QCreditCardPayment()
        self.checkPayment = QCheckPayment()
        self.aePayment = QAEPayment()
        self.transfertPayement = QNFCPayment()
        self.otherPayment = QOtherPayment()

        # Right Pannel

        self.rightLayout = QVBoxLayout()

        self.nfcInfo = QNFCInfo()
        self.history = QRefillingHistory()

        # layout
        # Left pannel
        self.paymentMethodGroupBox.setLayout(self.paymentMethodLayout)
        self.paymentMethodLayout.addWidget(self.cashPaymentRadio)
        self.paymentMethodLayout.addWidget(self.cardPaymentRadio)
        self.paymentMethodLayout.addWidget(self.checkPaymentRadio)
        self.paymentMethodLayout.addWidget(self.aePaymentRadio)
        self.paymentMethodLayout.addWidget(self.transfertPayementRadio)
        self.paymentMethodLayout.addWidget(self.otherPaymentRadio)
        self.paymentMethodLayout.addStretch(1)

        # midpannel

        self.paymentLayout.addWidget(self.cashPayment)
        self.paymentLayout.addWidget(self.cardPayment)
        self.paymentLayout.addWidget(self.checkPayment)
        self.paymentLayout.addWidget(self.aePayment)
        self.paymentLayout.addWidget(self.transfertPayement)
        self.paymentLayout.addWidget(self.otherPayment)

        # Right pannel
        self.rightLayout.addWidget(self.nfcInfo)
        self.rightLayout.addWidget(self.history)

        # Settings
        self.paymentMethodGroupBox.setTitle("Moyen de paiement")
        self.cashPaymentRadio.setText("Liquide")
        self.cashPaymentRadio.setIcon(uim.getIcon("cash"))

        self.cardPaymentRadio.setText("Carte")
        self.cardPaymentRadio.setIcon(uim.getIcon("card"))

        self.checkPaymentRadio.setText("Chèque")
        self.checkPaymentRadio.setIcon(uim.getIcon("check"))

        self.aePaymentRadio.setText("Compte AE")
        self.aePaymentRadio.setIcon(uim.getIcon("ae"))

        self.transfertPayementRadio.setText("Transfert")
        self.transfertPayementRadio.setIcon(uim.getIcon("transfert"))

        self.otherPaymentRadio.setText("Autre")
        self.otherPaymentRadio.setIcon(uim.getIcon("other"))

        self.cashPaymentRadio.setChecked(True)

        self.mainLayout.addWidget(self.paymentMethodGroupBox)
        self.mainLayout.addLayout(self.paymentLayout)
        self.mainLayout.addLayout(self.rightLayout)
        self.setLayout(self.mainLayout)

        self.cashPaymentRadio.toggled.connect(self.selectCash)
        self.cardPaymentRadio.toggled.connect(self.selectCreditCard)
        self.aePaymentRadio.toggled.connect(self.selectAE)
        self.checkPaymentRadio.toggled.connect(self.selectCheck)
        self.transfertPayementRadio.toggled.connect(self.selectTransfert)
        self.otherPaymentRadio.toggled.connect(self.selectOther)

        self.cashPayment.credited[Eur].connect(self.credit)
        self.cardPayment.credited[Eur].connect(self.credit)
        self.checkPayment.credited[Eur].connect(self.credit)
        self.otherPayment.credited[Eur].connect(self.credit)
        self.aePayment.credited[Eur].connect(self.credit)

        self.balanceUpdated.connect(self.nfcInfo.update)

    def selectCreditCard(self):
        if self.cardPaymentRadio.isChecked():
            self.paymentLayout.setCurrentWidget(self.cardPayment)

    def selectCash(self):
        if self.cashPaymentRadio.isChecked():
            self.paymentLayout.setCurrentWidget(self.cashPayment)

    def selectAE(self):
        if self.aePaymentRadio.isChecked():
            self.paymentLayout.setCurrentWidget(self.aePayment)

    def selectCheck(self):
        if self.checkPaymentRadio.isChecked():
            self.paymentLayout.setCurrentWidget(self.checkPayment)

    def selectTransfert(self):
        if self.transfertPayementRadio.isChecked():
            self.paymentLayout.setCurrentWidget(self.transfertPayement)

    def selectOther(self):
        if self.otherPaymentRadio.isChecked():
            self.paymentLayout.setCurrentWidget(self.otherPayment)

    def credit(self, amount):
        nfcm = QNFCManager()
        if nfcm.hasCard():
            uid = nfcm.getCardUID()
            dm = QDataManager()

            client = Client()
            counterId = dm.getCounter().getId()
            machineUID = dm.getUID()
            paymentMethod = self.sender().getPaymentMethod()
            refilling = client.requestRefilling(
                customer_id=uid,
                counter_id=counterId,
                device_uuid=machineUID,
                payment_method=paymentMethod,
                amount=amount,
            )
            log.info("User {} credited of {}".format(uid, amount))
            self.balanceUpdated.emit()
            self.history.addRefilling(refilling)
