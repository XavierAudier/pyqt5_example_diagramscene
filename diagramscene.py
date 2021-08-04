from enum import IntEnum
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, pyqtSignal, QLineF, QPointF
from PyQt5.QtGui import QPen, QPolygonF, QFont, QColor, QBrush
from diagramitem import DiagramType, DiagramItem
from diagramtextitem import DiagramTextItem
from arrow import Arrow


class Mode(IntEnum):
    InsertItem = 0
    InsertLine = 1
    InsertText = 2
    MoveItem = 3


class DiagramScene(QGraphicsScene):
    itemInserted = pyqtSignal(DiagramItem)
    textInserted = pyqtSignal(DiagramTextItem)
    itemSelected = pyqtSignal(QGraphicsItem)


    def font(self):
        return self.myFont
    def textColor(self):
        return self.myTextColor
    def itemColor(self):
        return self.myItemColor
    def lineColor(self):
        return self.myLineColor

    def __init__(self, itemMenu, parent=None):
        super().__init__(parent=parent)
        self.myItemMenu = itemMenu
        self.myMode = Mode.MoveItem
        self.myItemType = DiagramType.Step
        self.line = QGraphicsLineItem()
        self.textItem = DiagramTextItem()
        self.myItemColor = QColor("white")
        self.myTextColor = QColor("black")
        self.myLineColor = QColor("black")
        self.myFont = QFont()


    def setLineColor(self, color):
        self.myLineColor = color
        if (self.isItemChange(Arrow.Type)):
            item = self.selectedItems()[0]
            item.setColor(self.myLineColor)
            self.update()


    def setTextColor(self, color):
        self.myTextColor = QColor(color)
        if (self.isItemChange(DiagramTextItem.Type)):
            item = self.selectedItems()[0]
            item.setDefaultTextColor(self.myTextColor)


    def setItemColor(self, color):
        self.myItemColor = QColor(color)
        if (self.isItemChange(DiagramItem.Type)):
            item = self.selectedItems()[0]
            item.setBrush(QBrush(self.myItemColor))


    def setFont(self, font):
        self.myFont = font
        if (self.isItemChange(DiagramTextItem.Type)):
            item = self.selectedItems()[0]
            #At this point the selection can change so the first selected item might not be a DiagramTextItem
            if (item):
                item.setFont(self.myFont)


    def setMode(self, mode):
        self.myMode = mode


    def setItemType(self, item_type):
        self.myItemType = item_type

    def editorLostFocus(self, item):
        cursor = item.textCursor()
        cursor.clearSelection()
        item.setTextCursor(cursor)

        if not item.toPlainText():
            self.removeItem(item)
            item.deleteLater()

    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() != Qt.LeftButton):
            return

        if self.myMode == Mode.InsertItem:
            item = DiagramItem(self.myItemType, self.myItemMenu)
            item.setBrush(self.myItemColor)
            self.addItem(item)
            item.setPos(mouseEvent.scenePos())
            self.itemInserted.emit(item)
        elif self.myMode == Mode.InsertLine:            
            self.line = QGraphicsLineItem(QLineF(mouseEvent.scenePos(),mouseEvent.scenePos()))
            self.line.setPen(QPen(self.myLineColor))
            self.addItem(self.line)
        elif self.myMode == Mode.InsertText:
            textItem = DiagramTextItem("Test")
            textItem.setFont(self.myFont)
            textItem.setTextInteractionFlags(Qt.TextEditorInteraction)
            textItem.setZValue(1000.0)
            textItem.lostFocus.connect(self.editorLostFocus)
            textItem.selectedChange.connect(self.itemSelected)
            self.addItem(textItem)
            textItem.setDefaultTextColor(self.myTextColor)
            textItem.setPos(mouseEvent.scenePos())
            self.textInserted.emit(textItem)

        super().mousePressEvent(mouseEvent)


    def mouseMoveEvent(self, mouseEvent):
        if (self.myMode == Mode.InsertLine and self.line is not None):
            newLine = QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
        elif (self.myMode == Mode.MoveItem):
            super().mouseMoveEvent(mouseEvent)


    def mouseReleaseEvent(self, mouseEvent):
        if (self.line is not None and self.myMode == Mode.InsertLine):
            startItems = self.items(self.line.line().p1())
            if (len(startItems)> 0 and startItems[0] == self.line):
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if (len(endItems)> 0 and endItems[0] == self.line):
                endItems.pop(0)

            self.removeItem(self.line)
            del(self.line)

            if ((len(startItems) > 0) and (len(endItems) > 0) and (startItems[0].Type == DiagramItem.Type) and (endItems[0].Type == DiagramItem.Type) and (startItems[0] != endItems[0])):
                startItem = startItems[0]
                endItem = endItems[0]
                arrow = Arrow(startItem, endItem, parent=None)
                arrow.setColor(self.myLineColor)
                startItem.addArrow(arrow)
                endItem.addArrow(arrow)
                arrow.setZValue(-1000.0)
                self.addItem(arrow)
                arrow.updatePosition()
         
        self.line = None
        super().mouseReleaseEvent(mouseEvent)


    def isItemChange(self, item_type):
        items = self.selectedItems()
        print('test')
        for item in items:
            if item.Type == item_type:
                return True
        return False
