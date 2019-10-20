from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import PyQt5.QtCore
import PyQt5.QtGui

import copy
import json


from babel.numbers import format_currency

# Server response emulation
import uuid


MAC = hex(uuid.getnode())


def euro(price):
    return format_currency(price, "EUR", locale="fr_FR")


def center(self):
    """Centerize the window"""
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


def isFinalNode(dictionary):
    try:
        for key in dictionary:
            if isinstance(dictionary[key], dict) is False:
                return True

        return False
    except:
        print(dictionary, "is not a dictionary")
        return True


class QItemRegisterSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QItemRegisterSingleton, cls).__call__()
        return cls._instance[cls]


class QItemRegister(QObject, metaclass=QItemRegisterSingleton):

    priceUpdated = pyqtSignal(QVariant)

    def __init__(self, parent=None):
        QObject.__init__(self)

        self.itemDict = {}  # BASE OF ITEMS, WITHOUT TREE LOGIC

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        #     self.timer.start()
        self.happyHour = {}
        self.__latchHappyHour = {}
        self.timer.timeout.connect(self.updatePrice)

    def start(self):
        self.timer.start()

    def loadItemFile(self, itemModelFile):
        with open(itemModelFile, "r") as file:
            data = json.load(file)
            self.__parseDictionary(data)
        self.happyHour = self.parseHappyHour()

    def loadDict(self, itemDict):
        if isinstance(itemDict, dict) is False:
            raise TypeError("not a dictionary")
        self.__parseDictionary(itemDict)
        self.happyHour = self.parseHappyHour()

    def __parseDictionary(self, data):

        if isFinalNode(data) is False:
            for i in data:
                if isFinalNode(data[i]) is True:
                    data[i]["name"] = i
                self.__parseDictionary(data[i])
        else:
            uid = data["uid"]
            self.itemDict[uid] = data
            # del self.itemDict[uid]["uid"]  # I don't know if i should remove uid from this since it could be as usefull as redondant
            self.itemDict[uid]["currentPrice"] = data["defaultPrice"]

    def getItems(self, key=None):
        try:
            return copy.deepcopy(self.itemDict[key])
        except:
            return copy.deepcopy(self.itemDict)

    def getPrice(self, itemID):
        pass

    def parseHappyHour(self):
        # Happy hour format:
        # xxhxx-xxhxx=price;...;xxhxx-xxhxx=price
        try:
            happyHourDict = {}
            for uid in self.itemDict:
                self.__latchHappyHour[uid] = {}
                try:
                    happyHour = self.itemDict[uid]["happyHour"]
                    happyHour = happyHour.replace(" ", "")  # Remove every spaces
                    happyHour = happyHour.split(";")  # Break into many time intervals

                    parsedHappyHour = []
                    for i in happyHour:
                        happyPrice = float(i.split("=")[1])
                        interval = i.split("=")[0]
                        interval = interval.split("-")
                        h_start = float(interval[0].split("h")[0])
                        m_start = float(interval[0].split("h")[1])
                        h_end = float(interval[1].split("h")[0])
                        m_end = float(interval[1].split("h")[1])

                        m_start /= 60
                        m_end /= 60

                        parsedHappyHour.append([h_start + m_start, h_end + m_end, happyPrice])
                    happyHourDict[uid] = parsedHappyHour
                except:
                    pass
            return happyHourDict

        except:
            return {}

    def __isValid(self, subHappyHourDict):

        t_max = 0
        for i in subHappyHourDict:
            if i[0] > i[1] or i[0] < t_max:
                return False
            else:
                t_max = i[1]
        return True

    def updateItemList(self):
        pass

    def forceUpdateItemList(self):
        raise NotImplemented

    def updatePrice(self):
        """Check for each timeout if the price have to be updated"""
        h, m, s = QTime.currentTime().hour(), QTime.currentTime().minute(), QTime.currentTime().second()
        time = h + m / 60
        for uid in self.happyHour:
            if self.__isValid(self.happyHour[uid]):
                for interval in self.happyHour[uid]:

                    try:
                        self.__latchHappyHour[uid][interval[0]]  # If it does not exist yet
                    except:
                        self.__latchHappyHour[uid][interval[0]] = 0  # Initialize it

                    if interval[0] <= time and time <= interval[1]:
                        if self.__latchHappyHour[uid][interval[0]] == 1:
                            pass
                        else:
                            self.__latchHappyHour[uid][interval[0]] = 1
                            self.itemDict[uid]["currentPrice"] = interval[2]
                            print("Happy hour pour ", uid, " nouveau prix: ", interval[2])
                            self.priceUpdated.emit(uid)
                    else:
                        if self.__latchHappyHour[uid][interval[0]] == 1:
                            self.__latchHappyHour[uid][interval[0]] = 0
                            self.itemDict[uid]["currentPrice"] = self.itemDict[uid]["defaultPrice"]
                            print("Fin happy hour pour", uid, "nouveau prix", self.itemDict[uid]["currentPrice"])
                            self.priceUpdated.emit(uid)
                        else:
                            pass
        # print(h, m, s)


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
        self.mainVBoxLayout.insertLayout(self.mainVBoxLayout.count() - 1, self.layoutRow)

    def setRow(self, i, j, String):
        self.row[i][j].setText(String)


class QErrorDialog(QMessageBox):
    def __init__(self, title="Erreur", message="Erreur", info="Une erreur est survenue", icon=QMessageBox.Warning, parent=None):
        super().__init__(parent)

        self.setText(message)
        self.setInformativeText(info)
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(icon)

        #        self.setWindowIcon()
        self.setWindowTitle(title)
        self.setBaseSize(QSize(800, 600))


class QConnectorSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QConnectorSingleton, cls).__call__()
        return cls._instance[cls]


class QConnector(QObject, metaclass=QConnectorSingleton):

    balanceInfoUpdated = pyqtSignal(float)  # amount

    def __init__(self):
        QObject.__init__(self)

    def updateBalanceInfo(self, newBalance):
        self.balanceInfoUpdated.emit(newBalance)
