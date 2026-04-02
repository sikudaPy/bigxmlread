import sys

from PySide6.QtWidgets import (QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)
from PySide6.QtGui import *
from PySide6.QtCore import *

class TreeExample(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.layout.addWidget(self.tree)

        # Add dummy data
        for i in range(3):
            parent = QTreeWidgetItem(self.tree, [f"Item {i}"])
            QTreeWidgetItem(parent, ["Child"])

        # Connect expansion signal to clear the tree
        self.tree.itemExpanded.connect(self.clear_tree)
        
    def clear_tree(self, item):
        print(f"Expanding: {item.text(0)}. Clearing tree.")
        pass
        # This will remove all items, including the one just clicked
        #self.tree.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TreeExample()
    window.show()
    sys.exit(app.exec_())