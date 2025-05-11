# -*- coding: utf-8 -*-
"""*acquisition.py* file.

This file contains graphical elements to manage acquisition of images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QTableWidget,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import *
from lensepy.images.conversion import *
from lensepy.pyqt6 import *
from matplotlib import pyplot as plt
from widgets.analysis import *


class AcquisitionOptionsWidget(QWidget):
    """Acquisition Options."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        # Title
        self.label_acquisition_title = QLabel(translate("label_acquisition_title"))
        self.label_acquisition_title.setStyleSheet(styleH1)
        self.label_acquisition_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Table of images
        self.images_table = AcquisitionTableWidget(self)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_acquisition_title, 0, 0)
        self.layout.addWidget(self.images_table, 1, 0)
        self.layout.addStretch()

    def add_image(self, new_image: np.ndarray, voltage: float = 0.0):
        """Add a new image in the list."""
        print('\tAdding Image...')
        self.images_table.add_image(new_image, voltage)


class AcquisitionTableWidget(QTableWidget):

    def __init__(self, parent=None):
        """Default constructor.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.images_list = []
        self.voltage_list = []
        self.show_button_list = []
        self.setColumnCount(3)  # 3 columns
        self.setHorizontalHeaderLabels(["Image", "Voltage", "Show"])
        for i in range(5):
            self.insertRow(i)
            widget = QWidget()
            widget.setStyleSheet('background-color: red;')
            self.setCellWidget(i, 0, widget)
            self.setCellWidget(i, 1, widget)
        self.verticalHeader().setVisible(False)
        self.update_display()

    def add_image(self, new_image: np.ndarray, voltage: float):
        """Add a new image to the list.
        :param new_image: Image as an array, to add.
        """
        self.images_list.append(new_image)
        self.voltage_list.append(voltage)
        self.update_display()

    def erase_all(self):
        """Delete all the rows and reconstruct the first line (header)."""
        self.voltage_list = []
        self.show_button_list = []
        self.clearContents()

    def update_display(self):
        """Update Masks options widget display."""
        number_of_rows = len(self.images_list)
        print(f'Number of images = {number_of_rows}')
        for row in range(number_of_rows):
            # Create label for mask type (third column)
            label = QLabel(f'Image {row+1}')
            label_widget = qobject_to_widget(label)
            #self.setCellWidget(row, 1, wid)
        # Resize columns to fit content
        #self.resizeColumnsToContents()

    def button_show_mask_clicked(self):
        """Action performed when a show button is clicked.."""
        button = self.sender()
        index = -1
        for i in range(len(self.show_button_list)):
            if button == self.show_button_list[i]:
                index = i
                # Show the ith mask on the image
                self.parent.parent.action_masks_visualization(str(index+1))


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = AcquisitionOptionsWidget(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())