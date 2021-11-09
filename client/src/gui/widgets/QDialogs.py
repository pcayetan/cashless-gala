from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from src.managers.QDataManager import QDataManager
from src.managers.QNFCManager import QNFCManager
from src.managers.QUIManager import QUIManager

from src.gui.QUtils import center

# Collection of widgets based on dialog widgets


class QErrorDialog(QMessageBox):
    def __init__(
        self,
        title="Erreur",
        message="Erreur",
        info="Une erreur est survenue",
        icon=QMessageBox.Warning,
        parent=None,
    ):
        super().__init__(parent)

        self.setText(message)
        self.setInformativeText(info)
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(icon)

        #        self.setWindowIcon()
        self.setWindowTitle(title)
        self.setBaseSize(QSize(800, 400))
        center(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setFixedWidth(600)
        self.setFixedHeight(200)


class QWarningDialog(QMessageBox):
    def __init__(
        self,
        title="Erreur",
        message="Erreur",
        info="Une erreur est survenue",
        icon=QMessageBox.Warning,
        parent=None,
    ):
        super().__init__(parent)

        self.setText(message)
        self.setInformativeText(info)
        self.setStandardButtons(QMessageBox.Ok)
        self.setIcon(icon)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))

        #        self.setWindowIcon()
        self.setWindowTitle(title)
        self.setBaseSize(QSize(800, 400))
        center(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setFixedWidth(600)
        self.setFixedHeight(200)


class QNFCDialog(QDialog):
    cardInserted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uim = QUIManager()
        nfcm = QNFCManager()
        # Definition
        self.mainLayout = QVBoxLayout()
        self.label = QLabel()
        self.setFixedSize(450, 400)

        # Layout
        self.mainLayout.addWidget(self.label)
        self.setLayout(self.mainLayout)

        nfcm.cardInserted.connect(self.proceed)

        # Setup
        movie = uim.getAnimation("show-card-animation")
        self.label.setMovie(movie)
        movie.start()

        self.setWindowTitle("Veuillez présenter une carte devant le lecteur")
        self.setWindowIcon(uim.getIcon("nfc-icon"))

        center(self)

    def proceed(self):
        self.cardInserted.emit()
        self.done(0)
