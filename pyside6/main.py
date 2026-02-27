import sys
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                               QMessageBox, QTextEdit)

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        #labels = list( self.tr("Node/Attribute"), self.tr("Value"))

        #bigxmlWidget: BigXmlReader 

        #bigxmlWidget.header()->setSectionResizeMode(QHeaderView::ResizeToContents);
        #bigxmlWidget.setHeaderLabels(labels);
        #setCentralWidget(&bigxmlWidget);

        #createActions();

        #Menu
        button_action = QAction(QIcon("bug.png"), "&Your button", self)
        button_action.setStatusTip("This is your button")
        #button_action.triggered.connect(self.toolbar_button_clicked)
        button_action.setCheckable(True)
        #toolbar.addAction(button_action)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)
        self.statusBar().showMessage(self.tr("Ready"));

        self.setWindowTitle(self.tr("BigXmlReader"));
        self.resize(480, 320);
    
    #def createMenus(self):
 
        # fileMenu = self.menuBar().addMenu(self.tr("&File"));
        # fileMenu.addAction(openAct);
        # fileMenu.addSeparator();
        # fileMenu.addAction(exitAct);
        # menuBar().addSeparator();

    # findMenu = menuBar()->addMenu(tr("Find"));
    # findMenu->addAction(findAct);
    # findMenu->addAction(findActNext);
    # //findMenu->addSeparator();

    # helpMenu = menuBar()->addMenu(tr("&Help"));
    # helpMenu->addAction(aboutAct);
    # helpMenu->addAction(aboutQtAct);


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())