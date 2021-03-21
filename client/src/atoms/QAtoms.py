from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Project specific imports
from Atoms import *
from QUIManager import QUIManager
from QNFCManager import QNFCManager
from Client import Client
from Euro import Eur
from QUtils import QQuantity, QDelButton

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
    
    def addAction(self, actionName: str, function, icon: str = None):
        if actionName in self.actionDict:
            printW("{} already in action list".format(actionName))
        self.actionDict[actionName] = {'fct': function, 'icon': icon}

    def removeAction(self, actionName: str):
        del self.actionDict[actionName]

    def setActionDict(self, actionDict):
        self.actionDict = actionDict


class QUser(QAtom, User):
    def __init__(self, user):
        super().__init__(user)

    def showInfoPannel(self):
        from QAtomWidgets import QUserInfo
        self.infoPannel = QUserInfo(self)
        self.infoPannel.show()


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
        # To deal with circular import we import the module only when requiered
        from QAtomWidgets import QProductInfo
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
            warningDialog = QWarningDialog("Mauvais utilisateur", "L'utilisateur n'est pas concerné par cette transaction", "Veuillez présenter une carte concernée par la transaction")
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
