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
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Widget
class MainMenuWidget(QWidget):
    # Signals definition
    # ------------------
    signal_menu_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__(parent=None)
        self.setStyleSheet("background-color: white;")

        # Widgets
        # -------
        self.layout = QVBoxLayout()

        self.subwidget = QWidget()
        self.sublayout = QVBoxLayout()
        
        self.label_title_main_menu = QLabel('Menu')
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button_camera_settings_main_menu = QPushButton("Réglages caméra")
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_camera_settings_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_camera_settings_main_menu.clicked.connect(self.button_camera_settings_main_menu_isClicked)
        
        self.button_masks_main_menu = QPushButton("Masques")
        self.button_masks_main_menu.setStyleSheet(unactived_button)
        self.button_masks_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_masks_main_menu.clicked.connect(self.button_masks_main_menu_isClicked)
        
        self.button_acquisition_main_menu = QPushButton("Acquisition")
        self.button_acquisition_main_menu.setStyleSheet(unactived_button)
        self.button_acquisition_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_acquisition_main_menu.clicked.connect(self.button_acquisition_main_menu_isClicked)
        
        self.button_analyzes_main_menu = QPushButton("Analyses")
        self.button_analyzes_main_menu.setStyleSheet(unactived_button)
        self.button_analyzes_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_analyzes_main_menu.clicked.connect(self.button_analyzes_main_menu_isClicked)
        
        self.button_help_main_menu = QPushButton("Aide")
        self.button_help_main_menu.setStyleSheet(unactived_button)
        self.button_help_main_menu.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_help_main_menu.clicked.connect(self.button_help_main_menu_isClicked)
        
        self.button_options_main_menu = QPushButton("Options")
        self.button_options_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_options_main_menu.clicked.connect(self.button_options_main_menu_isClicked)
        
        self.sublayout.addWidget(self.label_title_main_menu)
        self.sublayout.addWidget(self.button_camera_settings_main_menu)
        self.sublayout.addWidget(self.button_masks_main_menu)
        self.sublayout.addWidget(self.button_acquisition_main_menu)
        self.sublayout.addWidget(self.button_analyzes_main_menu)
        self.sublayout.addStretch()
        self.sublayout.addWidget(self.button_help_main_menu)
        self.sublayout.addWidget(self.button_options_main_menu)
        self.subwidget.setLayout(self.sublayout)

        self.layout.addWidget(self.subwidget)
        self.setLayout(self.layout)
        
    def unactive_buttons(self):
        """ Switches all buttons to inactive style """
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_masks_main_menu.setStyleSheet(unactived_button)
        self.button_acquisition_main_menu.setStyleSheet(unactived_button)
        self.button_analyzes_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setStyleSheet(unactived_button)        
        
    def button_camera_settings_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_camera_settings_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.signal_menu_selected.emit('camera_settings_main_menu')
        
    def button_masks_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_masks_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.signal_menu_selected.emit('masks_main_menu')
        
    def button_acquisition_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_acquisition_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.signal_menu_selected.emit('acquisition_main_menu')
        
    def button_analyzes_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_analyzes_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.signal_menu_selected.emit('analyzes_main_menu')
        
    def button_help_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_help_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.signal_menu_selected.emit('help')
    
    def button_options_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_options_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.signal_menu_selected.emit('options_main_menu')

    def reset_menu(self):
        # Change style
        self.unactive_buttons()

        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(300, 300, 200, 600)

            self.central_widget = MainMenuWidget()
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
