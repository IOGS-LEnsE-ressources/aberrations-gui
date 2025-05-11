# -*- coding: utf-8 -*-
"""*main_menu_widget.py* file.

...

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QSlider, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# Translation
dictionary = {}

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Is number
def is_number(value, min_val=0, max_val=0):
    """
    Returns true if the value is a number between min and max.

    Parameters
    ----------
    value : float
        Number to test.
    min_val : float
        Minimum of the interval to test.
    max_val : float
        Maximum of the interval to test.

    Returns
    -------
    True if number is between min and max.
    """
    min_ok = False
    max_ok = False
    value2 = str(value).replace('.', '', 1)
    value2 = value2.replace('e', '', 1)
    value2 = value2.replace('-', '', 1)
    if value2.isdigit():
        value = float(value)
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        if (min_val != '') and (int(value) >= min_val):
            min_ok = True
        if (max_val != '') and (int(value) <= max_val):
            max_ok = True
        if min_ok != max_ok:
            return False
        else:
            return True
    else:
        return False

# %% Widget
class SliderBloc(QWidget):
    """

    """

    slider_changed = pyqtSignal(str)

    def __init__(self, name:str, unit:str, min_value:float, max_value:float) -> None:
        """

        """
        super().__init__(parent=None)
        self.min_value = min_value
        self.max_value = max_value
        self.value = round(self.min_value + (self.max_value - self.min_value)/3, 2)
        self.ratio = 100
        self.unit = unit
        
        self.layout = QVBoxLayout()
        
        # First line: name, value and unit
        # --------------------------------
        self.subwidget_texts = QWidget()
        self.sublayout_texts = QHBoxLayout()
        
        self.label_name = QLabel(translate(name)+':')
        self.label_name.setStyleSheet(styleH2)
        
        self.lineedit_value = QLineEdit()
        self.lineedit_value.setText(str(self.value))
        self.lineedit_value.editingFinished.connect(self.input_changed)
        
        self.label_unit = QLabel(unit)
        self.label_unit.setStyleSheet(styleH3)
        
        self.sublayout_texts.addWidget(self.label_name)
        self.sublayout_texts.addWidget(self.lineedit_value)
        self.sublayout_texts.addWidget(self.label_unit)
        self.sublayout_texts.setContentsMargins(0, 0, 0, 0)
        
        self.subwidget_texts.setLayout(self.sublayout_texts)
        
        # Second line: slider and min/max
        # -------------------------------
        self.subwidget_slider = QWidget()
        self.sublayout_slider = QHBoxLayout()
        
        self.label_min_value = QLabel(str(self.min_value)+' '+self.unit)
        self.label_min_value.setStyleSheet(styleH3)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_value*self.ratio))
        self.slider.setMaximum(int(self.max_value*self.ratio))
        self.slider.valueChanged.connect(self.slider_position_changed)
        
        self.label_max_value = QLabel(str(self.max_value)+' '+self.unit)
        self.label_max_value.setStyleSheet(styleH3)
        
        self.sublayout_slider.addWidget(self.label_min_value)
        self.sublayout_slider.addWidget(self.slider)
        self.sublayout_slider.addWidget(self.label_max_value)
        self.sublayout_slider.setContentsMargins(0, 0, 0, 0)
        
        self.subwidget_slider.setLayout(self.sublayout_slider)
        
        # All combined
        # ------------
        self.layout.addWidget(self.subwidget_texts)
        self.layout.addWidget(self.subwidget_slider)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
    def slider_position_changed(self):
        self.value = self.slider.value()/self.ratio
        self.slider_changed.emit(f'slider')
        self.update_block()
    
    def input_changed(self):
        self.value = max(self.min_value, min(self.max_value,float(self.lineedit_value.text())))
        self.update_block()
    
    def update_block(self):
        self.lineedit_value.setText(str(self.value))
        self.slider.setValue(int(self.value*self.ratio))

    def get_value(self):
        """Return the value of the block."""
        return self.value

    def set_value(self, value):
        """Set the value of the block."""
        self.value = value
        self.update_block()

    def set_min_max_slider_values(self, min_value, max_value):
        """Set the mininmum and the maximum values of the slider.

        """
        self.min_value = min_value
        self.slider.setMinimum(int(self.min_value * self.ratio))
        self.max_value = max_value
        self.slider.setMaximum(int(self.max_value * self.ratio))
        self.label_min_value.setText(str(self.min_value)+' '+self.unit)
        self.label_max_value.setText(str(self.max_value)+' '+self.unit)

    def set_enabled(self, value):
        """Set the widget enabled if value is True."""
        self.slider.setEnabled(value)
        self.lineedit_value.setEnabled(value)
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            #dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_slider_block"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = SliderBloc(name='name', unit='unit', min_value=4.2, max_value=7.8)
            self.setCentralWidget(self.central_widget)

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


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
