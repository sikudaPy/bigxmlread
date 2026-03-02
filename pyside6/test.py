import sys

from PySide6.QtWidgets import (QApplication, QTreeWidget, QTreeWidgetItem)
from PySide6.QtGui import *
from PySide6.QtCore import *

app = QApplication(sys.argv)

tree = QTreeWidget()
tree.setHeaderLabels(["Название", "Значение"])
items = [QTreeWidgetItem(['index %i' % i]) for i in range(5)]
subitems = [QTreeWidgetItem(['index %i' % i]) for i in range(5)]

index = 0
for item in items:
    index = index +1
    tree.addTopLevelItem(item)
    item.setData(1, 0, "value "+str(index))
    
for subitem in subitems:
    item.addChild(subitem)
    subitem.setText(1, "parent "+str(item))
    subitem.setData(1, Qt.UserRole, item)   

# print("indexes:")
# for subitem in subitems:
#     print(tree.indexOfTopLevelItem(subitem),)
tree.resizeColumnToContents(0)
tree.resizeColumnToContents(1)

tree.show()
app.exec()