from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging
from typing import Union, Any
from decimal import Decimal, InvalidOperation, Context, ROUND_DOWN

# Project specific imports
from src.utils.Euro import Eur
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager

log = logging.getLogger()
# Collection of widget based on input widgets


class QAbstractLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.returnPressed.connect(self.handleReturnPressed)
        self.autoSelect = False

    def handleReturnPressed(self):
        self.clearFocus()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.autoSelect:
            QTimer.singleShot(0, self.selectAll)

    def setText(self, string):
        super().setText(str(string))


class QTextLineEdit(QAbstractLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.previousText = ""


class QNumericLineEdit(QTextLineEdit):
    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.baseType = Decimal
        self.range = [self.baseType("-inf"), self.baseType("inf")]
        self.editingFinished.connect(self.handleEditingFinished)
        self.previousOnError = True
        self.maxDecimal = None

    def setValue(self, value: Any):
        if not isinstance(value, self.baseType):
            value = self.baseType(value)
        min, max = self.range
        if min <= value and value <= max:
            self.value = value
            self.previousText = str(value)
            # Makes sense only if the base type has its own __str__ like Eur
            self.setText(str(value))
            self.valueChanged.emit()
        else:
            if self.previousOnError is True:
                self.setText(self.previousText)
            log.warning(
                "Input value `{}` must be in range `[{},{}]`".format(value, min, max)
            )

    def setMin(self, min: Any):
        min = self.baseType(min)
        if min >= self.range[1]:
            log.warning("Minimum must be lower than maximum. Ingored")
        else:
            self.range[0] = min

    def setMax(self, max: Any):
        max = self.baseType(max)
        if max <= self.range[0]:
            log.warning("Maximum must be greater than minimum. Ingored")
        else:
            self.range[1] = max

    def setRange(self, range: list):
        if len(range) != 2:
            log.warning("Range must be a list of two numbers [a,b] such that a < b")
        else:
            self.setMin(range[0])
            self.setMax(range[1])

    def handleReturnPressed(self):
        super().handleReturnPressed()
        self.valueChanged.emit()

    def handleEditingFinished(self):
        text = self.text()
        baseType = self.baseType
        try:
            value = baseType(text)
        except (ValueError, InvalidOperation) as err:
            log.warning(err)
            if self.previousOnError is True:
                # setText triggers textChanged only
                self.setText(self.previousText)
            return
        if self.maxDecimal:
            # context = Context(prec=2, rounding=ROUND_DOWN)
            if self.value.as_tuple().exponent < -2:
                log.warning("Too many digits")
                if self.previousOnError is True:
                    self.setText(self.previousText)
                return

        self.setValue(value)


class QMoneyInputLine(QNumericLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = Eur(0)
        self.range = [Eur("-inf"), Eur("inf")]
        self.baseType = Eur
        # self.editingFinished.connect(self.handleEditingFinished)

    def setAmount(self, amount: Eur):
        super().setValue(amount)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        text = self.text()
        text = str(self.value.amount)
        self.setText(text)
