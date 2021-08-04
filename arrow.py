from diagramitem import DiagramItem
from PyQt5.QtCore import Qt, QLineF, QRectF, QSizeF, QPointF
from PyQt5.QtGui import QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsItem
from math import atan2, sin, cos, pi

class Arrow(QGraphicsLineItem):
    Type = 4

    def __init__(self, startItem, endItem, parent):
        super().__init__(parent)
        self.myStartItem = startItem
        self.myEndItem = endItem
        self.myColor = Qt.black
        self.arrowHead = QPolygonF()
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setPen(QPen(self.myColor, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    # def type(self):
    #     return self.Type

    def setColor(self, color):
        self.myColor = color

    def startItem(self):
        return self.myStartItem

    def endItem(self):
        return self.myEndItem
        
    def updatePosition(self):
        self.line = QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
        self.setLine(self.line)

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0

        return QRectF(self.line.p1(), QSizeF(self.line.p2().x() - self.line.p1().x(), self.line.p2().y() - self.line.p1().y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super().shape()
        path.addPolygon(self.arrowHead)
        return path


    def paint(self, painter, qstyleoptiongraphicsitem, qwidget):

        self.myPen = QPen()
        self.myPen.setColor(self.myColor)
        self.arrowSize = 20
        painter.setPen(self.myPen)
        painter.setBrush(self.myColor)

        # Draw line
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            centerLine = QLineF(self.myEndItem.pos(), self.myStartItem.pos())
            self.setLine(centerLine)
        else:
            centerLine = QLineF(self.myStartItem.pos(), self.myEndItem.pos())
            endPolygon = self.myEndItem.polygon()
            p1 = endPolygon.first() + self.myEndItem.pos()
            intersectPoint_1 = QPointF()
            for i in range(1, endPolygon.count()+1):
                p2 = endPolygon.at(i) + self.myEndItem.pos()
                polyLine = QLineF(p1, p2)
                intersectionType = polyLine.intersect(centerLine, intersectPoint_1)
                if (intersectionType ==  QLineF.BoundedIntersection):
                    break
                p1 = p2

            centerLine = QLineF(intersectPoint_1, self.myStartItem.pos())
            self.setLine(centerLine)

            startPolygon = self.myStartItem.polygon()
            p1 = startPolygon.first() + self.myStartItem.pos()
            intersectPoint_2 = QPointF()
            for i in range(1, startPolygon.count()+1):
                p2 = startPolygon.at(i) + self.myStartItem.pos()
                polyLine = QLineF(p1, p2)
                intersectionType = polyLine.intersect(centerLine, intersectPoint_2)
                if (intersectionType ==  QLineF.BoundedIntersection):
                    break
                p1 = p2

            centerLine = QLineF(intersectPoint_1, intersectPoint_2)
            self.setLine(centerLine)
            
        self.line = centerLine

        angle = atan2(-self.line.dy(), self.line.dx())

        arrowP1 = self.line.p1() + QPointF(sin(angle + pi / 3) * self.arrowSize, cos(angle + pi / 3) * self.arrowSize)
        arrowP2 = self.line.p1() + QPointF(sin(angle + pi - pi / 3) * self.arrowSize, cos(angle + pi - pi / 3) * self.arrowSize)

        self.arrowHead.clear()
        self.arrowHead << self.line.p1() << arrowP1 << arrowP2

        painter.drawLine(self.line)
        painter.drawPolygon(self.arrowHead)
        if (self.isSelected()):
            painter.setPen(QPen(self.myColor, 1, Qt.DashLine))
            myLine = self.line
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0,-8.0)
            painter.drawLine(myLine)

