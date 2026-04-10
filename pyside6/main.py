import sys

from PySide6.QtCore import (QByteArray, QFile, QFileInfo, QSaveFile, QSettings,
                            QTextStream, Qt, Slot, QXmlStreamReader, QDir)
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                               QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit)
from bigxmlwidget import BigXmlWidget, QPlainTextEdit, QPushButton 


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.findLayout = QHBoxLayout()
        # self.findTextLabel = QLabel(self.tr("Find:"))
        # self.findLayout.addWidget(self.findTextLabel, stretch=10, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
        self.findText = QLineEdit()
        self.findText.setPlaceholderText(self.tr(" Find text in xml "))
        self.findLayout.addWidget(self.findText, stretch=100, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
        self.findButton = QPushButton(self.tr(" Find... "))
        self.findLayout.addWidget(self.findButton, stretch=10, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
                
        self.treeWidget = BigXmlWidget(self.centralwidget)
        self.verticalLayout.addWidget(self.treeWidget, stretch=1000)
        self.setCentralWidget(self.centralwidget)

        self.findButton.clicked.connect(self.find)
        self.create_actions()
        self.create_menus()
        self.statusBar().showMessage(self.tr("Ready"));
        self.setWindowTitle(self.tr("BigXmlReader"))
        self.resize(480, 320)

    @Slot()
    def open(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Choose XML file"), QDir.currentPath(), self.tr("XML Files (*.xml)"))
        if fileName:
            if self.treeWidget.openFile(fileName[0], True):
                self.verticalLayout.insertLayout(0, self.findLayout)

    # @Slot()
    def find(self):
        findString = self.findText.text()

        item = self.treeWidget.currentItem()
        startWithEntry = []
        if item: 
            startWithEntry = item.data(1, Qt.UserRole)
        currentEntry = self.treeWidget.findInXML(findString, startWithEntry)
        if currentEntry:
            self.treeWidget.expandTocurrentEntry(currentEntry)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle(self.tr("BigXmlReader"))
            dlg.setText(self.tr("text: '"+findString+"' not found"))
            dlg.exec() 

    @Slot()
    def about(self):
        QMessageBox.about(self, self.tr("About BigXmlReader"),
                          self.tr("The <b>BigXmlReader</b> example demonstrates how to quick read big xml file. E-mail: sikuda@yandex.ru"))

    def create_menus(self):
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addAction(self._open_act)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_act)

        # self.menuBar().addSeparator()

        # self._edit_menu = self.menuBar().addMenu("&Find")
        # self._edit_menu.addAction(self._find_act)
        # self._edit_menu.addAction(self._findnext_act)

        self.menuBar().addSeparator()

        self._help_menu = self.menuBar().addMenu("&Help")
        self._help_menu.addAction(self._about_act)
        self._help_menu.addAction(self._about_qt_act)

    def create_actions(self):

        icon = QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen, QIcon(':/images/open.png'))
        self._open_act = QAction( icon, self.tr("&Open..."), self,
                                 shortcut=QKeySequence.StandardKey.Open,
                                 statusTip=self.tr("Open an existing file"),
                                 triggered=self.open)
        
        icon = QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit)
        self._exit_act = QAction(icon, self.tr("E&xit"), self, shortcut="Ctrl+Q",
                                 statusTip=self.tr("Exit the application"), triggered=self.close)

        #---------------------------------------------------------

        # icon = QIcon.fromTheme(QIcon.ThemeIcon.EditFind, QIcon(':/images/find.png'))
        # self._find_act = QAction(icon, self.tr("&Find..."), self,
        #                          shortcut=QKeySequence.StandardKey.Find,
        #                          statusTip=self.tr("Find"),
        #                          triggered=self.find)

        # icon = QIcon.fromTheme(QIcon.ThemeIcon.EditFind, QIcon(':/images/find.png'))
        # self._findnext_act = QAction(icon, self.tr("&Find next..."), self,
        #                          shortcut=QKeySequence.StandardKey.FindNext,
        #                          statusTip=self.tr("Find next"),
        #                          triggered=self.findNext)

        #----------------------------------------------------------

        icon = QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout)
        self._about_act = QAction(icon, self.tr("&About"), self,
                                  statusTip=self.tr("Show the application's About box"),
                                  triggered=self.about)

        self._about_qt_act = QAction(self.tr("About &Qt"), self,
                                     statusTip=self.tr("Show the Qt library's About box"),
                                     triggered=qApp.aboutQt)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())