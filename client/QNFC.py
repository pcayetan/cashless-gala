# Modules NFC

from smartcard.scard import SCardConnect
from smartcard.scard import SCardTransmit
from smartcard.scard import SCardListReaders
from smartcard.scard import SCardEstablishContext
from smartcard.scard import SCARD_SHARE_SHARED
from smartcard.scard import SCARD_PROTOCOL_T0
from smartcard.scard import SCARD_PROTOCOL_T1
from smartcard.scard import SCARD_SCOPE_USER

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject

# DEBUG

from smartcard.scard import SCardGetErrorMessage
from smartcard.System import readers as rd
from smartcard.scard import SCardReleaseContext


# ReaderObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver

from Console import *

class NFC_Reader_Error(Exception):
    pass


def getReaders():
    try:
        hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        hresult, readers = SCardListReaders(hcontext, [])
        if len(readers) == 0:
            raise NFC_Reader_Error("Can't find the NFC reader, try to unplug and plugin again")
        return readers
    except NFC_Reader_Error:
        printE("Can't find the NFC reader, try to unplug and plugin again")


def getReader(index=0):
    try:
        return getReaders()[index]
    except:
        return None


class QCardObserverSingleton(type(QObject), type(CardObserver)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(QCardObserverSingleton, cls).__call__()
        return cls._instance[cls]


# a simple card observer that prints inserted/removed cards
class QCardObserver(QObject, CardObserver, metaclass=QCardObserverSingleton):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    cardInserted = pyqtSignal()
    cardRemoved = pyqtSignal()
    errorCode = []

    def __init__(self):
        # should it be super(QObject), super(CardObserver) ?
        QObject.__init__(self)
        CardObserver.__init__(self)        
        self.cardReader = getReader()
        self.cardUID = toHexString([0,0,0,0]) # now it's always a string
        self.__hasCard = False


    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            try:
                hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
                hresult, hcard, dwActiveProtocol = SCardConnect(
                    hcontext,
                    self.cardReader,
                    SCARD_SHARE_SHARED,
                    SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1,
                )
                hresult, response = SCardTransmit(
                    hcard, dwActiveProtocol, [0xFF, 0xCA, 0x00, 0x00, 0x00]
                )

                self.__hasCard = True
                self.errorCode = response[-2:]

                if self.errorCode != [0x63, 0x00]:
                    self.cardUID = toHexString(response[:-2]) # string are more handy serverwise
                else:
                    self.cardUID = toHexString([0, 0, 0, 0])
                    printE("Failed to read card UID, please try again")

                #            print("+Inserted: ", toHexString(card.atr))
                self.cardInserted.emit()
                printNFC("+INSERTED {0}".format(self.cardUID))

            except:
                printE("unkown error occured, please try again")

        for card in removedcards:

            self.__hasCard = False
            self.cardUID = toHexString([0, 0, 0, 0])

            #            print("-Removed: ", toHexString(card.atr))
            self.cardRemoved.emit()
            printNFC("-Removed: {0}".format(self.cardUID))

    def getCardUID(self):
        return self.cardUID

    def hasCard(self):
        return self.__hasCard

    #DEBUG
    #For virtual card...
    def setCardState(self,state):
        self.__hasCard = state



# Allow the user to connect and disconect the reader whenerver he wants
class ReaderUpdater(QObject, ReaderObserver):
    """A simple reader observer that is notified
    when readers are added/removed from the system and
    prints the list of readers
    """

    readerInserted = pyqtSignal()
    readerRemoved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._hasReader= False

    def update(self, observable, actions):
        (addedreaders, removedreaders) = actions
        cardObserver = QCardObserver()
        cardObserver.cardReader = getReader()
        if len(addedreaders) != 0:
            printNFC("Added readers {0}".format(addedreaders))
            self.readerInserted.emit()
        if len(removedreaders) != 0:
            printNFC("Removed readers {0}".format(removedreaders))
            self.readerRemoved.emit()

        if cardObserver.cardReader:
            self._hasReader=True
        else:
            self._hasReader=False


