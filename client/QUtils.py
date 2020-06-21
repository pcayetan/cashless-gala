from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

import copy
import json

from Atoms import *
from Euro import Eur




#def euro(price):
#    return format_currency(price, "EUR", locale="fr_FR")


def center(self):
    """Centerize the window"""
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())




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
        except:
            self.row = [[labelRowName, LabelValue]]

        self.layoutRow.addWidget(labelRowName)
        self.layoutRow.addWidget(LabelValue)
        #        self.mainVBoxLayout.addLayout(self.layoutRow)
        self.mainVBoxLayout.insertLayout(
            self.mainVBoxLayout.count() - 1, self.layoutRow
        )

    def setRow(self, i, j, String):
        self.row[i][j].setText(String)


class QErrorDialog(QMessageBox):
    def __init__(
        self,
        title="Erreur",
        message="Erreur",
        info="Une erreur est survenue",
        icon=QMessageBox.Warning,
        parent=None,
    ):
        super().__init__(parent)

        self.setText(message)
        self.setInformativeText(info)
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(icon)

        #        self.setWindowIcon()
        self.setWindowTitle(title)
        self.setBaseSize(QSize(800, 600))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setFixedWidth(600)
        self.setFixedHeight(100)


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
        except:
            self.errorDialog.setWindowIcon(
                self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            )
            self.errorDialog.show()
            center(self.errorDialog)
            self.inputBar.setText("2")


class QIpInputDialog(QAbstractInputDialog):
    valueSelected = pyqtSignal(str)

    def __init__(self, questionText, parent=None):
        super().__init__(parent)
        self.errorDialog = QErrorDialog(
            "Erreur de saisie", "Erreur de saisie", "Veuillez saisir une Ip V4 valide"
        )

    def sendValue(self):
        config = MachineConfig()
        ipParser = self.inputBar.text().replace(" ", "").split(".")
        valid = True
        if len(ipParser) == 4:
            for i in ipParser:
                try:
                    if 0 <= int(i) and int(i) <= 255:
                        pass
                    else:  # invalid ip
                        valid = False
                except:  # Not a number
                    portParser = i.split(":")
                    if len(portParser) == 2:
                        try:
                            if (
                                0 <= int(portParser[0])
                                and int(portParser[0]) <= 255
                                and int(portParser[1]) > 0
                            ):
                                pass
                            else:
                                valid = False
                        except:
                            valid = False
                    else:
                        valid = False
        else:
            valid = False

        if valid is True:
            self.inputBar.setText(self.inputBar.text().replace(" ", ""))
            self.valueSelected.emit(self.inputBar.text())
            config.setHost("http://" + self.inputBar.text())
            api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(config))
            self.close()
        else:
            self.errorDialog.setWindowIcon(
                self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            )
            self.errorDialog.show()
            center(self.errorDialog)


class QNotImplemented(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("NOT IMPLEMENTED")
