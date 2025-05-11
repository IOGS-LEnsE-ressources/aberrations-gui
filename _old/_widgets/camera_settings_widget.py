# -*- coding: utf-8 -*-
"""*camera_settings_widget.py* file.

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
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap

if __name__ == '__main__':
    from slider_bloc import SliderBloc
    from imshow_pyqtgraph import TwoImageWidget
else:
    from widgets.slider_bloc import SliderBloc
    from widgets.imshow_pyqtgraph import TwoImageWidget
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds

from process.initialization_parameters import *

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 30  # px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Widget
class CameraSettingsWidget(QWidget):
    zoom_activated = pyqtSignal(bool)

    def __init__(self, camera: CameraIds):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.camera = camera

        # Title
        # -----
        self.label_title_camera_settings = QLabel("Paramètres de la caméra")
        self.label_title_camera_settings.setStyleSheet(styleH1)

        """# Camera ID
        # ---------
        self.subwidget_camera_id = QWidget()
        self.sublayout_camera_id = QHBoxLayout()

        self.label_title_camera_id = QLabel("Camera ID")
        self.label_title_camera_id.setStyleSheet(styleH2)

        self.label_value_camera_id = QLabel(translate("label_value_camera_id"))
        self.label_value_camera_id.setStyleSheet(styleH3)

        self.sublayout_camera_id.addWidget(self.label_title_camera_id)
        self.sublayout_camera_id.addStretch()
        self.sublayout_camera_id.addWidget(self.label_value_camera_id)
        self.sublayout_camera_id.setContentsMargins(0, 0, 0, 0)

        self.subwidget_camera_id.setLayout(self.sublayout_camera_id)"""

        # Settings
        # --------
        self.slider_exposure_time = SliderBloc(name="Temps d'exposition", unit='ms', min_value=0, max_value=10)
        self.slider_exposure_time.slider_changed.connect(self.slider_exposure_time_changing)

        self.slider_black_level = SliderBloc(name="Black level", unit='', min_value=1, max_value=100)
        self.slider_black_level.slider_changed.connect(self.slider_black_level_changing)

        # Big cam
        # -------
        self.button_big_cam = QPushButton('Caméra en plein écran')
        self.button_big_cam.setFixedHeight(BUTTON_HEIGHT)
        self.button_big_cam.setStyleSheet(unactived_button)
        self.button_big_cam.clicked.connect(self.button_big_cam_isClicked)

        # Set default settings
        # --------------------
        self.button_set_default_settings = QPushButton('Sauver en tant que valeurs par défaut')
        self.button_set_default_settings.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_set_default_settings.setStyleSheet(unactived_button)
        self.button_set_default_settings.clicked.connect(self.button_set_default_settings_isClicked)
        
        # Default settings backup
        # -----------------------
        self.button_default_settings_backup = QPushButton('Rétablir les valeurs par défaut')
        self.button_default_settings_backup.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_default_settings_backup.setStyleSheet(unactived_button)
        self.button_default_settings_backup.clicked.connect(self.button_default_settings_backup_isClicked)

        self.layout.addWidget(self.label_title_camera_settings)
        """self.layout.addWidget(self.subwidget_camera_id)"""
        self.layout.addWidget(self.slider_exposure_time)
        self.layout.addWidget(self.slider_black_level)
        self.layout.addWidget(self.button_big_cam)
        self.layout.addStretch()
        self.layout.addWidget(self.button_set_default_settings)
        self.layout.addWidget(self.button_default_settings_backup)
        self.setLayout(self.layout)

    def slider_exposure_time_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            exposure_time_value = self.slider_exposure_time.get_value() * 1000
            self.camera.set_exposure(exposure_time_value)

    def slider_black_level_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            self.camera.set_black_level(int(self.slider_black_level.get_value()))

    def update_parameters(self, auto_min_max: bool = False) -> None:
        """Update displayed parameters values, from the camera.
        """
        if auto_min_max:
            exposure_min, exposure_max = self.camera.get_exposure_range()
            self.slider_exposure_time.set_min_max_slider_values(exposure_min // 1000, exposure_max // 1000)

            black_min, black_max = self.camera.get_black_level_range()
            self.slider_black_level.set_min_max_slider_values(black_min, black_max)
        
        exposure_time = self.camera.get_exposure()
        self.slider_exposure_time.set_value(exposure_time / 1000)

        black_level = self.camera.get_black_level()
        self.slider_black_level.set_value(int(black_level))

    def button_big_cam_isClicked(self):
        self.button_big_cam.setStyleSheet(actived_button)
        self.zoom_activated.emit(True)
        self.button_big_cam.setStyleSheet(unactived_button)

    def button_set_default_settings_isClicked(self):
        exposure = 1e-3 * self.camera.get_exposure()
        black_level = self.camera.get_black_level()

        modify_parameter_value('config.txt', 'Exposure time', str(exposure))
        modify_parameter_value('config.txt', 'Black level', str(int(black_level)))
        
        self.update_parameters()

        msg_box = QMessageBox()
        msg_box.setStyleSheet(styleH3)
        msg_box.information(self, "Information", "Ces valeurs sont maintenant les valeurs par défaut.")
    
    def button_default_settings_backup_isClicked(self):
        default_settings_dict = read_default_parameters('config.txt')

        default_exposure = float(default_settings_dict['Exposure time']) # ms
        default_exposure *= 1000 # µs
        self.camera.set_exposure(default_exposure) # µs

        default_black_level = int(default_settings_dict['Black level'])
        self.camera.set_black_level(default_black_level)

        self.update_parameters()

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

            self.setWindowTitle(translate("window_title_camera_settings"))
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = CameraSettingsWidget(camera=None)
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
