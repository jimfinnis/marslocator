from PySide2 import QtWidgets
from PySide2.QtGui import QColor

import uiloader


class PointEditDialog(QtWidgets.QDialog):
    def __init__(self, name, r, g, b):
        super().__init__()
        self.name = name
        self.col = r, g, b
        uiloader.loadUi('pointedit.ui', self)
        self.setWindowTitle("Edit Point")
        self.colButton.setStyleSheet(f"background-color: rgb({r},{g},{b})")
        self.nameEdit.setText(name)
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(self.rejected)
        self.colButton.clicked.connect(self.selectColour)
        self.nameEdit.editingFinished.connect(self.nameChanged)

    def nameChanged(self):
        self.name = self.nameEdit.text()

    def selectColour(self):
        r, g, b = self.col
        col = QColor(r, g, b)
        col = QtWidgets.QColorDialog.getColor(col, None)
        if col.isValid():
            r, g, b = col.red(), col.green(), col.blue()
            self.col = r, g, b
            self.colButton.setStyleSheet(f"background-color: rgb({r},{g},{b})")

    def accepted(self):
        self.name = self.nameEdit.text()
        self.accept()

    def rejected(self):
        self.reject()
