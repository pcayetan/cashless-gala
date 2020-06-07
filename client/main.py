from GUI import *

# TODO: ENSURE BALANCE CAN'T HAVE ABSURDS VALUES (eg: 16.33333...)
# TODO: FIX MULTI-USER PANEL
# TODO: UNIFY KEY NAME BITWEEN THE SERVER AND THE CLIENT
# TODO: MAKE AUTOMATIC GRAPH
# TODO: FIND A EASIER WAY TO HANDLE TREEMODELS AND STUFF...
# TODO: ADD WARNING WHEN ADD HUGE AMOUNT ON CARDS
# TODO: HANDLE TRANSLATION
# TODO: ADD A TOOLBAR STATUS SINGLETON HANDLER                          [OK VIA QCONNECTOR]
# TODO: HANDLE CARD READER PLUG/UNPLUG                                  [OK]

if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    MainWindow = QMainMenu()
    # FakeCard = QFakeCard()

    # la fenêtre est rendue visible
    #    MainWindow.showMaximized()
    MainWindow.show()
    # FakeCard.show()
    app.exec_()
