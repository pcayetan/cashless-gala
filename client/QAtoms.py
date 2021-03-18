from Atoms import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from QUtils import *
from QItemTree import *

from QUIManager import QUIManager

# TODO:SOLVE THIS ARCHITECTURE PROBLEM
# /!\ ARCHITECTURE PROBLEM... MANAGER CAN'T BE CALLED HERE SINCE QATOMS IS IMPORTED IN QMANAGER
#     PROPOSAL: MERGE QATOMS AND QMANAGER
#     PROPOSAL2: DEFINE UIMANAGER IN QATOMS


########################
####### QT WIDGETS#####
######################


class QBuyingInfo(QWidget):
    def __init__(self, qBuying, parent=None):
        super().__init__(parent)
        productList = qBuying.getBasketItems()
        # Définitons
        self.mainLayout = QGridLayout()
        self.productTree = QTree([],)

        self.userInfoGroupBox = QGroupBox()
        self.userInfoLayout = QVBoxLayout()
        self.userInfoTree = QUserList()

        self.buttonLayout = QHBoxLayout()
        self.editButton = QPushButton()
        self.deleteButton = QPushButton()
        self.okButton = QPushButton()

        # Layout
        self.userInfoGroupBox.setLayout(self.userInfoLayout)
        self.userInfoLayout.addWidget(self.userInfoTree)

        self.mainLayout.addWidget(self.productTree, 0, 0)
        self.mainLayout.addWidget(self.userInfoGroupBox, 0, 1)
        self.mainLayout.addLayout(self.buttonLayout, 1, 0, 1, 2)

        # self.userRowInfo.addRow("UID",)

        self.buttonLayout.addWidget(self.editButton)
        self.buttonLayout.addWidget(self.deleteButton)
        self.buttonLayout.addWidget(self.okButton)

        self.setLayout(self.mainLayout)

        # Settings
        self.userInfoGroupBox.setTitle("Clients")
        self.editButton.setText("Éditer")
        self.deleteButton.setText("Rembourser")
        self.okButton.setText("Retour")


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
        except:
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


class QUserInfo(QWidget):
    def __init___(self, parent=None):
        super().__init__(parent)
        uim = QUIManager()

        center(self)
        self.setWindowTitle("Informations utilisateur")
        self.setWindowIcon(uim.getIcon("group"))


class QProductInfo(QWidget):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        uim = QUIManager()

        # Definition
        self.mainLayout = QVBoxLayout()
        self.rowInfo = QRowInfo()
        # Layout
        self.mainLayout.addWidget(self.rowInfo)
        self.setLayout(self.mainLayout)

        # Settings

        self.rowInfo.addRow("Prix", product.getPrice())
        self.rowInfo.addRow("Nom", product.getName())
        self.rowInfo.addRow("Code", product.getCode())
        self.rowInfo.addRow("Id", product.getId())
        self.setFixedSize(300, 100)

        self.setWindowTitle("Informations produit")
        self.setWindowIcon(uim.getWindowIcon("product"))
        center(self)


# ________/\\\___________/\\\\\\\\\_________________________________________________________________
# _____/\\\\/\\\\______/\\\\\\\\\\\\\_______________________________________________________________
#  ___/\\\//\////\\\___/\\\/////////\\\_____/\\\_____________________________________________________
#   __/\\\______\//\\\_\/\\\_______\/\\\__/\\\\\\\\\\\_____/\\\\\_______/\\\\\__/\\\\\____/\\\\\\\\\\_
#    _\//\\\______/\\\__\/\\\\\\\\\\\\\\\_\////\\\////____/\\\///\\\___/\\\///\\\\\///\\\_\/\\\//////__
#     __\///\\\\/\\\\/___\/\\\/////////\\\____\/\\\_______/\\\__\//\\\_\/\\\_\//\\\__\/\\\_\/\\\\\\\\\\_
#      ____\////\\\//_____\/\\\_______\/\\\____\/\\\_/\\__\//\\\__/\\\__\/\\\__\/\\\__\/\\\_\////////\\\_
#       _______\///\\\\\\__\/\\\_______\/\\\____\//\\\\\____\///\\\\\/___\/\\\__\/\\\__\/\\\__/\\\\\\\\\\_
#        _________\//////___\///________\///______\/////_______\/////_____\///___\///___\///__\//////////__
#


