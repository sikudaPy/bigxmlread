from enum import Enum
from PySide6.QtCore import QXmlStreamReader, QFile, QIODevice, Qt, Slot
from PySide6.QtGui import QCursor, QFont, QIcon, QPixmap
from PySide6.QtWidgets import QStyle, QTreeWidget, QWidget, QMessageBox, QTreeWidgetItem, QApplication, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QDialog


class XmlItemType(Enum):
    Empty = 0
    Node = 1
    Attribute = 2
    Comment = 3

intTreeInitialReadLevel   = 3 #initial open level
intTreeInitialExpandLevel = 1 #initial expand level

class BigXmlWidget(QTreeWidget, QWidget):

    def __init__(self, parent):
        super( BigXmlWidget, self ).__init__( parent )

        self.fDebug = True  #show debug column  

        self.currentFile = QFile()
        # self.findString = ""
        self.readLevel = -1
        self.fOpenNew = True
        font = QFont("Arial", 10) # Шрифт и размер
        self.setFont(font)

        style = QApplication.style()
        self.icon_dirOpen = style.standardIcon(QStyle.SP_DirOpenIcon)
        self.icon_dirClose = style.standardIcon(QStyle.SP_DirClosedIcon)
        self.icon_file = style.standardIcon(QStyle.SP_FileIcon)

        if self.fDebug: HEADERS = (self.tr("Node/Attribute"), self.tr("Value"), self.tr("DEBUG"))
        else: HEADERS = (self.tr("Node/Attribute"), self.tr("Value"))
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
                self.itemExpanded.disconnect()
                self.currentFile.seek(0)
                self.readBigXMLtoLevel()
                self.currentFile.close()
                self.itemExpanded.connect(self.expandBigXmlItem)
                return True
            else:
                QMessageBox.warning(self, self.tr("BigXmlReader"),
                                  self.tr("Cannot read file "+fileName+" - "+self.currentFile.errorString()))
                return False
        return True

    #open file to initial level
    def readBigXMLtoLevel(self, levelDown: int = 0):
        xml = QXmlStreamReader(self.currentFile)
        itemCurrent = QTreeWidgetItem("")
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.clear()
        level = 0
        indexEntry = [0]
        levelDown = intTreeInitialReadLevel
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
                        if self.fDebug: itemCurrent.setText(2, ", ".join(map(str,indexEntry)))
                        
                        if level == levelDown:
                            item = QTreeWidgetItem("")
                            item.setData(0, Qt.UserRole, XmlItemType.Empty)
                            itemCurrent.addChild(item)
                            itemCurrent.setIcon(0, self.icon_dirClose)
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
                                if self.fDebug: childItem.setText(2, ", ".join(map(str,indexEntry)))
                            indexEntry.pop()
                            #itemCurrent.setIcon(0, self.icon_dirOpen)

                case QXmlStreamReader.EndElement:
                    if level <= levelDown:
                        itemCurrent = itemCurrent.parent()
                        indexEntry.pop()
                    level = level - 1 
                    
                case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                    if (level <= levelDown):
                        itemCurrent.setText(1, xml.text())
        
        self.currentFile.close() 
        self.expandToDepth(intTreeInitialExpandLevel)
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        QApplication.restoreOverrideCursor()
        return not xml.error()
    
    @Slot()
    def handleCollapsed(self, item):
        if item.icon(0):
            item.setIcon(0, self.icon_dirClose)

    #expand next level with empty node
    @Slot()
    def expandBigXmlItem(self, itemBegin):
  
        #last item is Empty - need repead read xml
        fNeedExpand = False
        count = itemBegin.childCount()
        if count > 0 and itemBegin.child(count-1).data(0, Qt.UserRole) == XmlItemType.Empty:
            fNeedExpand = True
            itemBegin.removeChild(itemBegin.child(count-1))

        if fNeedExpand:
            currentEntry =  itemBegin.data(1, Qt.UserRole)
            if self.currentFile.open(QIODevice.ReadOnly | QIODevice.Text):
                self.currentFile.seek(0)
                xml = QXmlStreamReader(self.currentFile)
                level = 0
                item = None
                indexEntry = [-1]
                itemCurrent = None 
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
                                    item.setText(0, xml.name())    
                                    item.setData(0, Qt.UserRole, XmlItemType.Node)
                                    item.setData(1, Qt.UserRole, indexEntry)
                                    if self.fDebug: item.setText(2, ", ".join(map(str,indexEntry)))
                                    iAttr = 0
                                    indexEntry.insert(level+1,0)
                                    for attr in xml.attributes():
                                        childItem = QTreeWidgetItem("-")
                                        childItem.setText(0, attr.name())
                                        childItem.setText(1, attr.value())
                                        childItem.setData(0, Qt.UserRole,XmlItemType.Attribute)
                                        childItem.setIcon(0, self.icon_file)
                                        item.addChild(childItem)
                                        
                                        indexEntry[level]=iAttr 
                                        childItem.setData(1, Qt.UserRole, indexEntry)
                                        iAttr = iAttr + 1
                                        if self.fDebug: childItem.setText(2, ", ".join(map(str,indexEntry)))
                                    indexEntry.pop()
                                    itemCurrent.addChild(item) 
                                if isNextLevel(indexEntry, currentEntry, 2) and item:
                                    #item.takeChildren().clear()    
                                    item2 = QTreeWidgetItem("")
                                    item2.setData(0, Qt.UserRole, XmlItemType.Empty)
                                    item.addChild(item2)
                                    itemBegin.setIcon(0, self.icon_dirOpen)
                                    item.setIcon(0, self.icon_dirClose) 
                                else: 
                                    if isOnTheWay(indexEntry, currentEntry):   
                                        itemCurrent = itemCurrent.child(indexEntry[level-1])          

                        case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                            if isNextLevel(indexEntry, currentEntry) and len(indexEntry) == level:        
                                #itemCurrent.child(indexEntry[level-1]).setText(1, xml.text()) 
                                if itemCurrent.childCount() > 0:
                                    itemCurrent.child(itemCurrent.childCount()-1).setText(1, xml.text()) 
                                        
                        case QXmlStreamReader.EndElement:     
                            if isOnTheWay(indexEntry, currentEntry):                         
                                itemCurrent = itemCurrent.parent()
                            if len(indexEntry) > level:    
                                indexEntry.pop()    
                            level = level - 1
                            item = None

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

        textDialog.exec()
        textDialog.close()

    #-------------------------------- find String ---------------------------------

    #find  self.string in XML end return indexEntry
    def findInXML(self, findString: str, startWithEntry=[]):

        if self.currentFile.open(QIODevice.ReadOnly | QIODevice.Text):
            self.currentFile.seek(0)
            xml = QXmlStreamReader(self.currentFile)
            level = 0
            indexEntry = [-1]
            fFoundinAttrs = False
            while not xml.atEnd():
                tokentype = xml.readNext() 
                match tokentype:
                    case QXmlStreamReader.StartElement:
                        level = level + 1
                        if level == 1:
                            indexEntry[0] = indexEntry[0]+1
                        else:
                            if len(indexEntry) < level:
                                indexEntry.insert(level-1, -1) 
                            indexEntry[level-1] = indexEntry[level-1]+1

                            if findString in xml.name():
                                if isMore(indexEntry, startWithEntry): 
                                    break
                            for attr in xml.attributes():
                                if (findString in attr.name() or findString in attr.value()):
                                    if isMore(indexEntry, startWithEntry):
                                        fFoundinAttrs = True
                                        break 
                            if fFoundinAttrs:
                                break       
                    case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                        if findString in xml.text():
                            if isMore(indexEntry, startWithEntry):
                                break                               
                    case QXmlStreamReader.EndElement:     
                        level = level - 1

            self.currentFile.close() 

            if xml.atEnd(): return None       
            else: 
                if self.fDebug:  ", ".join(map(str,indexEntry))
                return indexEntry

        else: return None  

    #expand tree to current entry index
    def expandToEntry(self, currentEntry):
  
        if currentEntry:
            if self.currentFile.open(QIODevice.ReadOnly | QIODevice.Text):
                self.currentFile.seek(0)
                xml = QXmlStreamReader(self.currentFile)
                level = 0
                item = None
                indexEntry = [-1]
                itemCurrent = None
                fNeedReadXml = False 
                while not xml.atEnd():
                    tokentype = xml.readNext() 
                    match tokentype:
                        case QXmlStreamReader.StartElement:
                            level = level + 1
                            if level == 1:
                                indexEntry[0] = indexEntry[0]+1
                                if isOnTheNextEntry(indexEntry, currentEntry): 
                                    itemCurrent = self.topLevelItem(indexEntry[0])
                            else:
                                if len(indexEntry) < level:
                                    indexEntry.insert(level-1, -1) 
                                indexEntry[level-1] = indexEntry[level-1]+1

                                if isOnTheNextEntry(indexEntry, currentEntry): 
                                
                                    if len(indexEntry) <= len(currentEntry):
                                        if fNeedReadXml:
                                            item = QTreeWidgetItem("+")                         
                                            item.setText(0, xml.name())    
                                            item.setData(0, Qt.UserRole, XmlItemType.Node)
                                            item.setData(1, Qt.UserRole, indexEntry)
                                            if self.fDebug: item.setText(2, ", ".join(map(str,indexEntry)))
                                            iAttr = 0
                                            indexEntry.insert(level+1,0)
                                            for attr in xml.attributes():
                                                childItem = QTreeWidgetItem("-")
                                                childItem.setText(0, attr.name())
                                                childItem.setText(1, attr.value())
                                                childItem.setData(0, Qt.UserRole,XmlItemType.Attribute)
                                                childItem.setIcon(0, self.icon_file)
                                                item.addChild(childItem)
                                                
                                                indexEntry[level]=iAttr 
                                                childItem.setData(1, Qt.UserRole, indexEntry)
                                                iAttr = iAttr + 1
                                                if self.fDebug: childItem.setText(2, ", ".join(map(str,indexEntry)))
                                            indexEntry.pop()
                                            itemCurrent.addChild(item) 

                                        item2 = itemCurrent.child(indexEntry[level-1])
                                        if item2 is None:
                                            pass
                                        else: 
                                            itemCurrent = item2    
                                            count = itemCurrent.childCount()
                                            if count > 0 and itemCurrent.child(count-1).data(0, Qt.UserRole) == XmlItemType.Empty:
                                                itemCurrent.removeChild(itemCurrent.child(count-1)) 
                                                fNeedReadXml = True    
                                            
                                    if fNeedReadXml and len(indexEntry) == len(currentEntry)+1:
                                        if itemCurrent.childCount() == 0:
                                            item = QTreeWidgetItem("")
                                            item.setData(0, Qt.UserRole, XmlItemType.Empty)
                                            itemCurrent.addChild(item)
                                            itemCurrent.setIcon(0, self.icon_dirClose) 
 
                        case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                            if fNeedReadXml and len(indexEntry) == len(currentEntry): 
                                itemCurrent.setText(1, xml.text())       
                                        
                        case QXmlStreamReader.EndElement:
                            if currentEntry == indexEntry:
                                self.setCurrentItem(itemCurrent) 

                            if len(indexEntry) > level:    
                                indexEntry.pop() 
                            if isOnTheNextEntry(indexEntry, currentEntry) and len(indexEntry) <= len(currentEntry):                         
                                itemCurrent = itemCurrent.parent()       
                            level = level - 1

                self.currentFile.close()  

