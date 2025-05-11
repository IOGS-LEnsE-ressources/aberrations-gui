# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *
if __name__ == '__main__':
    from combobox_bloc import ComboBoxBloc
else:
    from widgets.combobox_bloc import ComboBoxBloc

# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30  # px

# %% Widget
class OptionsMenuWidget(QWidget):
    signal_language_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__(parent=None)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_options_menu = QLabel('Options')
        self.setStyleSheet(styleH1)
        
        # Language Selector
        # ------------------------------
        self.list_languages = ['English', 'Français', '中文']
        self.combobox_language_selection = ComboBoxBloc(translate('label_language_selector'), self.list_languages)
        self.combobox_language_selection.currentIndexChanged.connect(self.combobox_language_selection_changed)

        # Unit Selector
        # ------------------------------
        self.list_unit = ['mm', 'λ']
        self.combobox_unit_selection = ComboBoxBloc(translate('label_unit_selector'), self.list_unit)
        
        # Add widgets to the layout
        # -------------------------
        self.layout.addWidget(self.label_title_options_menu)
        #self.layout.addWidget(self.combobox_language_selection)
        #self.layout.addWidget(self.combobox_unit_selection)

        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def combobox_language_selection_changed(self, index):
        language_selected = self.list_languages[index-1]
        print(f"Signal emitted with language selected: {language_selected}")
        self.signal_language_updated.emit(language_selected)
    

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from ids_peak import ids_peak

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_options_menu_widget"))
            self.setGeometry(300, 300, 800, 200)

            self.central_widget = OptionsMenuWidget()
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
