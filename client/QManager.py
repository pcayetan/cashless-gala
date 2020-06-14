from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Atoms import *

from Client import *
from QNFC import *
import uuid

from Console import * #For colored printing

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


# Need to be seriously tested !
def parseProductDict(productList: [QProduct]):

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


class QUIManagerSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QUIManagerSingleton, cls).__call__()
        return cls._instance[cls]


class QUIManager(QObject, metaclass=QUIManagerSingleton):
    def __init__(self):
        self.theme = "default"
        self.themeRelPath = "ressources/themes/" + self.theme + "/"


class QNFCManagerSingleton(type(QObject)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QNFCManagerSingleton, cls).__call__()
        return cls._instance[cls]

class QNFCManager(QObject, metaclass=QNFCManagerSingleton):

    cardInserted = pyqtSignal() #It's a copy of the cardObserver signal.. but wrapped in a manager
    cardRemoved  = pyqtSignal()

    readerInserted = pyqtSignal()
    readerRemoved = pyqtSignal()

    def __init__(self):

        self.cardMonitor = CardMonitor()
        self.cardObserver = QCardObserver()
        self.cardMonitor.addObserver(self.cardObserver)
        
        self.readermonitor = ReaderMonitor()
        self.readerUpdater = ReaderUpdater()
        self.readermonitor.addObserver(self.readerUpdater)

        self.cardObserver.cardInserted.connect(self.wrapperCardInserted)
        self.cardObserver.cardRemoved.connect(self.wrapperCardRemoved)

    def getCardUID(self):
        return self.cardObserver.getCardUID()

    def wrapperCardInserted(self): #basicaly, it's just the same that the cardObserver event but wrapped here
        self.cardInserted.emit()

    def wrapperCardRemoved(self):
        self.cardRemoved.emit()



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
        self.counter = None # unsigned int
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
        printI(self.counterList)
        try:
            with open("data/counter", 'r') as file:
                self.counter = int(file.readline())
        except (ValueError):
            printE("Counter file corrupted, trying to set a default counter")
        except (FileNotFoundError):
            printI("Counter file not found, trying to set a default counter")
        finally:
            self.counter = self.counterList[0].id
            with open("data/counter", "w") as file:
                file.write(str(self.counter))
        printI("Request products availables for this counter")
        self.productList = client.requestCounterProduct(counter_id=self.counter)
        print(self.productList)
        self.productDict = parseProductDict(self.productList)
        print(self.productDict) 
        print(type(self.productList[0]))