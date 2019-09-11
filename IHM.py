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


def setFont(Widget,Font):
    
    for child in Widget.children():
        try:
            child.setFont(Font)
            setFont(child,Font)
        except:
            pass
        #TODO: Find a better way to do this 
        if (type(child) == type(QTreeView())): #Dirty hack to correct oversizing 
            child.resizeColumnToContents(0)



class QErrorDialog(QMessageBox):
    def __init__(self,Message="Erreur",parent=None):
        super().__init__(parent)

        self.setText(Message)
        self.setInformativeText("Essayez de relancer l'application ou de contacter l'équipe informatique")
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(QMessageBox.Critical)

        
#        self.setWindowIcon()
        self.setWindowTitle("Erreur")

class TreeItem():
    

    def __init__(self,data,parent=None):
        self.parentItem=parent
        if(type(data) == type([])):
            self.dataItem=data
        else:
            self.dataItem=[data]

        self.childItems=[]

        self.uid=None
        self.icon=""

    def appendChild(self,child):
        self.childItems.append(child)


    def child(self,row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.dataItem)

    def getData(self):
        return self.dataItem

    def data(self, column):
        try:
            return self.dataItem[column]
        except IndexError:
            return None

    def row(self): #ChildNumber in the Qt5 exemple
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def parent(self):
        return self.parentItem

    #Usefull method for dynamic Tree

    def insertChildren(self,position,count,columns):
        
        if (position<0 or position > len(self.childItems)):
            return False

        for i in range(0,count):
            data=[QVariant()]*columns
            item=TreeItem(data,self)
            self.childItems.insert(position,item)
        
        return True

    def insertColumns(self,position,columns):
        if (position <0 or position > len(self.dataItem)):
            return False

        for i in range(0,columns): # /!\ check Qt5 exemple
            self.dataItem.insert(position,QVariant())

        for child in self.childItems:
            child.insertColumns(position,columns)

        return True

    def removeChildren(self,position,count):
        if (position < 0  or position > len(self.childItems)):
            return False

        for i in range(0,count): #I think this may create a segfault if count is incorrect
            self.childItems.pop(position) 

        return True


    def removeColumns(self,position,columns):
        pass

    def childNumber(self): #Pointless but use the same name as the Qt5 exemple
        return self.row()


    def setData(self,column,data):
        self.dataItem[column]=data



class QTreeModel(QAbstractItemModel):
    
    def __init__(self,headers,data=None,parent=None):

        super(QTreeModel,self).__init__(parent)

        self.rootItem=TreeItem(headers)
        
        self.__itemList=[]
        if (data!=None):
            self.setupModelData(data,self.rootItem)

    
    def data(self,index,role):
        
        if not index.isValid():
            return None
        
        if (role == Qt.DecorationRole): #Should be moved into the future derivated class
            if (index.column()==0):
                try:
                    return QPixmap("ressources/icones/"+index.internalPointer().data(0)+".png")
                except:
                    pass #No picture found

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

    def index(self,row,column,parent=QModelIndex()):
        
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

    def setupModelData(self,data,parent): #TODO: Pseudo-Generic (Only the final nodes can have data) implementation should be overridden 

        if(type(data) == type({})):
