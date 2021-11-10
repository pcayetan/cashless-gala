from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import logging

# Project specific imports
from src.managers.QDataManager import QDataManager
from src.managers.QUIManager import QUIManager
from src.trees.QItemTree import *
from src.gui.QRefillerTab import *
from src.gui.QCounterTab import *

from src.gui.QUtils import center
from src.gui.widgets.QForms import QIpInputDialog

log = logging.getLogger()

# de transaction

#  Shared variables


#  Get item tree
# INITIALISATION


def setFont(Widget, Font):

    for child in Widget.children():
        try:
            child.setFont(Font)
            setFont(child, Font)
        except Exception:
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
        self.tabRefiller = QRefillerTab()
        # self.TabStat = QWidget()

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
        uim = QUIManager()
        self.setWindowIcon(uim.getWindowIcon("icon"))

        center(self)
        self.MainTab = QMainTab()
        self.setCentralWidget(self.MainTab)

        font = QFont()  # NOTE: Dirty trick to set the whole app font size
        font.setPointSize(16)
        setFont(self, font)

        #  Menu
        mainMenu = self.menuBar()  # Built in function that hold actions

        # Definitions
        configMenu = mainMenu.addMenu("&Config")
        # helpMenu = mainMenu.addMenu("&Aide")
        counterMenu = configMenu.addMenu("&Comptoir")
        ipMenu = configMenu.addMenu("&Adresse serveur")
        counterActionGroup = QActionGroup(self)
        self.counterActionGroup = QActionGroup(self)

        self.ipDialog = QIpInputDialog("Veuillez saisir l'adresse du serveur")
        self.ipDialog.setWindowTitle("IP Serveur")

        #  Settings
        # Menu & Actions
        dm = QDataManager()
        for counter in dm.counterList:
            # Create actions
            action = QAction(counter.getName(), self)
            action.triggered.connect(self.updateCounter)
            action.setCheckable(True)
            action.setData(counter)  # Looks like there's room for user defined data
            # Add the action to a group so that the actions are mutually exclusive
            self.counterActionGroup.addAction(action)
            # Set the current check on the right counter
            if counter == dm.counter:
                log.debug("Counter {} selected".format(counter))
                action.setChecked(True)
            # Add the action to the widget menu
            counterMenu.addAction(action)

        # Toolbar

    def ForceHistoryRefresh(self):
        pass

    def setServerAddress(self):
        pass

    def updateCounter(self):
        dm = QDataManager()
        action = self.sender()
        selectedCounter = action.data()
        dm.updateCounter(selectedCounter)
        log.info("Counter {} selected".format(selectedCounter))
