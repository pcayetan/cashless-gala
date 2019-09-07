import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 

import PyQt5.QtCore
import PyQt5.QtGui

from QNFC import *


import numpy as np
import json

#Pour fixer l'erreur de PyInstaller
import numpy.random.common
import numpy.random.bounded_integers
import numpy.random.entropy

PWD=os.getcwd()+"/"

def center(self):
    """Centerize the window"""
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())



with open("ItemModel.json",'r') as file:
    Dico=json.load(file)

CURRENT_KEY="root"
ITEM_LIST=[]

def parseDict(Dict):
    global CURRENT_KEY
    global ITEM_LIST
    if type(Dict) == type({}):
        """Bla"""
      #  print(CURRENT_KEY, list(Dict.keys()))
        for i in Dict:
            CURRENT_KEY=i
            parseDict(Dict[i])
    else:
        ITEM_LIST.append(CURRENT_KEY)
       # print(CURRENT_KEY,str(Dict)+"€")

parseDict(Dico)


class TreeItem():
    

    def __init__(self,data,parent=None):
        self.parentItem=parent
        if(type(data) == type([])):
            self.dataItem=data
        else:
            self.dataItem=[data]

        self.childItems=[]

    def appendChild(self,child):
        self.childItems.append(child)

    def appendData(self,data):
        self.dataItem.append(data)
    
    def setData(self,column,data):
        self.dataItem[column]=data

    def child(self,row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.dataItem)

    def data(self, column):
        try:
            return self.dataItem[column]
        except IndexError:
            return None

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def parent(self):
        return self.parentItem



class QTreeModel(QAbstractItemModel):
    
    def __init__(self,data,parent=None):

        super(QTreeModel,self).__init__(parent)

        self.rootItem=TreeItem(["Article","Prix"])
        
        self.__itemList=[]
        self.__currentKey="root"
        
        self.setupModelData(data,self.rootItem)

    
    def data(self,index,role):
        
        if not index.isValid():
            return None
        
        if (role != Qt.DisplayRole):
            return None

        item =index.internalPointer()
        return item.data(index.column())

    def rowCount(self,parent):
        
        if(parent.column() > 0):
            return 0
        
        if (not parent.isValid()):
            parentItem= self.rootItem
        else:
            parentItem= parent.internalPointer()
        
        return parentItem.childCount()

    def columnCount(self,parent):

        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()


    def flags(self,index):
        if (not index.isValid()):
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self,section,orientation,role=Qt.DisplayRole):
        
        if(orientation == Qt.Horizontal and role == Qt.DisplayRole):
            return self.rootItem.data(section)

        return None

    def index(self,row,column,parent):
        
        if (not self.hasIndex(row,column,parent)):
            return QModelIndex()

        
        if (not parent.isValid()):
            parentItem=self.rootItem
        else:
            parentItem=parent.internalPointer()
        
        childItem=parentItem.child(row)

        if(childItem != None):
            return self.createIndex(row,column,childItem)
        else:
            return QModelIndex()


    def parent(self,index):
        if (not index.isValid()):
            return QModelIndex()

        childItem=index.internalPointer()
        parentItem=childItem.parent()
        if(parentItem == self.rootItem):
            return QModelIndex()

        return self.createIndex(parentItem.row(),0,parentItem)

   #TODO: FIND THE CORRECT WAY TO DISPLAY THE PRICE 
    def setupModelData(self,data,parent):

        if(type(data) == type({})):
            print(self.__currentKey,list(data.keys()))
            for i in data:
                self.__currentKey=i
                item=TreeItem([i,""],parent) # /!\ THIS HACK SEEMS VERY DIRTY BUT IT WOKS WELL
                parent.appendChild(item)
                self.setupModelData(data[i],item)
        else:
            self.__itemList.append(self.__currentKey)
            #parent.appendData(str(data)+"€")
            parent.setData(1,str(data)+"€") # /!\ THIS HACK SEEMS VERY DIRTY BUT IT WOKS WELL

        


class QTree(QWidget):
    
    def __init__(self,parent=None):

        super().__init__(parent)
        #Definitions
        self.mainVBoxLayout=QVBoxLayout()

        self.TreeModel=QTreeModel(Dico,parent)
        self.TreeView=QTreeView()
        self.TreeView.setModel(self.TreeModel)
        self.TreeView.expandAll()
        self.TreeView.resizeColumnToContents(0)

        #Link
        self.mainVBoxLayout.addWidget(self.TreeView)
        self.setLayout(self.mainVBoxLayout)

class QAutoLineEdit(QLineEdit):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.completer=QCompleter()
        self.setCompleter(self.completer)
        self.model=QStringListModel()
        self.completer.setModel(self.model)
        

