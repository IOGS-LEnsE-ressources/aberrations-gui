# -*- coding: utf-8 -*-
"""*piezo.py* file.

This file contains graphical elements to manage NI DAQ controlled piezo.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : nov/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import *
from lensepy.images.conversion import *


class PiezoOptionsWidget(QWidget):
    """Acquisition Options."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.label_piezo_title = QLabel(translate("label_piezo_title"))
        self.label_piezo_title.setStyleSheet(styleH1)
        self.label_piezo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_piezo_title, 0, 0)


class PiezoMoveOptionsWidget(QWidget):
    """Acquisition Options."""

    voltage_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Title
        self.label_piezo_title = QLabel(translate("label_piezo_move_title"))
        self.label_piezo_title.setStyleSheet(styleH1)
        self.label_piezo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Slider to move
        self.voltage_slider = SliderBloc(translate('piezo_voltage_slider'), 'V', 0, 5)
        self.voltage_slider.set_value(1)
        self.voltage_slider.set_enabled(self.parent.parent.piezo_connected)
        if self.parent.parent.piezo_connected:
            self.parent.parent.piezo.write_dac(1)
        self.voltage_slider.slider_changed.connect(self.action_voltage_changed)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_piezo_title, 0, 0)
        self.layout.addWidget(self.voltage_slider,1, 0)

    def get_voltage(self) -> float:
        """Return the voltage from the slider.
        :return: Voltage as float (in V).
        """
        return float(self.voltage_slider.get_value())

    def action_voltage_changed(self, event):
        """Action performed when the voltage slider changed."""
        self.voltage_changed.emit('voltage')


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = PiezoMoveOptionsWidget(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())