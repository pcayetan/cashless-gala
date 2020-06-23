from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from QDataManager import QDataManager
from QUtils import *
from QItemTree import *


from QRefillerTab import *
from QCounterTab import *

# de transaction

#  Shared variables


#  Get item tree
# INITIALISATION



def setFont(Widget, Font):

    for child in Widget.children():
        try:
            child.setFont(Font)
            setFont(child, Font)
        except:
            pass
        # TODO: Find a better way to do this
        if isinstance(child, QTreeView):  # Dirty hack to correct oversizing
            child.resizeColumnToContents(0)


# class QUserHistory(Q)


class QMainTab(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialization
        self.tabCounter = QCounterTab()
        self.tabRefiller= QRefillerTab()
        self.TabStat = QWidget()

        # Add tabs
        self.addTab(self.tabCounter, "Comptoir")
        self.addTab(self.tabRefiller, "Rechargement")
        # self.addTab(self.TabStock, "Rechargements")

        # self.addTab(self.TabStat, "Stats")



class QMainMenu(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gala.Manager.Core")
        self.resize(1600, 1000)
        self.setWindowIcon(QIcon("icon.ico"))

        center(self)
        self.MainTab = QMainTab()
        self.setCentralWidget(self.MainTab)


        font = QFont()  # TODO: Dirty trick to set the whole app font size
        font.setPointSize(16)
        setFont(self, font)

        #  Menu
        mainMenu = self.menuBar()  # Built in function that hold actions

        # Definitions
        configMenu = mainMenu.addMenu("&Config")
        helpMenu = mainMenu.addMenu("&Aide")
        counterMenu = configMenu.addMenu("&Comptoir")
        counterActionList = []
        self.counterActionGroup = QActionGroup(self)

        self.ipDialog = QIpInputDialog("Veuillez saisir l'adresse du serveur")
        self.ipDialog.setWindowTitle("IP Serveur")

        #  Settings
        # Link

        # Toolbar

    def ForceHistoryRefresh(self):
        pass

    def setServerAddress(self):
        pass

    def updateCounter(self):
        pass
