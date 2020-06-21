from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Client import *
#for Data manager, create random machine uid
import uuid

# for QUIManager, find file in ressources
import os 

from Console import * #For colored printing

#TEST
import pickle
from pickle import PickleError
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

#EDIT: NOW MANAGERS ARE NOT DEPENDENT TO QATOMS ANYMORE SO THE TEXT ABOVE IS IRELEVANT BUT IT MUST BE TESTED

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# ________  _____ ______   ________  ________   ________  ________  _______   ________     
#|\   __  \|\   _ \  _   \|\   __  \|\   ___  \|\   __  \|\   ____\|\  ___ \ |\   __  \    
#\ \  \|\  \ \  \\\__\ \  \ \  \|\  \ \  \\ \  \ \  \|\  \ \  \___|\ \   __/|\ \  \|\  \   
# \ \  \\\  \ \  \\|__| \  \ \   __  \ \  \\ \  \ \   __  \ \  \  __\ \  \_|/_\ \   _  _\  
#  \ \  \\\  \ \  \    \ \  \ \  \ \  \ \  \\ \  \ \  \ \  \ \  \|\  \ \  \_|\ \ \  \\  \| 
#   \ \_____  \ \__\    \ \__\ \__\ \__\ \__\\ \__\ \__\ \__\ \_______\ \_______\ \__\\ _\ 
#    \|___| \__\|__|     \|__|\|__|\|__|\|__| \|__|\|__|\|__|\|_______|\|_______|\|__|\|__|
#          \|__|                                                                            
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# Need to be seriously tested !
def parseProductDict(productList: [Product]):

    productDict={"root":{},"prod":[]}
    def addToDictionnary(productDict, product, relativePath):
        if(len(relativePath) == 0): # End node
            productDict["prod"].append(product)
            return productDict

        else:
            newRelPath = relativePath[1:]
            categoryName = relativePath[0] 
            try:
                productDict[categoryName] = addToDictionnary(productDict[categoryName],product,newRelPath)
                return productDict
            except KeyError:
                productDict[categoryName]={"prod":[]}
                productDict[categoryName] = addToDictionnary(productDict[categoryName],product,newRelPath)
                return productDict

    for product in productList:
        categoryList = product.getCategory().strip().split('.')
        categoryList.insert(0,"root")
        productDict = addToDictionnary(productDict,product, categoryList)

    productDict["root"]["prod"] = productDict["prod"] #remove useless root key
    productDict = productDict["root"]
    return productDict



#def parseProductDict(productDict):
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
    def __init__(self,parent=None):
        client = Client()
        # Definition
        self.productList = []  # list of "Products"
        self.productDict = {}  # With categories
        self.buyingList = []
        self.refillingList = []
        self.counterList = []

        self.clock = QTime()
        self.counter = None # Atomic Counter
        self.uid = None #string uid machine
        self.serverAddress = None #string format ipv4 e.g 192.168.0.1:50051

        # Initialisation
        printI("Data initialization")

        #Machine uid initialisation

        try:
            with open("data/uid",'r') as file:
                self.uid = file.readline()
        except ValueError:
            printW("uid file corrupted, a new uid will be generated")
        except FileNotFoundError:
            printW("uid file not found in ./data, a new uid will be generated")
        finally:
            with open("data/uid",'w') as file:
                self.uid = str(uuid.uuid4())
                file.write(self.uid)

        #counter initialisation
        printI("Request counter list")
        self.counterList = client.requestCounterList()
        try:
            with open('data/counter','rb') as file: #open read/write/binary file
                try:
                    loadedCounter = pickle.load(file)
                    if loadedCounter in self.counterList:
                        printI('Loaded counter from memory')
                        self.counter = loadedCounter
                    else:
                        printW('Unable to find the loaded counter in the existing list')
                        printN('Setting a new default counter')
                        self.counter = self.counterList[0]
                except:
                    printW('Unable to read a counter in memory')
                    printN('Setting a new default counter')
                    self.counter = self.counterList[0]
        except FileNotFoundError:
            printW('Counter file not found')
            printN('Setting a new default counter')
            self.counter = self.counterList[0]

        with open('data/counter','wb') as file:
            pickle.dump(self.counter,file)

        printI("Request products availables for this counter")
        self.productList = client.requestCounterProduct(counter_id=self.counter.getId())
        self.productDict = parseProductDict(self.productList)
        

    def getPrice(self, product):
        pass

