# -*- coding: utf-8 -*-
"""*lineedit_block.py* file.

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


# %% Widget
class LineEditBloc(QWidget):
    def __init__(self, title: str, txt:str='') -> None: 
        super().__init__(parent=None)
        
        self.layout = QHBoxLayout()

        self.label = QLabel(translate(title))
        self.label.setStyleSheet(styleH2)

        self.lineedit = QLineEdit(txt)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def setText(self, text:str):
        self.lineedit.setText(text)

    def text(self):
        return self.lineedit.text()
    
    def clear(self):
        self.lineedit.clear()

    def selectAll(self):
        self.lineedit.selectAll()

    def setPlaceholderText(self, text:str):
        self.lineedit.setPlaceholderText(text)

    def setMaxLength(self, length:int):
        self.lineedit.setMaxLength(length)

    def setReadOnly(self, readonly: bool):
        self.lineedit(readonly)

    def editing_finished_signal(self):
        return self.lineedit.editingFinished


        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_line_edit_block"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = LineEditBloc(title='Title', txt='HEY !')
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
