import sys
from PySide6 import QtWidgets
from gui import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(1280, 800)
    window.show()
    sys.exit(app.exec())
