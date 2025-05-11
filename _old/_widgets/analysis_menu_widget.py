# -*- coding: utf-8 -*-
"""*analysis_menu_widget.py* file.

*analysis_menu_widget* file that contains :class::AnalysisMenuWidget

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : https://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-PolyAberrations.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

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

if __name__ == '__main__':
    from lineedit_bloc import LineEditBloc
else:
    from widgets.lineedit_bloc import LineEditBloc

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Widget
class AnalysisMenuWidget(QWidget):
    # Signals definition
    # ------------------
    analysis_selected = pyqtSignal(str)
    focal_changed = pyqtSignal(str)
    f_number_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setStyleSheet("background-color: white;")

        self.parent = parent

        # Widgets
        # -------
        self.layout = QVBoxLayout()

        self.subwidget = QWidget()
        self.sublayout = QVBoxLayout()
        
        self.label_title_main_menu = QLabel('Menu')
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineedit_focal = LineEditBloc(title='Focale (mm)')
        self.lineedit_focal.editing_finished_signal().connect(self.emit_focal_changed)

        self.lineedit_f_number = LineEditBloc(title="f-number")
        self.lineedit_f_number.editing_finished_signal().connect(self.emit_f_number_changed)
        
        self.button_zernike_menu = QPushButton("Zernike / Seidel")
        self.button_zernike_menu.setStyleSheet(unactived_button)
        self.button_zernike_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_zernike_menu.clicked.connect(self.button_analysis_menu_isClicked)

        self.button_psf_menu = QPushButton("PSF")
        self.button_psf_menu.setStyleSheet(unactived_button)
        self.button_psf_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_psf_menu.clicked.connect(self.button_analysis_menu_isClicked)

        self.button_mtf_menu = QPushButton("MTF")
        self.button_mtf_menu.setStyleSheet(unactived_button)
        self.button_mtf_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_mtf_menu.clicked.connect(self.button_analysis_menu_isClicked)

        self.button_spot_diagram_menu = QPushButton("Spot diagram")
        self.button_spot_diagram_menu.setStyleSheet(unactived_button)
        self.button_spot_diagram_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_spot_diagram_menu.clicked.connect(self.button_analysis_menu_isClicked)

        self.sublayout.addWidget(self.label_title_main_menu)
        self.sublayout.addWidget(self.lineedit_focal)
        self.sublayout.addWidget(self.lineedit_f_number)
        self.sublayout.addWidget(self.button_zernike_menu)
        self.sublayout.addWidget(self.button_psf_menu)
        self.sublayout.addWidget(self.button_mtf_menu)
        self.sublayout.addWidget(self.button_spot_diagram_menu)
        self.sublayout.addStretch()
        self.subwidget.setLayout(self.sublayout)

        self.layout.addWidget(self.subwidget)
        self.setLayout(self.layout)

        if parent is not None:
            self.lineedit_focal.setText(str(self.parent.focal))
            self.lineedit_f_number.setText(str(self.parent.f_number))
        
    def emit_focal_changed(self):
        self.focal_changed.emit(self.lineedit_focal.text())
        
    def emit_f_number_changed(self):
        self.f_number_changed.emit(self.lineedit_f_number.text())
        
    def unactive_buttons(self):
        """ Switches all buttons to inactive style """
        self.button_zernike_menu.setStyleSheet(unactived_button)
        self.button_psf_menu.setStyleSheet(unactived_button)
        self.button_mtf_menu.setStyleSheet(unactived_button)
        self.button_spot_diagram_menu.setStyleSheet(unactived_button)
        
    def button_analysis_menu_isClicked(self):
        sender = self.sender()

        # Change style
        self.unactive_buttons()
        sender.setStyleSheet(actived_button)
        if sender == self.button_zernike_menu:
            # Action
            self.analysis_selected.emit('zernike')

        elif sender == self.button_psf_menu:
            # Action
            self.analysis_selected.emit('psf')

        elif sender == self.button_mtf_menu:
            # Action
            self.analysis_selected.emit('mtf')

        elif sender == self.button_spot_diagram_menu:
            # Action
            self.analysis_selected.emit('spot_diagram')

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

            self.central_widget = AnalysisMenuWidget()
            self.setCentralWidget(self.central_widget)

            # Connect signals
            self.central_widget.focal_changed.connect(self.on_focal_changed)
            self.central_widget.f_number_changed.connect(self.on_f_number_changed)

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

        def on_focal_changed(self, text):
            print(f"Focale changed: {text}")

        def on_f_number_changed(self, text):
            print(f"f-number changed: {text}")

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
