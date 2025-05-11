# -*- coding: utf-8 -*-
"""*title_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout,
    QLabel,
    QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from lensepy import load_dictionary, translate
from lensepy.css import *

# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px

# %% Widget
class TitleWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.setStyleSheet("background-color: white;")  # Set background color for the entire widget
        self.title = "Contrôle interférométrique & Analyseur de front d'onde ZYGO"
        self.subtitle = "Interface développée par Dorian Mendes (Promo 2026) et Julien Villemejane (PRAG)"

        self.layout = QVBoxLayout()

        self.subwidget = QWidget()
        self.sublayout = QGridLayout()

        self.label_title = QLabel(self.title)
        self.label_title.setStyleSheet(styleH1)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_subtitle = QLabel(self.subtitle)
        self.label_subtitle.setStyleSheet(styleH2)
        self.label_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lense_logo = QLabel('Logo')
        self.lense_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QPixmap("./assets/IOGS-LEnsE-logo_small.jpg")
        self.lense_logo.setPixmap(logo)

        self.sublayout.addWidget(self.label_title, 0, 0)
        self.sublayout.addWidget(self.label_subtitle, 1, 0)
        self.sublayout.setColumnStretch(0, 10)
        self.sublayout.setColumnStretch(1, 5)
        self.sublayout.addWidget(self.lense_logo, 0, 1, 2, 1)

        self.subwidget.setLayout(self.sublayout)
        self.layout.addWidget(self.subwidget)
        self.setLayout(self.layout)

    def set_title(self, value):
        self.title = value
        self.label_title.setText(self.title)

    def set_subtitle(self, value):
        self.subtitle = value
        self.label_subtitle.setText(self.subtitle)

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(300, 300, 800, 200)

            self.central_widget = TitleWidget()
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
