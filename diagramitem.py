from enum import IntEnum
from PyQt5.QtCore import Qt, QSize, QRectF, QRect, QPointF
from PyQt5.QtGui import QKeySequence, QPixmap, QIcon, QFont, QIntValidator, QPainter, QPainterPath, QPolygonF, QPen
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsItem

class DiagramType(IntEnum):
    Step = 0
    Conditional = 1
    StartEnd = 2
    Io = 3
    
class DiagramItem(QGraphicsPolygonItem):
    Type = 15
  
    def __init__(self, diagramType, contextMenu, parent=None):
        super().__init__(parent=parent)
        self.myDiagramType = diagramType
        self.arrows = []
        self.myContextMenu = contextMenu

        self.path = QPainterPath()
        self.myPolygon = QPolygonF()
        if self.myDiagramType == DiagramType.StartEnd:
            path.moveTo(200, 50)
            path.arcTo(150, 0, 50, 50, 0, 90)
            path.arcTo(50, 0, 50, 50, 90, 90)
            path.arcTo(50, 50, 50, 50, 180, 90)
            path.arcTo(150, 50, 50, 50, 270, 90)
            path.lineTo(200, 25)
            self.myPolygon = path.toFillPolygon()
        elif self.myDiagramType == DiagramType.Conditional:
            self.myPolygon.append(QPointF(-100, 0))
            self.myPolygon.append(QPointF(0, 100))
            self.myPolygon.append(QPointF(100, 0))
            self.myPolygon.append(QPointF(0, -100))
            self.myPolygon.append(QPointF(-100, 0))
        elif self.myDiagramType == DiagramType.Step:
            self.myPolygon.append(QPointF(-100, -100))
            self.myPolygon.append(QPointF(100, -100))
            self.myPolygon.append(QPointF(100, 100))
            self.myPolygon.append(QPointF(-100, 100))
            self.myPolygon.append(QPointF(-100, -100))
        else:
            self.myPolygon.append(QPointF(-120, -80))
            self.myPolygon.append(QPointF(-70, 80))
            self.myPolygon.append(QPointF(120, 80))
            self.myPolygon.append(QPointF(70, -80))
            self.myPolygon.append(QPointF(-120, -80))

        self.setPolygon(self.myPolygon)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)


    def polygon(self):
        return self.myPolygon
        
    def image(self):
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)

        return pixmap
        
    # def type(self):
    #     return self.Type

    def diagramType(self):
        return self.myDiagramType

    def removeArrow(self, arrow):
        self.arrows.remove(arrow)


    def removeArrows(self):
        # need a copy here since removeArrow() will
        # modify the arrows container
        arrowsCopy = self.arrows
        for arrow in arrowsCopy:
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)
            del(arrow)


    def addArrow(self, arrow):
        self.arrows.append(arrow)
        
    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.myContextMenu.exec(event.screenPos())

    def itemChange(self, change, value):
        if (change == QGraphicsItem.ItemPositionChange):
            for arrow in self.arrows:
                arrow.updatePosition()

        return value
