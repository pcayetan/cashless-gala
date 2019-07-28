# importations à faire pour la réalisation d'une interface graphique
#Application simple
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow
from PyQt5.QtGui import QIcon

import numpy as np

#Pour les auto-complete
from PyQt5.QtWidgets import QLineEdit, QCompleter
from PyQt5.QtCore import QStringListModel


#Widgets usuel

from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QTabWidget, QPushButton, QListWidget, QGroupBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
#from PyQt5.QtNfc import QNearFieldManager #NFC wtf ?

#Widget exotiques

from PyQt5.QtGui import QMovie


#Modules NFC

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


# a simple card observer that prints inserted/removed cards
class QCardObserver(CardObserver, QObject):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    CardInserted=pyqtSignal()
    CardRemoved= pyqtSignal()   

    def __init__(self,CardReader):
        print("Surcharge constructeur")
        QObject.__init__(self)
        self.CardReader=CardReader
    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            hresult,hcontext=SCardEstablishContext(SCARD_SCOPE_USER)
            hresult, hcard, dwActiveProtocol = SCardConnect(hcontext,self.CardReader, SCARD_SHARE_SHARED,SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
            hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0xCA,0x00,0x00,0x00])
            self.CardInserted.emit()
            print("+Inserted: ", toHexString(card.atr))
            print(toHexString(response))
        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
            self.CardRemoved.emit()

class NFC_Reader_Error(Exception):
    pass

def GetReaders():
    try:
        hresult,hcontext=SCardEstablishContext(SCARD_SCOPE_USER)
        hresult, readers= SCardListReaders(hcontext,[])
        if(len(readers)==0):
            raise NFC_Reader_Error("Lecteur NFC introuvable, essayez de le rebrancher.")
        return readers
    except NFC_Reader_Error:
        exit()




PWD=os.getcwd()+"/"

print(PWD)




def ParseFile(File,separator=";", Header=True, Headers=[]):
    """Parse a file"""

def center(self):
    """Centerize the window"""
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


class QAutoLineEdit(QLineEdit):
    def __init__(self,Parent=None):
        super().__init__(Parent)
        self.Completer=QCompleter()
        self.setCompleter(self.Completer)
        self.Model=QStringListModel()
        self.Completer.setModel(self.Model)
        


class QCounter(QWidget):
    def __init__(self,Parent=None):
        super().__init__(Parent)
        
        self.Layout=QGridLayout()

        #Panier
        #Layout principal
        self.LayoutOrder=QVBoxLayout()
        #Widget frame permettant d'encadrer un ensemble
        self.GroupBoxOrder=QGroupBox() 
        self.GroupBoxOrder.setTitle("Panier")
        self.ListOrder= QListWidget()
        self.LayoutOrder.addWidget(self.ListOrder)
        self.ButtonDelOrder=QPushButton()
        self.ButtonDelOrder.setText("Supprimer")
        self.LayoutOrder.addWidget(self.ButtonDelOrder)
        self.GroupBoxOrder.setLayout(self.LayoutOrder)
        self.Layout.addWidget(self.GroupBoxOrder,0,0)

        #Interface création de commande
        self.LayoutUser=QVBoxLayout()
        self.GroupBoxUser=QGroupBox()
        self.GroupBoxUser.setTitle("Sélection des articles")

        #Recherche rapide
        self.LayoutFastSearch=QHBoxLayout()
        self.InputLine=QAutoLineEdit()
        self.InputLine.resize(400,50)
        self.InputLine.Model.setStringList(["Coca", "Chocolat", "Ice Tea", "Café", "Thé"])
        self.ButtonValidateItem=QPushButton()
        self.ButtonValidateItem.setText("OK")
        self.LayoutFastSearch.addWidget(self.InputLine)
        self.LayoutFastSearch.addWidget(self.ButtonValidateItem)

        self.LayoutUser.addLayout(self.LayoutFastSearch)
        self.GroupBoxUser.setLayout(self.LayoutUser)

        self.Layout.addWidget(self.GroupBoxUser,0,1)


        self.setLayout(self.Layout)
        

        #Pa
        


