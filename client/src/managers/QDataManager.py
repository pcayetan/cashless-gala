# for Data manager, create random machine uid
import sys
import uuid
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

from pathlib import Path
import pickle
from pickle import PickleError

import logging

# Project specific imports

from src.managers.Client import Client
from src.atoms.Atoms import *


# /!\ Managers must always be called in Qt context, so no global variable for data manager...
#     the reason is simple, DataManager needs QAtoms, that need Widgets. Widgets can't be create
#     if the Qt application did not start yet... It's the best compromise I have found to keep
#     the power of QAtoms.
#     So every time you need a manager in a widget, ensure to call it in the widget e.g
#     class MyCuteWidget(QWidget):
#           def __init__(self):
#               dm = QDataManager()
#               ...
#     otherwise you might get a core dump error from Qt
# /!\

# EDIT: NOW MANAGERS ARE NOT DEPENDENT TO QATOMS ANYMORE SO THE TEXT ABOVE IS IRELEVANT BUT IT MUST BE TESTED

# ________/\\\________/\\\\____________/\\\\____________________________________________________________________________________________________
# _____/\\\\/\\\\____\/\\\\\\________/\\\\\\____________________________________________________________________________________________________
#  ___/\\\//\////\\\__\/\\\//\\\____/\\\//\\\_______________________________________________/\\\\\\\\____________________________________________
#   __/\\\______\//\\\_\/\\\\///\\\/\\\/_\/\\\__/\\\\\\\\\_____/\\/\\\\\\____/\\\\\\\\\_____/\\\////\\\_____/\\\\\\\\___/\\/\\\\\\\___/\\\\\\\\\\_
#    _\//\\\______/\\\__\/\\\__\///\\\/___\/\\\_\////////\\\___\/\\\////\\\__\////////\\\___\//\\\\\\\\\___/\\\/////\\\_\/\\\/////\\\_\/\\\//////__
#     __\///\\\\/\\\\/___\/\\\____\///_____\/\\\___/\\\\\\\\\\__\/\\\__\//\\\___/\\\\\\\\\\___\///////\\\__/\\\\\\\\\\\__\/\\\___\///__\/\\\\\\\\\\_
#      ____\////\\\//_____\/\\\_____________\/\\\__/\\\/////\\\__\/\\\___\/\\\__/\\\/////\\\___/\\_____\\\_\//\\///////___\/\\\_________\////////\\\_
#       _______\///\\\\\\__\/\\\_____________\/\\\_\//\\\\\\\\/\\_\/\\\___\/\\\_\//\\\\\\\\/\\_\//\\\\\\\\___\//\\\\\\\\\\_\/\\\__________/\\\\\\\\\\_
#        _________\//////___\///______________\///___\////////\//__\///____\///___\////////\//___\////////_____\//////////__\///__________\//////////__

log = logging.getLogger()

# Need to be seriously tested !
def parseProductDict(productList: [Product]):

    productDict = {"root": {}, "Product": []}

    def addToDictionnary(productDict, product, relativePath):
        if len(relativePath) == 0:  # End node
            productDict["Product"].append(product)
            return productDict

        else:
            newRelPath = relativePath[1:]
            categoryName = relativePath[0]
            try:
                productDict[categoryName] = addToDictionnary(
                    productDict[categoryName], product, newRelPath
                )
                return productDict
            except KeyError:
                productDict[categoryName] = {"Product": []}
                productDict[categoryName] = addToDictionnary(
                    productDict[categoryName], product, newRelPath
                )
                return productDict

    for product in productList:
        categoryList = product.getCategory().strip().split(".")
        categoryList.insert(0, "root")
        productDict = addToDictionnary(productDict, product, categoryList)

    productDict["root"]["Product"] = productDict["Product"]  # remove useless root key
    productDict = productDict["root"]
    return productDict


# def parseProductDict(productDict):
#    productList = []
#    if isinstance(productDict, Product) is True:
#        return [productDict]
#    elif isinstance(productDict, dict):
#        for key in productDict:
#            productList += parseProductDict(
#                productDict[key]
#            )  # Concatenate product lists
#
#    return productList


class QDataManagerSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QDataManagerSingleton, cls).__call__()
        return cls._instance[cls]


class QDataManager(QObject, metaclass=QDataManagerSingleton):
    priceUpdated = pyqtSignal(Product)

    def __init__(self, parent=None):
        super().__init__(parent)
        client = Client()
        log = logging.getLogger()

        # Definition
        self.productList = []  # list of "Products"
        self.productDict = {}  # With categories
        self.buyingList = []
        self.refillingList = []
        self.counterList = []
        if getattr(sys, "frozen", False):
            # If the program has been frozen by cx_freeze
            self.rootDir = Path(sys.executable).absolute().parents[0]
        else:
            self.rootDir = Path(__file__).absolute().parents[2]

        self.timer = QTimer(self)
        self.counter = None  # Atomic Counter
        self.uid = None  # string uid machine
        self.serverAddress = None  # string format ipv4 e.g 192.168.0.1:50051

        self.timer.timeout.connect(self.update)
        self.timer.start(500)

        # Initialisation
        log.info("Data initialization")

        # Machine uid initialisation

        try:
            with open(self.rootDir / Path("data/uid"), "r") as file:
                self.uid = file.readline()
        except ValueError:
            log.warning("uid file corrupted, a new uid will be generated")
        except FileNotFoundError:
            log.warning("uid file not found in ./data, a new uid will be generated.")

        if not self.uid:
            with open(self.rootDir / Path("data/uid"), "w") as file:
                self.uid = str(uuid.uuid4())
                file.write(self.uid)
                log.info("New machine uid generated")

        # counter initialisation
        log.info("Request counter list")
        self.counterList = client.requestCounterList()
        try:
            with open(Path("data/counter"), "rb") as file:
                try:
                    loadedCounter = pickle.load(file)
                    if loadedCounter in self.counterList:
                        log.info("Loaded counter from memory")
                        self.counter = loadedCounter
                    else:
                        log.warning(
                            "Unable to find the loaded counter in the existing list"
                        )
                        log.info("Setting a new default counter")
                        self.counter = self.counterList[0]
                except PickleError:
                    log.warning("Counter memory corrupted")
                    log.info("Setting a new default counter")
                    self.counter = self.counterList[0]
        except FileNotFoundError:
            log.warning("Counter file not found")
            log.info("Setting a new default counter")
            self.counter = self.counterList[0]

        with open(Path("data/counter"), "wb") as file:
            pickle.dump(self.counter, file)

        log.info("Request products availables for this counter")
        self.productList = client.requestCounterProduct(counter_id=self.counter.getId())
        self.productDict = parseProductDict(self.productList)

    def getPrice(self, product):
        for prod in self.productList:
            if product.getId() == prod.getId():
                return prod.getPrice()

    def getCounter(self):
        return self.counter

    def getUID(self):
        return self.uid

    def update(self):
        client = Client()
        currentTime = client.getTime()
        for product in self.productList:
            for happyHour in product.getHappyHours():
                if (
                    happyHour.getStart() < currentTime
                    and currentTime < happyHour.getEnd()
                ):
                    log.info(
                        "Happy hour sur {0}, {1} au lieu de {2}".format(
                            product, happyHour.getPrice(), product.getDefaultPrice()
                        )
                    )
                    product.setPrice(happyHour.getPrice())
                    self.priceUpdated.emit(product)
                else:
                    if product.getPrice() != product.getDefaultPrice():
                        log.info("Happy hour sur {0} terminée.".format(product))
                        self.priceUpdated.emit(product)
                    product.setPrice(product.getDefaultPrice())
