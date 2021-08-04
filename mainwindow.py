import PyQt5
from PyQt5.QtCore import Qt, QSize, QRectF, QRect
from PyQt5.QtGui import QKeySequence, QPixmap, QIcon, QFont, QIntValidator, QPainter, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QButtonGroup, QGridLayout, QToolButton, QLabel, QWidget, QSizePolicy, QToolBox, QFontComboBox, QComboBox, QMenu, QGraphicsView, QHBoxLayout
from diagramitem import DiagramType, DiagramItem
from diagramscene import DiagramScene, Mode
from diagramtextitem import DiagramTextItem
from arrow import Arrow

InsertTextButton = 10

class MainWindow(QMainWindow):
    
    
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        
        self.itemMenu = None

        self.createActions()
        self.createToolBox()
        self.createMenus()

        self.scene = DiagramScene(self.itemMenu, self)
        self.scene.setSceneRect(QRectF(0, 0, 500, 500))
        self.scene.itemInserted.connect(self.itemInserted)
        self.scene.textInserted.connect(self.textInserted)
        self.scene.itemSelected.connect(self.itemSelected)
        
        self.createToolbars()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.toolBox)
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("Diagramscene")
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.handleFontChange()


    def backgroundButtonGroupClicked(self, button):
        buttons = self.backgroundButtonGroup.buttons()
        for myButton in buttons:
            if (myButton != button):
                button.setChecked(False)
        text = button.text()
        if (text == "Blue Grid"):
            self.scene.setBackgroundBrush(QBrush(QPixmap("./images/background1.png")))
        elif (text == "White Grid"):
            self.scene.setBackgroundBrush(QBrush(QPixmap("./images/background2.png")))
        elif (text == "Gray Grid"):
            self.scene.setBackgroundBrush(QBrush(QPixmap("./images/background3.png")))
        else:
            self.scene.setBackgroundBrush(QBrush(QPixmap("./images/background4.png")))

        self.scene.update()
        self.view.update()


    def buttonGroupClicked(self, button):
        buttons = self.buttonGroup.buttons()
        for myButton in buttons:
            if (myButton != button):
                button.setChecked(False)

        button_id = self.buttonGroup.id(button)
        if (button_id == InsertTextButton):
            self.scene.setMode(Mode.InsertText)
        else:
            self.scene.setItemType(button_id)
            self.scene.setMode(Mode.InsertItem)


    def deleteItem(self):
        selectedItems = self.scene.selectedItems()
        for item in selectedItems:
            if (item.Type == Arrow.Type):
                item.startItem().removeArrow(item)
                item.endItem().removeArrow(item)
                self.scene.removeItem(item)
                del(item)


        selectedItems = self.scene.selectedItems()
        for item in selectedItems:
            if (item.type() == DiagramItem.Type):
                item.removeArrows()
            self.scene.removeItem(item)
            del(item)


    def pointerGroupClicked(self):
        self.scene.setMode(self.pointerTypeGroup.checkedId())

    def bringToFront(self):
        if not self.scene.selectedItems():
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if (item.zValue() >= zValue and type(item) == DiagramItem):
                zValue = item.zValue() + 0.1
        
        selectedItem.setZValue(zValue)


    def sendToBack(self):
        if not self.scene.selectedItems():
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if (item.zValue() <= zValue and type(item) == DiagramItem):
                zValue = item.zValue() - 0.1
        
        selectedItem.setZValue(zValue)


    def itemInserted(self, item):
        self.pointerTypeGroup.button(Mode.MoveItem).setChecked(True)
        self.scene.setMode(self.pointerTypeGroup.checkedId())
        self.buttonGroup.button(int(item.diagramType())).setChecked(False)


    def textInserted(self, item):
        self.buttonGroup.button(InsertTextButton).setChecked(False)
        self.scene.setMode(self.pointerTypeGroup.checkedId())


    def currentFontChanged(self, font):
        self.handleFontChange()


    def fontSizeChanged(self, size):
        self.handleFontChange()


    def sceneScaleChanged(self, scale):
        newScale = float(scale.replace("%", "")) / 100.0
        oldMatrix = self.view.transform()
        self.view.resetTransform()
        self.view.translate(oldMatrix.dx(), oldMatrix.dy())
        self.view.scale(newScale, newScale)


    def textColorChanged(self):
        textAction = self.sender()
        self.fontColorToolButton.setIcon(self.createColorToolButtonIcon("./images/textpointer.png", QColor(textAction.data())))
        self.textButtonTriggered()


    def itemColorChanged(self):
        self.fillAction = self.sender()
        self.fillColorToolButton.setIcon(self.createColorToolButtonIcon("./images/floodfill.png", QColor(self.fillAction.data())))
        self.fillButtonTriggered()


    def lineColorChanged(self):
        self.lineAction = self.sender()
        self.lineColorToolButton.setIcon(self.createColorToolButtonIcon("./images/linecolor.png", QColor(self.lineAction.data())))
        self.lineButtonTriggered()
        

    def textButtonTriggered(self):
        self.scene.setTextColor(self.textAction.data())


    def fillButtonTriggered(self):
        self.scene.setItemColor(self.fillAction.data())


    def lineButtonTriggered(self):
        self.scene.setLineColor(self.lineAction.data())


    def handleFontChange(self):
        font = self.fontCombo.currentFont()
        font.setPointSize(int(self.fontSizeCombo.currentText()))
        if self.boldAction.isChecked():
            font.setWeight(QFont.Bold)
        else:
            font.setWeight(QFont.Normal)
        font.setItalic(self.italicAction.isChecked())
        font.setUnderline(self.underlineAction.isChecked())

        self.scene.setFont(font)
        
        
    def itemSelected(self, item):
        textItem = DiagramTextItem(item)

        font = textItem.font()
        self.fontCombo.setCurrentFont(font)
        self.fontSizeCombo.setEditText(str(font.pointSize()))
        self.boldAction.setChecked(font.weight() == QFont.Bold)
        self.italicAction.setChecked(font.italic())
        self.underlineAction.setChecked(font.underline())
    
    
    def about(self):
        QMessageBox.about(self, "About Diagram Scene",
                        "The <b>Diagram Scene</b> example shows "
                            "use of the graphics framework.")
    

    def createToolBox(self):
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked.connect(self.buttonGroupClicked)
        self.layout = QGridLayout()
        self.layout.addWidget(self.createCellWidget("Conditional", DiagramType.Conditional), 0, 0)
        self.layout.addWidget(self.createCellWidget("Process", DiagramType.Step), 0, 1)
        self.layout.addWidget(self.createCellWidget("Input/Output", DiagramType.Io), 1, 0)
        

        self.textButton = QToolButton()
        self.textButton.setCheckable(True)
        self.buttonGroup.addButton(self.textButton, InsertTextButton)
        self.textButton.setIcon(QIcon(QPixmap("./images/textpointer.png")))
        self.textButton.setIconSize(QSize(50, 50))
        self.textLayout = QGridLayout()
        self.textLayout.addWidget(self.textButton, 0, 0, Qt.AlignHCenter)
        self.textLayout.addWidget(QLabel("Text"), 1, 0, Qt.AlignCenter)
        self.textWidget = QWidget()
        self.textWidget.setLayout(self.textLayout)
        self.layout.addWidget(self.textWidget, 1, 1)

        self.layout.setRowStretch(3, 10)
        self.layout.setColumnStretch(2, 10)

        self.itemWidget = QWidget()
        self.itemWidget.setLayout(self.layout)

        self.backgroundButtonGroup = QButtonGroup(self)
        self.backgroundButtonGroup.buttonClicked.connect(self.backgroundButtonGroupClicked)

        self.backgroundLayout = QGridLayout()
        self.backgroundLayout.addWidget(self.createBackgroundCellWidget("Blue Grid", "./images/background1.png"), 0, 0)
        self.backgroundLayout.addWidget(self.createBackgroundCellWidget("White Grid", "./images/background2.png"), 0, 1)
        self.backgroundLayout.addWidget(self.createBackgroundCellWidget("Gray Grid", "./images/background3.png"), 1, 0)
        self.backgroundLayout.addWidget(self.createBackgroundCellWidget("No Grid", "./images/background4.png"), 1, 1)

        self.backgroundLayout.setRowStretch(2, 10)
        self.backgroundLayout.setColumnStretch(2, 10)

        self.backgroundWidget = QWidget()
        self.backgroundWidget.setLayout(self.backgroundLayout)

        self.toolBox = QToolBox()
        self.toolBox.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(self.itemWidget.sizeHint().width())
        self.toolBox.addItem(self.itemWidget, "Basic Flowchart Shapes")
        self.toolBox.addItem(self.backgroundWidget, "Backgrounds")


    def createActions(self):
        self.toFrontAction = QAction(QIcon("./images/bringtofront.png"),
                                    "Bring to &Front", self)
        self.toFrontAction.setShortcut("Ctrl+F")
        self.toFrontAction.setStatusTip("Bring item to front")
        self.toFrontAction.triggered.connect(self.bringToFront)

        self.sendBackAction = QAction(QIcon("./images/sendtoback.png"), "Send to &Back", self)
        self.sendBackAction.setShortcut("Ctrl+T")
        self.sendBackAction.setStatusTip("Send item to back")
        self.sendBackAction.triggered.connect(self.sendToBack)

        self.deleteAction = QAction(QIcon("./images/delete.png"), "&Delete", self)
        self.deleteAction.setShortcut("Delete")
        self.deleteAction.setStatusTip("Delete item from diagram")
        self.deleteAction.triggered.connect(self.deleteItem)

        self.exitAction = QAction("E&xit", self)
        self.exitAction.setShortcuts(QKeySequence.Quit)
        self.exitAction.setStatusTip("Quit Scenediagram example")
        self.exitAction.triggered.connect(self.close)

        self.boldAction = QAction("Bold", self)
        self.boldAction.setCheckable(True)
        pixmap = QPixmap("./images/bold.png")
        self.boldAction.setIcon(QIcon(pixmap))
        self.boldAction.setShortcut("Ctrl+B")
        self.boldAction.triggered.connect(self.handleFontChange)

        self.italicAction = QAction(QIcon("./images/italic.png"), "Italic", self)
        self.italicAction.setCheckable(True)
        self.italicAction.setShortcut("Ctrl+I")
        self.italicAction.triggered.connect(self.handleFontChange)

        self.underlineAction = QAction(QIcon("./images/underline.png"), "Underline", self)
        self.underlineAction.setCheckable(True)
        self.underlineAction.setShortcut("Ctrl+U")
        self.underlineAction.triggered.connect(self.handleFontChange)

        self.aboutAction = QAction("A&bout", self)
        self.aboutAction.setShortcut("F1")
        self.aboutAction.triggered.connect(self.about)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.exitAction)

        self.itemMenu = self.menuBar().addMenu("&Item")
        self.itemMenu.addAction(self.deleteAction)
        self.itemMenu.addSeparator()
        self.itemMenu.addAction(self.toFrontAction)
        self.itemMenu.addAction(self.sendBackAction)

        self.aboutMenu = self.menuBar().addMenu("&Help")
        self.aboutMenu.addAction(self.aboutAction)


    def createToolbars(self):
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.deleteAction)
        self.editToolBar.addAction(self.toFrontAction)
        self.editToolBar.addAction(self.sendBackAction)

        self.fontCombo = QFontComboBox()
        self.fontCombo.currentFontChanged.connect(self.currentFontChanged)

        self.fontSizeCombo = QComboBox()
        self.fontSizeCombo.setEditable(True)
        for i in range(8, 30, 2):
            self.fontSizeCombo.addItem(str(i))
        validator = QIntValidator(2, 64, self)
        self.fontSizeCombo.setValidator(validator)
        self.fontSizeCombo.currentTextChanged.connect(self.fontSizeChanged)

        self.fontColorToolButton = QToolButton()
        self.fontColorToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.fontColorToolButton.setMenu(self.createColorMenu(self.textColorChanged, Qt.black))
        self.textAction = self.fontColorToolButton.menu().defaultAction()
        self.fontColorToolButton.setIcon(self.createColorToolButtonIcon("./images/textpointer.png", Qt.black))
        self.fontColorToolButton.setAutoFillBackground(True)
        self.fontColorToolButton.clicked.connect(self.textButtonTriggered)

        self.fillColorToolButton = QToolButton()
        self.fillColorToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.fillColorToolButton.setMenu(self.createColorMenu(self.itemColorChanged, Qt.white))
        self.fillAction = self.fillColorToolButton.menu().defaultAction()
        self.fillColorToolButton.setIcon(self.createColorToolButtonIcon("./images/floodfill.png", Qt.white))
        self.fillColorToolButton.clicked.connect(self.fillButtonTriggered)

        self.lineColorToolButton = QToolButton()
        self.lineColorToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.lineColorToolButton.setMenu(self.createColorMenu(self.lineColorChanged, Qt.black))
        self.lineAction = self.lineColorToolButton.menu().defaultAction()
        self.lineColorToolButton.setIcon(self.createColorToolButtonIcon("./images/linecolor.png", Qt.black))
        self.lineColorToolButton.clicked.connect(self.lineButtonTriggered)

        self.textToolBar = self.addToolBar("Font")
        self.textToolBar.addWidget(self.fontCombo)
        self.textToolBar.addWidget(self.fontSizeCombo)
        self.textToolBar.addAction(self.boldAction)
        self.textToolBar.addAction(self.italicAction)
        self.textToolBar.addAction(self.underlineAction)

        self.colorToolBar = self.addToolBar("Color")
        self.colorToolBar.addWidget(self.fontColorToolButton)
        self.colorToolBar.addWidget(self.fillColorToolButton)
        self.colorToolBar.addWidget(self.lineColorToolButton)

        self.pointerButton = QToolButton()
        self.pointerButton.setCheckable(True)
        self.pointerButton.setChecked(True)
        self.pointerButton.setIcon(QIcon("./images/pointer.png"))
        self.linePointerButton = QToolButton()
        self.linePointerButton.setCheckable(True)
        self.linePointerButton.setIcon(QIcon("./images/linepointer.png"))

        self.pointerTypeGroup = QButtonGroup(self)
        self.pointerTypeGroup.addButton(self.pointerButton, int(Mode.MoveItem))
        self.pointerTypeGroup.addButton(self.linePointerButton, int(Mode.InsertLine))
        self.pointerTypeGroup.buttonClicked.connect(self.pointerGroupClicked)

        self.sceneScaleCombo = QComboBox()
        scales = []
        scales.append("50%")
        scales.append("75%")
        scales.append("100%")
        scales.append("125%")
        scales.append("150%")
        self.sceneScaleCombo.addItems(scales)
        self.sceneScaleCombo.setCurrentIndex(2)
        self.sceneScaleCombo.currentTextChanged.connect(self.sceneScaleChanged)

        self.pointerToolbar = self.addToolBar("Pointer type")
        self.pointerToolbar.addWidget(self.pointerButton)
        self.pointerToolbar.addWidget(self.linePointerButton)
        self.pointerToolbar.addWidget(self.sceneScaleCombo)


    def createBackgroundCellWidget(self, text, image):
        button = QToolButton()
        button.setText(text)
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.backgroundButtonGroup.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget


    def createCellWidget(self, text, item_type):
        item = DiagramItem(item_type, self.itemMenu)
        icon = QIcon(item.image())

        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, int(item_type))

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget
    

    def createColorMenu(self, slot, defaultColor):
        colors = []
        colors.append(QColor("black"))
        colors.append(QColor("white"))
        colors.append(QColor("red"))
        colors.append(QColor("blue"))
        colors.append(QColor("yellow"))
        names = []
        names.append("black")
        names.append("white")
        names.append("red")
        names.append("blue")
        names.append("yellow")

        colorMenu = QMenu(self)
        for i in range(len(colors)):
            action = QAction(names[i], self)
            action.setData(colors[i])
            action.setIcon(self.createColorIcon(colors[i]))
            action.triggered.connect(slot)
            colorMenu.addAction(action)
            if (colors[i] == defaultColor):
                colorMenu.setDefaultAction(action)
        
        return colorMenu
    

    def createColorToolButtonIcon(self, imageFile, color):
        pixmap = QPixmap(50, 80)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        image = QPixmap(imageFile)
        # Draw icon centred horizontally on button.
        target = QRect(4, 0, 42, 43)
        source = QRect(0, 0, 42, 43)
        painter.fillRect(QRect(0, 60, 50, 80), color)
        painter.drawPixmap(target, image, source)
        painter.end()

        return QIcon(pixmap)


    def createColorIcon(self, color):
        pixmap = QPixmap(20, 20)
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.fillRect(QRect(0, 0, 20, 20), color)
        painter.end()

        return QIcon(pixmap)