#--------------------------- index working ------------------------------------
#index on the way in currentEntry
def isOnTheWay(indexEntry, currentEntry):
    if len(indexEntry) <= len(currentEntry):
        for i in range(len(indexEntry)):
            if  currentEntry[i] != indexEntry[i]:
                return False
        return True    
    return False 

#index on the way of entry (0,8,0), (0,8,0,3) (0,8,0,3,1) way of(0,8,0,2)
def isOnTheNextEntry(indexEntry, currentEntry):
    if len(indexEntry) <= len(currentEntry)+1:
        lenMin = min(len(indexEntry), len(currentEntry)-1)
        for i in range(lenMin):
            if  currentEntry[i] != indexEntry[i]:
                return False
        return True    
    return False    


#index on next level for current (step1 [0,8,0,1] in [0,8,0] )    
def isNextLevel(indexEntry, currentEntry, levelStep=1):
    if len(indexEntry) == len(currentEntry)+levelStep:
        for i in range(len(currentEntry)):
            if  currentEntry[i] != indexEntry[i]:
                return False
        return True    
    return False 

#more indexEntry inside current [0,8,0,1],[0,8,0,1,2] inside [0,8,0]
def isMore(indexEntry, currentEntry):
    lenMin = min(len(indexEntry), len(currentEntry))
    for i in range(lenMin):
        if  indexEntry[i] > currentEntry[i]:
                return True
    if len(indexEntry) > len(currentEntry): return True
    else: return False 

