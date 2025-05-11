# -*- coding: utf-8 -*-
"""*combobox_block.py* file.

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
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; color:{BLUE_IOGS}; font-weight: normal"

# Translation
dictionary = {}

# %% Widget
class ComboBoxBloc(QWidget):
    selection_changed = pyqtSignal(str)

    def __init__(self, title: str, list_options: list) -> None: 
        super().__init__(parent=None)
        
        self.layout = QHBoxLayout()

        self.label = QLabel(translate(title))
        self.label.setStyleSheet(styleH2)

        self.combobox = QComboBox()
        self.combobox.addItem('===== Sélectionner une option =====')
        self.combobox.setCurrentIndex(0)
        self.combobox.addItems(list_options)
        self.combobox.setStyleSheet(styleH3)

        self.currentIndexChanged = self.combobox.currentIndexChanged

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.combobox.currentTextChanged.connect(self.emit_selection_changed)

    def emit_selection_changed(self, text):
        self.selection_changed.emit(text)  # Émettre le signal avec le texte sélectionné
        print('Option changée')

    def update_options(self, list_options):
        self.combobox.clear()
        self.combobox.addItem('===== Sélectionner une option =====')
        self.combobox.setCurrentIndex(0)
        self.combobox.addItems(list_options)

        
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

            self.setWindowTitle(translate("window_title_combo_box_block"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = ComboBoxBloc(title='Title', list_options=['opt1', 'opt2'])
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
