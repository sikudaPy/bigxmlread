from enum import Enum
from PySide6.QtCore import QXmlStreamReader, QFile, QIODevice, Qt, Slot
from PySide6.QtGui import QCursor, QFont, QIcon
from PySide6.QtWidgets import QStyle, QTreeWidget, QWidget, QMessageBox, QTreeWidgetItem, QApplication, QPlainTextEdit, QVBoxLayout, QDialog


class XmlItemType(Enum):
    Empty = 0
    Node = 1
    Attribute = 2
    Comment = 3

# class BigXmlItem(QTreeWidgetItem):
#      def __init__(self, parent, type):
#         super( BigXmlItem, self ).__init__( parent)
#         self.__type = type

#      @property
#      def type(self):
#         return self.__type   

intTreeInitialLevel = 3 #initial open level

class BigXmlWidget(QTreeWidget, QWidget):

    def __init__(self, parent):
        super( BigXmlWidget, self ).__init__( parent )

        self.currentFile = QFile()
        self.readLevel = -1
        self.fOpenNew = True
        font = QFont("Arial", 10) # Шрифт и размер
        self.setFont(font)

        style = QApplication.style()
        self.icon_dirOpen = style.standardIcon(QStyle.SP_DirOpenIcon)
        self.icon_dirClose = style.standardIcon(QStyle.SP_DirClosedIcon)
        self.icon_file = style.standardIcon(QStyle.SP_FileIcon)
        #folderIcon = QIcon()
        #folderIcon.addPixmap( QIcon(':/images/open.png'), QIcon.Normal, QIcon.On)
        #folderIcon.addPixmap( QIcon(':/images/close.png'), QIcon.Normal, QIcon.Off)

        HEADERS = (self.tr("Node/Attribute"), self.tr("Value"), self.tr("DEBUG"))
        self.setColumnCount(len(HEADERS))
        self.setHeaderLabels(HEADERS)
        self.setAlternatingRowColors(True)
        
        self.itemExpanded.connect(self.expandBigXmlItem)
        self.itemCollapsed.connect(self.handleCollapsed)
        self.itemActivated.connect(self.enterBigXmlItem)


    def openFile(self, fileName: str, fOpenNew: bool):
        if self.fOpenNew:
            self.currentFile.setFileName(fileName)
            if self.currentFile.open(QIODevice.ReadOnly | QIODevice.Text):
                self.currentFile.seek(0)
                self.readBigXMLtoLevel(intTreeInitialLevel)
                self.currentFile.close()
                return True
            else:
                QMessageBox.warning(self, self.tr("BigXmlReader"),
                                  self.tr("Cannot read file "+fileName+" - "+self.currentFile.errorString()))
                return False
        return True

    def readBigXMLtoLevel(self,levelDown: int = 0):
        xml = QXmlStreamReader(self.currentFile)
        itemCurrent = QTreeWidgetItem("")
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.clear()
        level = 0
        indexEntry = [0]
        while not xml.atEnd():
            tokentype = xml.readNext() 
            match tokentype:
                case QXmlStreamReader.StartElement:
                    level = level+1
                    if level <= levelDown:
                        if level == 1:
                            itemCurrent = QTreeWidgetItem("+")
                            self.addTopLevelItem(itemCurrent)
                        else:
                            item = QTreeWidgetItem("+")
                            itemCurrent.addChild(item)
                            indexEntry.insert(level, itemCurrent.childCount()-1)
                            itemCurrent = item
                        itemCurrent.setText(0, xml.name())    
                        itemCurrent.setData(0, Qt.UserRole, XmlItemType.Node)

                        itemCurrent.setData(1, Qt.UserRole, indexEntry)
                        #DEBUG
                        itemCurrent.setText(2, ", ".join(map(str,indexEntry)))
                        
                        #itemCurrent.setIcon(0, self.icon_dirOpen)
                        if level == levelDown:
                            item = QTreeWidgetItem("")
                            item.setData(0, Qt.UserRole, XmlItemType.Empty)
                            itemCurrent.addChild(item)
                            #itemCurrent.setIcon(0, self.icon_dirClose)
                        else:
                            iAttr = 0
                            indexEntry.insert(level+1,0)
                            for attr in xml.attributes():
                                childItem = QTreeWidgetItem("-")
                                childItem.setText(0, attr.name())
                                childItem.setText(1, attr.value())
                                childItem.setData(0, Qt.UserRole,XmlItemType.Attribute)
                                childItem.setIcon(0, self.icon_file)
                                itemCurrent.addChild(childItem)
                                 
                                indexEntry[level]=iAttr 
                                childItem.setData(1, Qt.UserRole, indexEntry)
                                iAttr = iAttr + 1
                                #DEBUG
                                childItem.setText(2, ", ".join(map(str,indexEntry)))
                            indexEntry.pop()

                case QXmlStreamReader.EndElement:
                    if level <= levelDown:
                        itemCurrent = itemCurrent.parent()
                        indexEntry.pop()
                    level = level - 1 
                    
                case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                    if (level <= levelDown):
                        itemCurrent.setText(1, xml.text())
                        #itemCurrent.setData(1, Qt.UserRole,XmlItemType.Comment)
                        #itemCurrent.setIcon(0, bookmarkIcon)
                        #itemCurrent.takeChildren().clear()
        
        self.expandToDepth(intTreeInitialLevel-2)
        self.resizeColumnToContents(0)
        QApplication.restoreOverrideCursor()
        return not xml.error()
    
    @Slot()
    def handleCollapsed(self, item):
        #item.setIcon(0, self.icon_dirClose)
        pass

    @Slot()
    def expandBigXmlItem(self, itemBegin):
        if itemBegin.childCount() == 1:
            if itemBegin.child(0).data(0, Qt.UserRole) == XmlItemType.Empty:
                # itemBegin.takeChildren().clear()
                currentEntry = itemBegin.data(1, Qt.UserRole)
                print(", ".join(map(str,currentEntry)))
                if self.currentFile.open(QIODevice.ReadOnly | QIODevice.Text):
                    self.currentFile.seek(0)
                
                    xml = QXmlStreamReader(self.currentFile)
                    level = 0
                    indexEntry = [-1]
                    itemCurrent = None
                    fNeedReadData = False 
                    while not xml.atEnd():
                        tokentype = xml.readNext() 
                        match tokentype:
                            case QXmlStreamReader.StartElement:
                                level = level + 1
                                if level == 1:
                                    indexEntry[0] = indexEntry[0]+1
                                    if isOnTheWay(indexEntry, currentEntry): 
                                        itemCurrent = self.topLevelItem(indexEntry[0])
                                else:
                                    if len(indexEntry) < level:
                                        indexEntry.insert(level-1, -1) 
                                    indexEntry[level-1] = indexEntry[level-1]+1

                                    if isNextLevel(indexEntry, currentEntry):
                                        item = QTreeWidgetItem("+")
                                        itemCurrent.addChild(item)
                                        indexEntry.insert(level, itemCurrent.childCount()-1)
                                        itemCurrent = item
                                        itemCurrent.setText(0, xml.name())    
                                        itemCurrent.setData(0, Qt.UserRole, XmlItemType.Node)
                                        itemCurrent.setData(1, Qt.UserRole, indexEntry)
                                        iAttr = 0
                                        indexEntry.insert(level+1,0)
                                        for attr in xml.attributes():
                                            childItem = QTreeWidgetItem("-")
                                            childItem.setText(0, attr.name())
                                            childItem.setText(1, attr.value())
                                            childItem.setData(0, Qt.UserRole,XmlItemType.Attribute)
                                            childItem.setIcon(0, self.icon_file)
                                            itemCurrent.addChild(childItem)
                                            
                                            indexEntry[level]=iAttr 
                                            childItem.setData(1, Qt.UserRole, indexEntry)
                                            iAttr = iAttr + 1
                                            #DEBUG
                                            childItem.setText(2, ", ".join(map(str,indexEntry)))
                                        indexEntry.pop()
                                        item = QTreeWidgetItem("")
                                        item.setData(0, Qt.UserRole, XmlItemType.Empty)
                                        itemCurrent.addChild(item)    
                                        #break
                                    else: 
                                        if isOnTheWay(indexEntry, currentEntry):   
                                            itemCurrent = itemCurrent.child(indexEntry[level-1])
                                            #Empty_child
                                            fNeedReadData = False
                                            if itemCurrent:
                                                if itemCurrent.childCount() == 1:
                                                    if itemCurrent.child(0).data(0, Qt.UserRole) == XmlItemType.Empty and indexEntry == currentEntry:
                                                        itemCurrent.takeChildren().clear()
                                                        #fNeedReadData = True           

                                    # iAttrs = xml.attributes().count()
                                    # if iAttrs > 0:
                                    #     indexEntry.insert(level+1, iAttrs-1) 
                                    #     #indexEntry.pop() 

                                # if itemCurrent: print(itemCurrent.text(0))
                                # print(", ".join(map(str,indexEntry)))

                            case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                                if isNextLevel(indexEntry, currentEntry):        
                                    itemCurrent.setText(1, xml.text())    
                                            
                            case QXmlStreamReader.EndElement:     
                                if isOnTheWay(indexEntry, currentEntry):                         
                                    itemCurrent = itemCurrent.parent()
                                if len(indexEntry) > level:
                                    indexEntry.pop()    
                                #if fNeedReadData:
                                #    break
                                level = level - 1

                    self.currentFile.close()                


    @Slot()
    def enterBigXmlItem(self, itemBegin: QTreeWidgetItem):

        label = QPlainTextEdit(self)
        label.setPlainText(itemBegin.text(1));
        label.setReadOnly(True);
        label.setMaximumHeight(200);

        textDialog = QDialog(self)
        textDialog.setMinimumSize(320, 240)
        textDialog.setLayout(QVBoxLayout())
        textDialog.layout().addWidget(label)

        textDialog.setWindowTitle(self.tr("BigXmlReader"))
        #connect(okButton, SIGNAL(pressed()), &textDialog, SLOT(accept()));

        textDialog.exec()
        textDialog.close()

#index on the way in currentEntry
def isOnTheWay(indexEntry, currentEntry):
    if len(indexEntry) <= len(currentEntry):
        for i in range(len(indexEntry)):
            if  currentEntry[i] != indexEntry[i]:
                return False
        return True    
    return False    
    
def isNextLevel(indexEntry, currentEntry):
    if len(indexEntry) == len(currentEntry)+1:
        for i in range(len(currentEntry)):
            if  currentEntry[i] != indexEntry[i]:
                return False
        return True    
    return False     