class QMainTab(QTabWidget):
    def __init__(self,Parent=None):
        super().__init__(Parent)

        #Initialization
        self.TabCounter=QCounter()
        self.TabStock=QWidget()
        self.TabStat=QWidget()

        #Add tabs
        self.addTab(self.TabCounter,"Comptoir")
        self.addTab(self.TabStock,"Stocks")
        self.addTab(self.TabStat,"Stats")

        self.resize(600,400)



class QNFCDialog(QWidget):
        
    def __init__(self,Parent=None):
        super().__init__(Parent)

        self.setWindowIcon(QIcon(PWD+"ressources/logoCarte.png"))
        self.Layout=QVBoxLayout()

        Movie=QMovie(PWD+"ressources/Animation2.gif")

        self.Card = QLabel()
        self.Card.setMovie(Movie)
        Movie.start()

        self.LabelInstruction=QLabel()
        self.LabelInstruction.setText("Veuillez présenter la carte devant le lecteur")


        self.Button= QPushButton()
        self.Button.setText("Annuler")

        
        
        self.Layout.addWidget(self.Card)
        self.Layout.addWidget(self.LabelInstruction)
        self.Layout.addWidget(self.Button)
        self.setLayout(self.Layout)
        self.setWindowTitle("Paiement")

        self.Button.clicked.connect(self.Cancel)

        #NFC
        self.NFCReader=GetReaders()[0]

        self.CardMonitor=CardMonitor()
        self.CardObserver=QCardObserver(self.NFCReader)
        self.CardMonitor.addObserver(self.CardObserver)

        self.CardObserver.CardInserted.connect(self.Payement)        

        self.show()

    def Cancel(self):
        #Do stuff...
        print("Annuler")
        self.close()

    def Payement(self):
        print("Carte détectée, paiement effectué")
        self.close()

    def Detect():
        print("Card detected")
        

class QFakeCard(QWidget):
    def __init__(self,Parent=None):
        super().__init__(Parent)

        self.setWindowIcon(QIcon(PWD+"ressources/logoCarte.png"))
        self.Layout=QVBoxLayout()
        
        self.Card = QLabel()
        self.Card.setPixmap(QPixmap(PWD+"ressources/logoCarte.png"))
        self.Button= QPushButton()
        self.Button.setText("Présenter une carte sur le lecteur")    
        self.Button.clicked.connect(self.OpenNFCDialog)
        
        self.Layout.addWidget(self.Card)
        self.Layout.addWidget(self.Button)
        self.setLayout(self.Layout)
        self.setWindowTitle("Simulation")
        self.show()

        self.NFCDialog=None

    def OpenNFCDialog(self):
        self.NFCDialog=QNFCDialog()
        self.NFCDialog.show()
        center(self.NFCDialog)


if (__name__ == '__main__'):
    # Première étape : création d'une application Qt avec QApplication
    #    afin d'avoir un fonctionnement correct avec IDLE ou Spyder
    #    on vérifie s'il existe déjà une instance de QApplication
    app = QApplication.instance() 
    if not app: # sinon on crée une instance de QApplication
        app = QApplication(sys.argv)


    MainWindow=QMainWindow()
    MainWindow.setWindowTitle("Gala.Manager.Core")
    MainWindow.resize(800,600)
    MainWindow.setWindowIcon(QIcon(PWD+"ressources/logo.png"))
    center(MainWindow)

    MainTab= QMainTab()

    MainWindow.setCentralWidget(MainTab)

    
    # création d'une fenêtre avec QWidget dont on place la référence dans fen


    #edit = QLineEdit()
    #Completer=QCompleter()
    #edit.setCompleter(Completer)
    #model=QStringListModel()
    #Completer.setModel(model)
    #get_data(model)

    edit2=QAutoLineEdit()
    edit2.Model.setStringList(["Coca", "Chocolat", "Ice Tea", "Café", "Thé"])


    FakeCard= QFakeCard()



    # la fenêtre est rendue visible
    #edit.show()
    edit2.show()
    MainWindow.show()






    # exécution de l'application, l'exécution permet de gérer les événements
    app.exec_()
