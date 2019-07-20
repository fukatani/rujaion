from PyQt5 import QtCore, Qt, QtGui
from PyQt5 import QtWidgets


class ResultTableModel(QtWidgets.QTableWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.resize(350, 800)
        self.row_size = 15
        self.column_size = 3
        self.setRowCount(self.row_size)
        self.setColumnCount(self.column_size)
        self.setHorizontalHeaderLabels(["Name", "Value", "Type"])
        self.setVerticalHeaderLabels([""] * self.row_size)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)

        for i in range(self.row_size):
            for j in range(1, self.column_size):
                item = self.cell()
                # execute the line below to every item you need locked
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j, item)

    def __contextMenu(self):
        menu = QtWidgets.QMenu()
        self._addCustomMenuItems(menu)
        menu.exec_(QtGui.QCursor.pos())

    def _addCustomMenuItems(self, menu: QtWidgets.QMenu):
        menu.addSeparator()
        menu.addAction(u"Clear", self.clear)

    def cell(self, var: str = "") -> Qt.QTableWidgetItem:
        item = Qt.QTableWidgetItem()
        item.setText(var.replace("true", "T").replace("false", "F"))
        return item

    def set_cell(self, i: int, j: int, var: str = ""):
        self.setItem(i, j, self.cell(var))

    def name_iter(self):
        for i in range(self.row_size):
            if self.item(i, 0) is not None:
                yield i, self.item(i, 0).text()

    def clear(self):
        for i in range(self.row_size):
            self.set_cell(i, 0, var="")

    def add_var(self, var: str):
        for i in range(self.row_size):
            if self.item(i, 0) is None:
                self.set_cell(i, 0, var)
                return

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        pass
