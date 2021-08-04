import PyQt5
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

def main(args=[], **kwargs):
    app = QApplication(args, **kwargs)
    mainWindow = MainWindow()
    mainWindow.setGeometry(100, 100, 800, 500)
    mainWindow.show()

    return app.exec()
    

if __name__ == "__main__":
    main()