class QRowInfo(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        #Definition
        self.mainVBoxLayout=QVBoxLayout()
        
        #Link
        self.setLayout(self.mainVBoxLayout)

        #Settings
        #self.mainVBoxLayout.addStretch(1)

        self.row=np.array([])

    def addRow(self,RowName,Value):
        
        self.layoutRow=QHBoxLayout()
        labelRowName=QLabel()
        labelRowName.setText(RowName)
        LabelValue=QLabel()
        LabelValue.setText(Value)
        try:
            self.row=np.vstack([self.row,[labelRowName,LabelValue]])
        except:
            self.row=np.array([[labelRowName,LabelValue]])


        self.layoutRow.addWidget(labelRowName)
        self.layoutRow.addWidget(LabelValue)
#        self.mainVBoxLayout.addLayout(self.layoutRow)
        self.mainVBoxLayout.insertLayout(self.mainVBoxLayout.count()-1,self.layoutRow)
    
    def setRow(self,i,j,String):
        self.row[i][j].setText(String)



class QInfoNFC(QGroupBox):
    """Display some basics info about the NFC card """
    def __init__(self,parent=None):
        super().__init__(parent)
        #Definitions
        self.mainVBoxLayout = QVBoxLayout()
#        self.frameGroupBox=QGroupBox()
        self.RowInfo = QRowInfo()

        #Link
#        self.frameGroupBox.setLayout(self.mainVBoxLayout)
        self.setLayout(self.mainVBoxLayout) 
        self.mainVBoxLayout.addWidget(self.RowInfo)
        

        #settings

        self.setTitle("Lecteur NFC")
        self.RowInfo.addRow("Solde","0€")
        self.RowInfo.addRow("UID","00 00 00 00 00 00 00")

        nfcObserver=QCardObserver()
        print(nfcObserver)

        nfcObserver.cardInserted.connect(self.addCard)
        nfcObserver.cardRemoved.connect(self.removeCard)
        
    def addCard(self):
        observer=QCardObserver()
        if observer.cardUID[-2:] == [0x63,0x00]:
            print("Erreur de lecture, veuillez réessayer")
        self.RowInfo.setRow(1,1,toHexString(observer.cardUID))
        
    
    def removeCard(self):
        observer=QCardObserver()
        self.RowInfo.setRow(1,1,toHexString(observer.cardUID))

        
class QSearchBar(QWidget):
    """Fast Search Bar"""
    def __init__(self,parent=None):
        super().__init__(parent)

        #Definition
        self.mainHBoxLayout=QHBoxLayout()
        self.inputLine=QAutoLineEdit()
        self.pushButton=QPushButton()

        self.wordList=[]

        #Link
        self.setLayout(self.mainHBoxLayout)
        self.mainHBoxLayout.addWidget(self.inputLine)
        self.mainHBoxLayout.addWidget(self.pushButton)

        #Settings
        #self.inputLine.resize(300,50)
        self.pushButton.setText("OK")
        


class QCounter(QWidget):
    global ITEM_LIST
    def __init__(self,parent=None):
        super().__init__(parent)
        
        ###Definition###

        self.mainGridLayout=QGridLayout()
        #Order definition (left pannel)
        self.orderVBoxLayout=QVBoxLayout()
        self.orderGroupBox=QGroupBox() 
        self.orderRemovePushButton=QPushButton()
        self.orderListWidget= QListWidget()

        #ProductSelection definition (middle pannel)
        self.productSelectionVBoxLayout=QVBoxLayout()
        self.productSelectionGroupBox=QGroupBox()
        self.searchBar=QSearchBar()
        self.productTree=QTree()

        #infoNFC definition (right pannel)
        
        self.paymentVBoxLayout=QVBoxLayout()
        self.infoNFC=QInfoNFC()
        self.GroupBoxHistory=QGroupBox()
        self.NFCDialog=QNFCDialog()
        self.ButtonValidateOrder=QPushButton()

        ###Link###
        self.setLayout(self.mainGridLayout)

        #Order pannel
        
        self.orderVBoxLayout.addWidget(self.orderListWidget)
        self.orderVBoxLayout.addWidget(self.orderRemovePushButton)
        self.orderGroupBox.setLayout(self.orderVBoxLayout)
        self.mainGridLayout.addWidget(self.orderGroupBox,0,0,2,1)

        #Product Selection pannel
        self.productSelectionVBoxLayout.addWidget(self.searchBar)
        self.productSelectionVBoxLayout.addWidget(self.productTree)
        self.productSelectionGroupBox.setLayout(self.productSelectionVBoxLayout)
        self.mainGridLayout.addWidget(self.productSelectionGroupBox,0,1,2,1)

        #Payment pannel
        self.paymentVBoxLayout.addWidget(self.infoNFC)
        self.paymentVBoxLayout.addWidget(self.GroupBoxHistory,2)
        self.mainGridLayout.addLayout(self.paymentVBoxLayout,0,2)
        self.mainGridLayout.addWidget(self.ButtonValidateOrder,1,2)
        self.ButtonValidateOrder.clicked.connect(self.OpenNFCDialog)


        ###Settings###
        #Order pannel
        self.orderGroupBox.setTitle("Panier")
        self.orderRemovePushButton.setText("Supprimer")

        #Product Selection pannel
        self.productSelectionGroupBox.setTitle("Sélection des articles")
        self.searchBar.inputLine.model.setStringList(ITEM_LIST)



        #NFC & History space

        self.GroupBoxHistory.setTitle("Historique")

        self.ButtonValidateOrder.setText("Valider et payer")
        self.ButtonValidateOrder.setFixedHeight(50)
        
        

    def OpenNFCDialog(self):
        if (self.NFCDialog.isVisible() == False):
            #self.NFCDialog=QNFCDialog()
            #self.NFCDialog.initObserver()
            center(self.NFCDialog)
            self.NFCDialog.show()
        else:
            print("Widget déjà ouvert")

class QMainTab(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

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
        
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowIcon(QIcon(PWD+"ressources/logoCarte.png"))
        self.mainVBoxLayout=QVBoxLayout()

        Movie=QMovie(PWD+"ressources/Animation2.gif")

        self.card = QLabel()
        self.card.setMovie(Movie)
        Movie.start()

        self.LabelInstruction=QLabel()
        self.LabelInstruction.setText("Veuillez présenter la carte devant le lecteur")


        self.button= QPushButton()
        self.button.setText("Annuler")

        
        
        self.mainVBoxLayout.addWidget(self.card)
        self.mainVBoxLayout.addWidget(self.LabelInstruction)
        self.mainVBoxLayout.addWidget(self.button)
        self.setLayout(self.mainVBoxLayout)
        self.setWindowTitle("Paiement")

        self.button.clicked.connect(self.Cancel)




    def Cancel(self):
        #Do stuff...
        print("Annuler")
        self.close()

    def Payement(self):
        print("Carte détectée")
        #if(self.CardMonitor.countObservers() > 0):
        #    self.CardMonitor.deleteObserver(self.CardObserver)
        self.close()

        

class QFakeCard(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        cardObserver=QCardObserver()

        self.setWindowIcon(QIcon(PWD+"ressources/logoCarte.png"))
        self.mainVBoxLayout=QVBoxLayout()
        
        self.card = QLabel()
        self.card.setPixmap(QPixmap(PWD+"ressources/logoCarte.png"))

        self.GroupBoxFCEdit=QGroupBox()
        self.GroupBoxFCEdit.setTitle("UID en hexadécimal")
        hbox=QHBoxLayout()
        self.FCEdit=QLineEdit()
        self.FCEdit.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.FCEdit.resize(400,50)
        hbox.addWidget(self.FCEdit)
        self.GroupBoxFCEdit.setLayout(hbox)
        

        self.buttonAddCard= QPushButton()
        self.buttonAddCard.setText("Présenter une carte sur le lecteur")    
        self.buttonAddCard.clicked.connect(cardObserver.virtualCardInsert)

        self.buttonRemoveCard= QPushButton()
        self.buttonRemoveCard.setText("Enlever la carte du lecteur")
        self.buttonRemoveCard.clicked.connect(cardObserver.virtualCardRemove)
        
        self.mainVBoxLayout.addWidget(self.card)
        self.mainVBoxLayout.addWidget(self.GroupBoxFCEdit)
        self.mainVBoxLayout.addWidget(self.buttonAddCard)
        self.mainVBoxLayout.addWidget(self.buttonRemoveCard)
        self.setLayout(self.mainVBoxLayout)
        self.setWindowTitle("Simulation")

        self.NFCDialog=None

    def LinkWidget(self,Widget):
        self.LinkedWidget=Widget

    def CloseNFCDialog(self):
        self.LinkedWidget.Payement()

class QMainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gala.Manager.Core")
        self.resize(800,600)
        self.setWindowIcon(QIcon(PWD+"ressources/logo.png"))
        center(self)
        self.MainTab=QMainTab()
        self.setCentralWidget(self.MainTab)

        
        #NFC
        #self.NFCReader=getReaders()[0]

        self.CardMonitor=CardMonitor()
        self.CardObserver=QCardObserver()
        self.CardMonitor.addObserver(self.CardObserver)

        #self.CardObserver.cardInserted.connect(self.addCard)
        #self.CardObserver.cardRemoved.connect(self.removeCard)

        #self.MainTab.TabCounter.




class QFadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.Timer=QTimer()
        self.Duration=500
        self.Interval=2
        self.Timer.setInterval(self.Interval)
        self.Timer.setTimerType(PyQt5.QtCore.Qt.PreciseTimer)
        self.Timer.timeout.connect(self.Callback)
        self.setWindowOpacity(0) 
        
        self.Timer.start()

        self.Opacity=0
        self.Count=0

    def Callback(self):
        self.Opacity=self.Count*self.Interval/self.Duration
        self.Count+=1
        #print(self.Opacity)
        if(self.Opacity<=1):
            self.setWindowOpacity(self.Opacity)
        else:
            self.setWindowOpacity(1)
            self.Timer.stop()



