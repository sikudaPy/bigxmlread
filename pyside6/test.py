import sys

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

#class TreeExample(QWidget):
    # def __init__(self):
    #     super().__init__()
    #     self.layout = QVBoxLayout(self)
    #     self.tree = QTreeWidget()
    #     self.tree.setColumnCount(1)
    #     self.layout.addWidget(self.tree)

    #     # Add dummy data
    #     for i in range(3):
    #         parent = QTreeWidgetItem(self.tree, [f"Item {i}"])
    #         QTreeWidgetItem(parent, ["Child"])

    #     # Connect expansion signal to clear the tree
    #     self.tree.itemExpanded.connect(self.clear_tree)
        
    # def clear_tree(self, item):
    #     for i in range(3):
    #         parentItem = self.tree.topLevelItem(i)
    #         print(f"Next: {parentItem.text(0)}. ")
    #     pass
    #     # This will remove all items, including the one just clicked
    #     #self.tree.clear()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()

        layout2.addWidget(Color('red'))
        layout2.addWidget(Color('yellow'))
        layout2.addWidget(Color('purple'))

        layout1.addLayout( layout2 )

        layout1.addWidget(Color('green'))

        layout3.addWidget(Color('red'))
        layout3.addWidget(Color('purple'))

        layout1.addLayout( layout3 )

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    #sys.exit(app.exec_())