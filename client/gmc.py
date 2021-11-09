#!/usr/bin/env python
import sys
from pathlib import Path
import os

# sys.path.insert(1, "managers")
# sys.path.insert(1, "managers/com")
sys.path.insert(1, "src/managers")
sys.path.insert(1, "src/managers/com")  # The generated com files need it
from src.gui.GUI import *

from src.utils.logs import init_logging

# from qt_material import apply_stylesheet
# from qt_material import list_themes


# TODO: ENSURE BALANCE CAN'T HAVE ABSURDS VALUES (eg: 16.33333...)       [OK Money class + string]
# TODO: FIX MULTI-USER PANEL
# TODO: UNIFY KEY NAME BITWEEN THE SERVER AND THE CLIENT                 [OK GRPC]
# TODO: MAKE AUTOMATIC GRAPH
# TODO: FIND A EASIER WAY TO HANDLE TREEMODELS AND STUFF...              [OK QATOMS]
# TODO: ADD WARNING WHEN ADD HUGE AMOUNT ON CARDS
# TODO: HANDLE TRANSLATION
# TODO: ADD A TOOLBAR STATUS SINGLETON HANDLER                          [OK VIA QCONNECTOR]
# TODO: HANDLE CARD READER PLUG/UNPLUG                                  [OK]
# TODO: ADD TRADUCTION
# TODO: REPLACE all "from XXX import *" by to "from XXX import YYY"
# TODO: REPLACE THE "CONSOLE" MODULE BY A REAL BUILT-IN LOGGING MODULE

if __name__ == "__main__":
    init_logging()
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    #        apply_stylesheet(app, theme="dark_teal.xml")
    MainWindow = QMainMenu()
    # la fenêtre est rendue visible
    #    MainWindow.showMaximized()
    MainWindow.show()
    # VirtualCard.show()
    app.exec_()
