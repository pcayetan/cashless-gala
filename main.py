from IHM import *








def parseFile(File,separator=";", Header=True, Headers=[]):
    """Parse a file"""



if (__name__ == '__main__'):
    # Première étape : création d'une application Qt avec QApplication
    #    afin d'avoir un fonctionnement correct avec IDLE ou Spyder
    #    on vérifie s'il existe déjà une instance de QApplication
    app = QApplication.instance() 
    if not app: # sinon on crée une instance de QApplication
        app = QApplication(sys.argv)

    MainWindow=QMainMenu()
    font=QFont()
    font.setPointSize(12)
    setFont(MainWindow,font)
    FakeCard= QFakeCard()
    FakeCard.LinkWidget(MainWindow.MainTab.TabCounter.NFCDialog)

#    W.Layout.addStretch(1)
    #Test Fading-In / Out widget

     
    #FadingIn=QFadingWidget()
    #FadingIn.show()


    #MyTree=Tree()
    #MyTree.show()        


    # la fenêtre est rendue visible
    MainWindow.show()
    FakeCard.show()
    # exécution de l'application, l'exécution permet de gérer les événements
    app.exec_()
