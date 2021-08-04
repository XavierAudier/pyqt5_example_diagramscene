from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QLineF


class DiagramTextItem(QGraphicsTextItem):

    Type = 3


    lostFocus = pyqtSignal(QObject)
    selectedChange = pyqtSignal(QGraphicsItem)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)


    # def type(self):
    #     return self.Type


    def itemChange(self, change, value):  
        if (change == QGraphicsItem.ItemSelectedHasChanged):
            self.selectedChange.emit(self)
        return value


    def focusOutEvent(self, event):
        print('test2')
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.lostFocus.emit(self)
        super().focusOutEvent(event)


    def mouseDoubleClickEvent(self, event):
        print('test3')
        if (self.textInteractionFlags() == Qt.NoTextInteraction):
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
        super().mouseDoubleClickEvent(event)

