'''This class handles the display of the treatment of unwrapped phase images. That is, displaying the PSF, the MTF,
the encircled energy and near-focal point energy distribution. Is components use external windows to display their contents,
each of which is composed of smaller display units (...DisplayWidget)
-------------------------------
|  Display#1   |  Display#2   |
|              |              |
|--------------|--------------|
|  Display#3   |  Display#4   |
|              |              |
-------------------------------
'''

import numpy as np

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QCheckBox,
    QGridLayout, QVBoxLayout, QHBoxLayout, QGridLayout
)
from views.bar_graph_view import BarGraphView
from views.images_display_view import ImagesDisplayView

class PSFView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.

    def get_image(self):
        pass

class PSFDisplayWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.title = QLabel("")
        self.image_display = ImagesDisplayView()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.image)

    def set_image(self, image):
        self.image_display.set_image_from_array(image)

    def set_title(self, title : str):
        self.title.setText(title)