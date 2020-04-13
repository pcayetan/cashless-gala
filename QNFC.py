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


class NFC_Reader_Error(Exception):
    pass


def getReaders():
    try:
        hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        hresult, readers = SCardListReaders(hcontext, [])
        if len(readers) == 0:
            raise NFC_Reader_Error("Lecteur NFC introuvable, essayez de le rebrancher.")
        return readers
    except NFC_Reader_Error:
        print("Lecteur NFC introuvable, essayez de le rebrancher.")
        # exit()


def getReader():
    try:
        return getReaders()[0]
    except:
        pass


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
    __hasCard = False
    cardUID = []
    errorCode = []
    cardBalance = None

    def __init__(self):
        QObject.__init__(self)
        CardObserver.__init__(self)
        self.cardReader = getReader()

    # print(self.cardReader)

    def hasCard(self):
        return self.__hasCard

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            try:
                hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
                hresult, hcard, dwActiveProtocol = SCardConnect(hcontext, self.cardReader, SCARD_SHARE_SHARED, SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
                hresult, response = SCardTransmit(hcard, dwActiveProtocol, [0xFF, 0xCA, 0x00, 0x00, 0x00])

                self.__hasCard = True
                self.errorCode = response[-2:]

                if self.errorCode != [0x63, 0x00]:
                    self.cardUID = response[:-2]
                else:
                    self.cardUID = [0, 0, 0, 0]
                    print("ERREUR (0x63,0x00): Erreur de lecture de l'UID, veuillez re-essayer")

                #            print("+Inserted: ", toHexString(card.atr))
                self.cardInserted.emit()
                print("+Inserted: ", toHexString(self.cardUID))

            except:
                print("ERREUR: Une erreur inconnue est survenue durrant la lecture, veuillez re-essayer")

        for card in removedcards:

            self.__hasCard = False
            self.cardUID = [0, 0, 0, 0]

            #            print("-Removed: ", toHexString(card.atr))
            self.cardRemoved.emit()
            print("-Removed: ", toHexString(self.cardUID))

    def virtualCardInsert(self):
        self.cardUID = [0x1, 0x2, 0x3, 0x4]
        self.__hasCard = True
        self.cardInserted.emit()

    def virtualCardRemove(self):
        self.cardUID = [0, 0, 0, 0]
        self.__hasCard = False
        self.cardRemoved.emit()


# Allow the user to connect and disconect the reader whenerver he wants
class printobserver(ReaderObserver):
    """A simple reader observer that is notified
    when readers are added/removed from the system and
    prints the list of readers
    """

    def update(self, observable, actions):
        (addedreaders, removedreaders) = actions
        cardObserver = QCardObserver()
        cardObserver.cardReader = getReader()
        print("Added readers", addedreaders)
        print("Removed readers", removedreaders)


# TODO: Make something more "standard" regarding the rest of the code
readermonitor = ReaderMonitor()
readerobserver = printobserver()
readermonitor.addObserver(readerobserver)
