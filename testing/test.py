import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MyWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.button = QtWidgets.QPushButton("Click to Display Text")
        self.button2 = QtWidgets.QPushButton("Clear")
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setPlaceholderText("OKOK")
        self.text_edit = QtWidgets.QTextEdit()
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.line_edit,0, 0, 3, 3)
        self.layout.addWidget(self.button, 0, 1, 3, 3)
        self.layout.addWidget(self.button2, 0, 4, 3, 4)
        self.layout.addWidget(self.text_edit)

        self.button.clicked.connect(self.magic)
        self.button2.clicked.connect(self.clear)
        
    @QtCore.Slot()
    def magic(self):
        self.text_edit.append(self.line_edit.text())

    @QtCore.Slot()
    def clear(self):
        self.text_edit.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(400, 600)
    widget.show()

    sys.exit(app.exec_())