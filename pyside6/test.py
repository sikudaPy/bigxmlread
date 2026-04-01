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
    indexModel = tree.indexFromItem(item)
    item.setData(1, Qt.DisplayRole, str(indexModel.row())+'-'+str(indexModel.column()))
    
for subitem in subitems:
    item.addChild(subitem)
    subitem.setText(1, "parent "+str(item))
    #subitem.setData(1, Qt.UserRole, item)   

# print("indexes:")
# for subitem in subitems:
#     print(tree.indexOfTopLevelItem(subitem),)
tree.resizeColumnToContents(0)
tree.resizeColumnToContents(1)

# for i in range(3):
#     item = tree.itemAt(0, 0)
#     if item:
#         item.setText(1, str(i))

#     item = tree.itemAt(1, 1)
#     if item:
#         item.setText(1, '-'+str(i)) 

#itemFromIndex(index)           


tree.show()
app.exec()