#            print(self.__currentKey,list(data.keys()))
            for i in data:
                self.__currentKey=i
                if(type(data[i]) == type({})):
                    item=len(self.rootItem.getData())*[""]
                    item[0]=i
                    item=TreeItem(item,parent) 
                else:
                    self.__itemList.append(i)
                    item=TreeItem([i]+data[i],parent)
                
                parent.appendChild(item)
                self.setupModelData(data[i],item)

    #Mandatory functions for editable tree

    def insertRows(self,position,rows,parent=QModelIndex()):
        parentItem=self.getItem(parent)
        if (not parentItem):
            return False
        self.beginInsertRows(parent,position,position + rows -1)
        sucess=parentItem.insertChildren(position,rows,self.rootItem.columnCount())
        self.endInsertRows()
        return sucess

    def insertColumns(self,position,columns,parent=QModelIndex()):
        pass

    def removeRows(self,position,rows,parent):
        pass

    def removeColumns(self,position,columns,parent):
        pass

    def setHeaderData(self,section,orientation,value,role):
        if role != QtCore.Qt.EditRole or orientation != QtCore.Qt.Horizontal:
            return False

        result = self.rootItem.setData(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result
    
    def setData(self,index,value,role):
        if (role != Qt.EditRole):
            return False

        item = self.getItem(index)
        result=item.setData(index.column(),value)

        if (result == True):
            self.dataChanged.emit(index,index,[Qt.DisplayRole,Qt.EditRole])

        return result

    #Tool
    
    def getItem(self,index):
        if (index.isValid()):
            item=index.internalPointer()
            if (item):
                return item
                
        return self.rootItem


class QTree(QWidget):
    
    def __init__(self,headers,data=None,parent=None):

        super().__init__(parent)
        #Definitions
        self.mainVBoxLayout=QVBoxLayout()

        self.TreeModel=QTreeModel(headers,data)
        self.TreeView=QTreeView()
        self.TreeView.setModel(self.TreeModel)
        self.TreeView.expandAll()
        self.TreeView.resizeColumnToContents(0)

        #Link
        self.mainVBoxLayout.addWidget(self.TreeView)
        self.setLayout(self.mainVBoxLayout)




class QItemSelector(QTree):

    def __init__(self,headers,data=None,parent=None):
        super().__init__(headers,data,parent)
        self.TreeView.doubleClicked[QModelIndex].connect(self.selectItem)
        self.basketTree=None

    def setBasket(self,basketTree):
        self.basketTree=basketTree

    def selectItem(self,item):
        data=item.internalPointer().getData()
        if len(data)>1:
            if data[1]!="":
              #  errorDialog=QErrorDialog("WTF ?")
              #  center(errorDialog)
              #  errorDialog.exec()
                print("ITEM SELECTED",item.internalPointer().data(0),item)
                #self.basketTree.TreeModel.insertRow(1,item.parent())

                index = self.basketTree.TreeView.selectionModel().currentIndex()
                model = self.basketTree.TreeView.model()

                if not model.insertRow(index.row()+1, index.parent()):
                    return

                #self.updateActions()

                for column in range(model.columnCount(index.parent())):

                    child = model.index(index.row()+1, column, index.parent())
                    model.setData(child, "[NO DATA]", Qt.EditRole)

                btn=QQuantity()
                child=model.index(index.row()+1,1,index.parent())
                model.setData(child,"",Qt.EditRole)
                self.basketTree.TreeView.setIndexWidget(child,btn)
                self.basketTree.TreeView.resizeColumnToContents(1) #TODO: FIX THIS SHITY HACK ! I use this because without this the button is not correctly placed 
                self.basketTree.TreeView.resizeColumnToContents(0)

class QQuantity(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        
        #Definition
        self.mainHBoxLayout=QHBoxLayout()
        self.minusButton=QToolButton()
        self.quantityEditLine=QLineEdit()
        self.plusButton=QToolButton()

        #Settings
        self.minusButton.setText("-")
        #self.minusButton.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

        self.quantityEditLine.setText("1")
        self.quantityEditLine.setAlignment(Qt.AlignHCenter)
        self.quantityEditLine.setFixedWidth(50)
        #self.quantityEditLine.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

        self.plusButton.setText("+")
        #self.plusButton.setSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.Minimum)

        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)        
        #Link

        self.mainHBoxLayout.addWidget(self.minusButton)
        self.mainHBoxLayout.addWidget(self.quantityEditLine)
        self.mainHBoxLayout.addWidget(self.plusButton)
        self.setLayout(self.mainHBoxLayout)



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
        ###TOOLS###
        self.jsonFileName="ItemModel.json"

        ###Definition###

        self.mainGridLayout=QGridLayout()
        #Order definition (left pannel)
        self.orderVBoxLayout=QVBoxLayout()
        self.orderGroupBox=QGroupBox() 
        self.orderRemovePushButton=QPushButton()
        self.orderListWidget= QTree(["Articles","Quantité","Prix total"])

        #ProductSelection definition (middle pannel)
        self.productSelectionVBoxLayout=QVBoxLayout()
        self.productSelectionGroupBox=QGroupBox()
        self.searchBar=QSearchBar()
        self.productTree=QItemSelector(["Articles","Prix"],self.__getItemDictionary(self.jsonFileName))

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
        
        self.productTree.setBasket(self.orderListWidget)

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
        self.searchBar.inputLine.model.setStringList(self.__getItemList())



        #NFC & History space

        self.GroupBoxHistory.setTitle("Historique")

        self.ButtonValidateOrder.setText("Valider et payer")
        self.ButtonValidateOrder.setFixedHeight(50)


    def __getItemDictionary(self,jsonFileName):
        try:
            with open(jsonFileName,'r') as file:
                return json.load(file)
        except:
            #rise some error:
            print("ERREUR: Impossible de lire le fichier",jsonFileName)

    def __getItemList(self):
        itemList=[]
        self.__parseDictionary(self.__getItemDictionary(self.jsonFileName),itemList)
        return itemList

    def __parseDictionary(self,data,itemList):

        if(type(data) == type({})):
            for i in data:
                if(type(data[i]) == type({})):
                    self.__parseDictionary(data[i],itemList)
                else:
                    itemList.append(i)
        

    def OpenNFCDialog(self):
        cardHandler=QCardObserver()
        if (self.NFCDialog.isVisible() == False ):
            if (cardHandler.hasCard() == False):
                center(self.NFCDialog)
                self.NFCDialog.show()
            else:
                print("Carte déjà présente sur le lecteur")
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
        
        cardObserver=QCardObserver()
        cardObserver.cardInserted.connect(self.Payement)




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
        self.resize(1200,800)
        self.setWindowIcon(QIcon(PWD+"ressources/logo.png"))
        center(self)
        self.MainTab=QMainTab()
        self.setCentralWidget(self.MainTab)

        
        #NFC
        #self.NFCReader=getReaders()[0]

        self.CardMonitor=CardMonitor()
        self.CardObserver=QCardObserver()
        self.CardMonitor.addObserver(self.CardObserver)



        font=QFont() #TODO: Dirty trick to set the whole app font size 
        font.setPointSize(12)
        setFont(self,font)

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



