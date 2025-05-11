import sys
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

table_style = f"background-color: {BLACK}; color: {BLUE_IOGS}; font-size: 15px;"


class TableFromNumpy(QTableWidget):
    def __init__(self, arr):
        super().__init__()
        self.array = arr
        self.layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)
        self.setLayout(self.layout)
        self.update_table(arr)  # Initial population of the table

    def update_table(self, arr):
        self.array = arr
        nb_lines, nb_cols = arr.shape

        # Set the number of rows and columns
        self.table_widget.setRowCount(nb_lines)
        self.table_widget.setColumnCount(nb_cols)

        # Fill the table with items
        for i in range(nb_lines):
            for j in range(nb_cols):
                item = QTableWidgetItem(str(self.array[i, j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(i, j, item)

        # Disable scroll bars
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Disable row and column headers
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)

        # Set column and row resize mode to stretch
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table_widget.setStyleSheet(table_style)

    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    arr = np.array([['', f"{translate('button_circle_mask')}", 'B', 'C'], [
                   'PV', 1.5, 2.2, 3.9], ['RMS', 4.2, 5.7, 6.5]])

    app = QApplication(sys.argv)
    mainWidget = TableFromNumpy(arr=np.zeros((5, 6)))

    # Example of updating the table with new data
    new_arr = np.array([['', f"{translate('button_circle_mask')}", 'X', 'Y'],
                        ['PV', 1.1, 2.3, 3.4],
                        ['RMS', 4.5, 5.6, 6.7]])
    mainWidget.update_table(new_arr)
    mainWidget.show()

    sys.exit(app.exec())