class QAtom(QObject, Atom):
    def __init__(self, atom=None):
        super().__init__()
        self.atomKeys = []
        if atom:
            self.setAtom(atom)
        self.actionDict = {}

    def setAtom(self, atom):
        if isinstance(atom, Atom):
            self.atomKeys = list(vars(atom).keys())
        else:
            self.atomKeys = atom.getAtomKeys()

        selfDict = vars(self)  # get the dictionnary representation of the QAtom
        for key in self.atomKeys:  # for each attribute of the incomming atom
            selfDict[key] = vars(atom)[key]  # copy it in the QAtom

    def getAtom(self):
        atom = (type(self).__bases__[1])()  # Create an atom that match the base class
        # note that it involve that the base class must always be the 2nd base
        atomDict = vars(atom)
        selfDict = vars(self)
        # /!\ THIS INVOLVE THAT THIS FUNCTION DOES NOT RETURN A COPY BUT THE ACTUAL ATOM /!\
        #    IT'S COOL BECAUSE IT MEANS THAT WE CAN EITHER WORK WITH A COPY OR A POINTER
        #    BUT WE HAVE TO BE CAREFULL WITH THIS AND USE DEEPCOPY OR NOT...
        for key in self.atomKeys:
            atomDict[key] = selfDict[key]
        # We return actually a copy of the data contained in QAtom
        return atom

    def getAtomKeys(self):
        return self.atomKeys

    def getActionDict(self):
        return self.actionDict

    def setActionDict(self, actionDict):
        self.actionDict = actionDict


class QUser(QAtom, User):
    def __init__(self, user):
        super().__init__(user)
        self.infoPannel = None


class QProduct(QAtom, Product):

    deleted = pyqtSignal()
    updated = pyqtSignal()

    def __init__(self, product):
        super().__init__(product)

        self.infoPannel = None
        self.editPannel = None
        self.quantityPannel = QQuantity(self)
        self.delButton = QDelButton()

        self.quantityPannel.quantityChanged.connect(self.update)
        self.delButton.clicked.connect(self.delete)

        self.actionDict = {"Informations produit": {"fct": self.showInfoPannel, "icon": "product"}}

    def showInfoPannel(self):
        self.infoPannel = QProductInfo(self)
        self.infoPannel.show()

    def getQuantityPannel(self):
        return self.quantityPannel

    def getDelButton(self):
        return self.delButton

    def incQuantity(self):
        self.setQuantity(self.getQuantity() + 1)
        self.update()
        return self.getQuantity()

    def decQuantity(self):
        if self.getQuantity() > 1:
            self.setQuantity(self.getQuantity() - 1)
            self.update()
        return self.getQuantity()

    def update(self):
        self.quantityPannel.update()
        self.updated.emit()

    def delete(self):
        self.deleted.emit()


class QCounter(QAtom, Counter):
    def __init__(self, counter):
        super().__init__(counter)
        self.infoPannel = None


class QOperation(QAtom, Operation):
    def __init__(self, operation):
        super().__init__(operation)


class QBuying(QOperation, Buying):
    sRefounded = pyqtSignal()  # The attribute "refounded" already exists

    def __init__(self, buying):
        super().__init__(buying)
        self.actionDict["Rembourser"] = {"fct": self.refound, "icon": "delete"}

    def refound(self):
        client = Client()
        nfcm = QNFCManager()
        userList = self.getDistribution().getUserList()
        if nfcm.getCardUID() in userList:
            reply = QMessageBox.question(
                None, "Rembourser transaction", "Rembourser cette transaction ?", QMessageBox.Yes, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if client.requestRefund(buying_id=self.getId()) is None:
                    printE("Error during refounding")
                else:
                    self.sRefounded.emit()
        else:
            warningDialog = QWarningDialog("Mauvais utilisateur","L'utilisateur n'est pas concerné par cette transaction","Veuillez présenter une carte concernée par la transaction")
            center(warningDialog)
            warningDialog.exec()


#        self.infoPannel = QBuyingInfo(self)


class QRefilling(QOperation, Refilling):
    def __init__(self, refilling):
        super().__init__(refilling)
        self.infoPannel = None


class QDistribution(QAtom, Distribution):
    def __init__(self, distribution):
        super().__init__(distribution)
        self.infoPannel = None
