from enum import Enum
from PySide6.QtCore import QXmlStreamReader, QFile, QIODevice, Qt, Slot
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QTreeWidget, QWidget, QMessageBox, QTreeWidgetItem, QApplication, QPlainTextEdit, QVBoxLayout, QDialog


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


class BigXmlWidget(QTreeWidget, QWidget):

    def __init__(self, parent):
        super( BigXmlWidget, self ).__init__( parent )

        self.currentFile = QFile()
        self.readLevel = -1
        self.fOpenNew = True
        #folderIcon = QIcon()
        #folderIcon.addPixmap( QIcon(':/images/open.png'), QIcon.Normal, QIcon.On)
        #folderIcon.addPixmap( QIcon(':/images/close.png'), QIcon.Normal, QIcon.Off)

        HEADERS = (self.tr("Node/Attribute"), self.tr("Value"))
        self.setColumnCount(len(HEADERS))
        self.setHeaderLabels(HEADERS)
        self.setAlternatingRowColors(True)
        
        self.itemExpanded.connect(self.expandBigXmlItem)
        self.itemActivated.connect(self.enterBigXmlItem)


    def openFile(self, fileName: str, fOpenNew: bool):
        if self.fOpenNew:
            self.currentFile.close()
            self.currentFile.setFileName(fileName)
            if self.currentFile.open(QIODevice.ReadOnly | QIODevice.Text):
                self.currentFile.seek(0)
                self.readBigXMLtoLevel(3)
                return True
            else:
                QMessageBox.warning(self, self.tr("BigXmlReader"),
                                  self.tr("Cannot read file "+fileName+" - "+self.currentFile.errorString()))
                return False
        return True

    def readBigXMLtoLevel(self,levelDown: int):
        xml = QXmlStreamReader(self.currentFile)
        itemCurrent = QTreeWidgetItem("")
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.clear()
        level = 0
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
                            itemCurrent = item
                        itemCurrent.setText(0, xml.name())    
                        #itemCurrent.setData(0, Qt.UserRole, XmlItemType.Node)
                        #itemCurrent.setIcon(0, folderIcon) 
                        if level == levelDown:
                            item = QTreeWidgetItem("")
                            #item.setData(0, Qt.UserRole, XmlItemType.Empty)
                            itemCurrent.addChild(item)
                        else:
                            for attr in xml.attributes():
                                childItem = QTreeWidgetItem("-")
                                childItem.setText(0, attr.name())
                                childItem.setText(1, attr.value())
                                #childItem.setData(0, Qt.UserRole,XmlItemType.Attribute)
                                itemCurrent.addChild(childItem)
            
                case QXmlStreamReader.EndElement:
                    if level <= levelDown:
                        itemCurrent = itemCurrent.parent()
                    level = level - 1    

                case QXmlStreamReader.Characters | QXmlStreamReader.DTD | QXmlStreamReader.Comment:
                    if (level <= levelDown):
                        itemCurrent.setText(1, xml.text())
                        #itemCurrent.setData(1, Qt.UserRole,XmlItemType.Comment)
                        #itemCurrent.setIcon(0, bookmarkIcon)
                        #itemCurrent.takeChildren().clear()

        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        QApplication.restoreOverrideCursor()
        return not xml.error()
    
    @Slot()
    def expandBigXmlItem(self, itemBegin:  QTreeWidgetItem):
        pass
        #BigXmlItem* item = static_cast<BigXmlItem*>(itemBegin);
        if itemBegin:
            #QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            if itemBegin.childCount() == 1:
                if itemBegin.child(0).data(0, Qt.UserRole) == XmlItemType.Empty :

                    itemBegin.takeChildren().clear()
                    # QXmlStreamReader xml;

                #calculate current item
                # QHash<int, int> currentIndex = QHash() ;
                # int i = 0;
                # QTreeWidgetItem* item1 = item;
                # while( item1 != 0 ){
                #     if( item1->parent() == 0 ) currentIndex.insert(i,indexOfTopLevelItem(item1));
                #     else currentIndex.insert(i,item1->parent()->indexOfChild(item1));
                #     item1 = item1->parent();
                #     i++;
                # }
                # int k = 0;
                # int i2 = i / 2;
                # while( k < i2 ){
                #     int val = currentIndex.value(k);
                #     currentIndex.insert(k, currentIndex.value(i-k-1));
                #     currentIndex.insert(i-k-1, val);
                #     k++;
                # }
                # int maxLevel = i;

    #             QString strFilename;
    #             openFile(strFilename, xml, false);
    #             maxIndex.clear();
    #             bool InsideIndex = false;
    #             int level = 0;
    #             while( !xml.atEnd() ){

    #                 QXmlStreamReader::TokenType tokentype = xml.readNext();
    #                 switch (tokentype) {
    #                 case QXmlStreamReader::StartElement:
    #                 {
    #                     if(maxIndex.contains(level)) maxIndex.insert( level, maxIndex.value(level)+1);
    #                     else maxIndex.insert( level, 0);
    #                     level ++;

    #                     InsideIndex = isInsideIndex(currentIndex);

    #                     foreach(QXmlStreamAttribute attr, xml.attributes())
    #                     {
    #                         if(maxIndex.contains(level)) maxIndex.insert( level, maxIndex.value(level)+1);
    #                         else maxIndex.insert( level, 0);
    #                         if( InsideIndex && (level == maxLevel) ){
    #                             BigXmlItem* childItem = new BigXmlItem(item, BigXmlItem::Attribute);
    #                             childItem->setText(0, attr.name().toString());
    #                             childItem->setText(1, attr.value().toString());
    #                         }
    #                     }

    #                     if( InsideIndex && (level == maxLevel + 1)){
    #                         item = createChildItem(item, BigXmlItem::Node);
    #                         item->setText(0, xml.name().toString());
    #                         item->setIcon(0, folderIcon);
    #                         new BigXmlItem(item, BigXmlItem::Empty);
    #                     }
    #                 }
    #                     break;
    #                 case QXmlStreamReader::EndElement:
    #                     if( InsideIndex && (level > maxLevel) &&(level <= maxLevel + 1)){
    #                         if(item) item = static_cast<BigXmlItem*>(item->parent());
    #                     }
    #                     maxIndex.remove(level);
    #                     level --;
    #                     break;
    #                 case QXmlStreamReader::Characters:
    #                 case QXmlStreamReader::DTD:
    #                 case QXmlStreamReader::Comment:
    #                     if( InsideIndex && (level > maxLevel) && (level <= maxLevel + 1)){
    #                         QString name(xml.text().toString().simplified());
    #                         if( (name.size() > 0) && item ){
    #                             item->setText(1, name);
    #                             item->takeChildren().clear();
    #                             item->setIcon(0, bookmarkIcon);
    #                             item->setXmlType(BigXmlItem::Comment);
    #                         }
    #                     }
    #                     break;
    #                 default: break;
    #                 }
    #             }
    #         }
    #     }
    # }
    #QTreeWidget::expandItem(itemBegin);
    #setCurrentItem ( itemBegin );

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

    