from PyQt5 import QtCore, Qt
from PyQt5 import QtWidgets


# TODO: width


class ResultTableModel(QtWidgets.QTableWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.setFixedWidth(320)
        self.row_size = 15
        self.column_size = 3
        self.setRowCount(self.row_size)
        self.setColumnCount(self.column_size)
        self.setHorizontalHeaderLabels(["Name", "Type", "Value"])
        self.setVerticalHeaderLabels([""] * self.row_size)

        for i in range(self.row_size):
            for j in range(self.column_size):
                if j == 0:
                    continue
                item = self.cell()
                # execute the line below to every item you need locked
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j, item)

    def cell(self, var=""):
        item = Qt.QTableWidgetItem()
        item.setText(var)
        return item

    def set_cell(self, i, j, var=""):
        self.setItem(i, j, self.cell(var))

    def name_iter(self):
        for i in range(self.row_size):
            if self.item(i, 0) is not None:
                yield i, self.item(i, 0).text()

    def keyPressEvent(self, event):
        pass
