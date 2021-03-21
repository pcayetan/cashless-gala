from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Project specific imports
from Euro import Eur
from QNFCManager import QNFCManager
from QUIManager import QUIManager
from Client import Client

# def euro(price):
#    return format_currency(price, "EUR", locale="fr_FR")


def center(self):
    """Centerize the window"""
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


class QNFCDialog(QDialog):
    cardInserted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uim = QUIManager()
        nfcm = QNFCManager()
        # Definition
        self.mainLayout = QVBoxLayout()
        self.label = QLabel()
        self.setFixedSize(450, 400)

        # Layout
        self.mainLayout.addWidget(self.label)
        self.setLayout(self.mainLayout)

        nfcm.cardInserted.connect(self.proceed)

        # Setup
        movie = uim.getAnimation("show-card-animation")
        self.label.setMovie(movie)
        movie.start()

        self.setWindowTitle("Veuillez présenter une carte devant le lecteur")
        self.setWindowIcon(uim.getIcon("nfc-icon"))

        center(self)

    def proceed(self):
        self.cardInserted.emit()
        self.done(0)


class QDelButton(QToolButton):

    deleted = pyqtSignal(QToolButton)

    def __init__(self, parent=None):
        super().__init__(parent)

        uim = QUIManager()
        self.row = -1
        self.clicked.connect(self.delete)

        # So normally ui manager should be used here
        # but because of the cycle import problem I can't import the ui manager here unless
        # I merge QAtoms with QManager...
        #        self.setIcon(QIcon("ressources/themes/default/ui-icons/delete.png"))
        self.setIcon(uim.getIcon("delete"))
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

    def __init__(self, product, parent=None):
        super().__init__(parent)

        # Definition
        self.mainHBoxLayout = QHBoxLayout()
        self.minusButton = QToolButton()
        self.quantityEditLine = QLineEdit()
        self.plusButton = QToolButton()
        self.quantity = product.getQuantity()
        self.product = product

        # Settings
        self.minusButton.setText("-")

        self.quantityEditLine.setText(str(self.quantity))
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
        self.product.incQuantity()
        self.quantity = self.product.getQuantity()
        self.quantityEditLine.setText(str(self.quantity))
        self.quantityEditLine.editingFinished.emit()
        self.quantityChanged.emit()

    def decQuantity(self):
        self.product.decQuantity()
        self.quantity = self.product.getQuantity()
        if self.quantity > 0:
            self.quantityEditLine.setText(str(self.quantity))
            self.quantityEditLine.editingFinished.emit()
        else:
            self.product.setQuantity(1)

    def editingFinished(self):
        try:
            self.product.setQuantity(int(self.quantityEditLine.text()))
        except ValueError:
            self.product.setQuantity(1)
            self.quantity = self.product.getQuantity()
            if self.quantityEditLine.text() != "":
                self.quantityEditLine.setText("1")

        if self.quantity >= 1:
            self.quantityChanged.emit()
        else:
            self.quantityEditLine.setText("1")
            self.product.setQuantity(1)
            popUp = QErrorDialog(
                "Erreur de saisie", "Quantité invalide", "Veuillez saisir un nombre entier positif non nul",
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
            self.product.setQuantity(int(qty))
            self.quantityEditLine.setText(str(qty))
            self.quantityChanged.emit()
        except ValueError:
            print("ERROR: ", qty, " is not a number")

    def update(self):
        self.quantityEditLine.setText(str(self.product.getQuantity()))



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
        self.mainVBoxLayout.insertLayout(self.mainVBoxLayout.count() - 1, self.layoutRow)

    def setRow(self, i, j, String):
        self.row[i][j].setText(str(String))


class QErrorDialog(QMessageBox):
    def __init__(
        self, title="Erreur", message="Erreur", info="Une erreur est survenue", icon=QMessageBox.Warning, parent=None,
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


class QWarningDialog(QMessageBox):
    def __init__(
        self, title="Erreur", message="Erreur", info="Une erreur est survenue", icon=QMessageBox.Warning, parent=None,
    ):
        super().__init__(parent)

        self.setText(message)
        self.setInformativeText(info)
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(icon)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))

        #        self.setWindowIcon()
        self.setWindowTitle(title)
        self.setBaseSize(QSize(800, 600))
        center(self)

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
        self.errorDialog = QErrorDialog("Erreur de saisie", "Erreur de saisie", "Erreur")

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
        self.errorDialog = QErrorDialog("Erreur de saisie", "Erreur de saisie", "Veuillez saisir un nombre réel.")
        self.inputBar.setText("2")

    def sendValue(self):
        try:
            self.valueSelected.emit(float(self.inputBar.text()))
            self.inputBar.setText("2")
            self.close()
        except ValueError:
            self.errorDialog.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            self.errorDialog.show()
            center(self.errorDialog)
            self.inputBar.setText("2")


class QIpInputDialog(QAbstractInputDialog):
    valueSelected = pyqtSignal(str)

    def __init__(self, questionText, parent=None):
        super().__init__(parent)
        self.errorDialog = QErrorDialog("Erreur de saisie", "Erreur de saisie", "Veuillez saisir une Ip V4 valide")

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
                except ValueError:  # Not a number
                    portParser = i.split(":")
                    if len(portParser) == 2:
                        try:
                            if 0 <= int(portParser[0]) and int(portParser[0]) <= 255 and int(portParser[1]) > 0:
                                pass
                            else:
                                valid = False
                        except ValueError:
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
            self.errorDialog.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
            self.errorDialog.show()
            center(self.errorDialog)


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
