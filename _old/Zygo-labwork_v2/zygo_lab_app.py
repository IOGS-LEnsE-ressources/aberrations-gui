# -*- coding: utf-8 -*-
"""*zygo_lab_app.py* file.

*zygo_lab_app* file that contains :class::ZygoLabApp

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
from lensepy import load_dictionary, translate, dictionary
import sys
from PyQt6.QtWidgets import (
    QWidget, QPushButton,
    QMainWindow, QApplication, QMessageBox)
from widgets.main_widget import MainWidget, load_menu
from process.zernike_coefficients import Zernike 

## Example for IDS Camera
from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.ids.camera_ids import CameraIds

## Image display and thread
from lensecam.camera_thread import CameraThread
from lensepy.pyqt6 import *
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
## Camera settings Widget for IDS
from widgets.camera import *
from widgets.images import *
from widgets.masks import *
from drivers.nidaq_piezo import *
## Modes
from modes.modes import *
from modes.camera import *


ZERNIKE_MAX = 36

def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)


def load_default_parameters(file_path: str) -> dict:
    """
    Load parameter from a CSV file.

    :return: Dict containing 'key_1': 'language_word_1'.

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '#', which will be ignored.

    The file should have the following format:
        # comment
        # comment
        key_1 ; language_word_1
        key_2 ; language_word_2
    """
    dictionary_loaded = {}
    if os.path.exists(file_path):
        # Read the CSV file, ignoring lines starting with '//'
        data = np.genfromtxt(file_path, delimiter=';',
                             dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the CSV file
        for key, value in data:
            dictionary_loaded[key.strip()] = value.strip()
        return dictionary_loaded
    else:
        print('File error')
        return {}

class MainWindow(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """

    def __init__(self):
        """
        Initialisation of the main Window.
        """
        super().__init__()
        load_default_dictionary('FR')
        # Read default parameters
        self.default_parameters = load_default_parameters('./config.txt')
        ## GUI structure
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        # Menu
        load_menu('./config/menu.txt', self.central_widget.main_menu)
        self.central_widget.main_signal.connect(self.main_action)

        # Global mode
        # -----------
        self.main_mode = None
        self.main_submode = None
        self.display_3D = True
        self.zoom_activated = False     # Camera is started in a large window
        self.zoom_window = QWidget()
        self.mask_created = False       # Almost one mask is created and selected
        self.acquisition_done = False   # Almost one acquisition is done and data are acquired
        self.acquisition_number = 0
        self.images_opened = False      # Almost a set of 5 images is opened or acquired
        self.wrapped_phase_done = False      # Phase from acquisition is wrapped
        self.unwrapped_phase_done = False    # Phase from acquisition is unwrapped
        self.masks_changed = False    # Check if masks changed

        # Data from camera
        # ----------------------------
        self.raw_image = None
        self.displayed_image = None
        self.image_bits_depth = 8

        # Data for process phase
        # ----------------------------
        self.images = Images()
        self.masks = Masks()
        self.wrapped_phase = None
        self.unwrapped_phase = None
        self.unwrapped_phase_to_correct = None
        self.cropped_mask_phase = None
        if 'Wedge Factor' in self.default_parameters:
            self.wedge_factor = float(self.default_parameters['Wedge Factor'])
        else:
            self.wedge_factor = -1
        self.pv_stats = []
        self.rms_stats = []
        self.analysis_completed = False

        # Data for default correction
        # ---------------------------
        self.corrected_phase = None
        self.coeff_counter = 0
        self.coeff_zernike_max = ZERNIKE_MAX
        self.zernike = Zernike(self.coeff_zernike_max)

        # Initialization of the camera
        # ----------------------------
        self.camera = CameraIds()
        self.camera_thread = CameraThread()
        self.camera_connected = self.camera.find_first_camera()
        if self.camera_connected:
            self.camera.init_camera()
            self.image_bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
            if 'Exposure Time' in self.default_parameters:
                self.camera.set_exposure(float(self.default_parameters['Exposure Time'])*1000)  # in us
            else:
                self.camera.set_exposure(10000) # in us
            if 'Black Level' in self.default_parameters:
                self.camera.set_black_level(float(self.default_parameters['Black Level']))
            else:
                self.camera.set_black_level(32)
            self.camera_thread.set_camera(self.camera)
            self.camera_thread.image_acquired.connect(self.thread_update_image)
            # Display image
            #self.camera_thread.start()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No Camera Connected")
            dlg.setText("No IDS Camera is connected to the computer...\n\nThe application will not start "
                        "correctly.\n\nYou will only access to a pre-established data set.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            # sys.exit(-1)

        # Initialization of the piezo
        # ---------------------------
        self.piezo_connected = False
        if 'Piezo Active' in self.default_parameters:
            if self.default_parameters['Piezo Active'] == '1':
                self.piezo = NIDaqPiezo()
                self.piezo_connected = self.piezo.get_piezo() is not None
                if 'Piezo Channel' in self.default_parameters:
                    self.piezo.set_channel(int(self.default_parameters['Piezo Channel']))
        # Update menu
        self.central_widget.update_menu()

    def reset_data(self):
        """Reset all the data when a new acquisition is done or new set of images is opened."""
        self.wrapped_phase = None
        self.wrapped_phase_done = False
        self.unwrapped_phase = None
        self.unwrapped_phase_to_correct = None
        self.unwrapped_phase_done = False
        self.cropped_mask_phase = None

        self.pv_stats = []
        self.rms_stats = []
        self.analysis_completed = False

        self.corrected_phase = None
        self.coeff_counter = 0
        self.zernike = Zernike(self.coeff_zernike_max)

    def main_action(self, event):
        """
        Action performed by an event in the main widget.
        :param event: Event that triggered the action.
        """
        if event == 'camera':
            pass

        elif event == 'zoom_camera':
            try:
                self.zoom_activated = True
                self.zoom_window = ZoomImagesWidget(self)
                self.zoom_window.show()
                self.zoom_window.slider_changed.connect(self.action_zoom_camera_changed)
                min_value, max_value = self.camera.get_exposure_range()
                if 'Max Expo Time' in self.default_parameters:
                    max_value = float(self.default_parameters['Max Expo Time'])*1000  # in us
                self.zoom_window.set_slider_range(min_value/1000, max_value/1000)
                expo_time = self.camera.get_exposure()/1000
                self.zoom_window.set_slider_value(expo_time)
                self.zoom_window.closeEvent = self.action_zoom_closed
            except Exception as e:
                print(e)

    def thread_update_image(self, image_array):
        """Actions performed if a camera thread is started."""
        if self.main_mode is None or self.main_mode == 'camera' or self.main_mode == 'piezo':
            if image_array is not None:
                if self.image_bits_depth > 8:
                    self.raw_image = image_array.view(np.uint16)
                    self.displayed_image = self.raw_image >> (self.image_bits_depth-8)
                    self.displayed_image = self.displayed_image.astype(np.uint8)
                    self.displayed_image = self.displayed_image.squeeze()
                else:
                    self.raw_image = image_array.view(np.uint8)
                    self.displayed_image = self.raw_image.squeeze()
            if self.zoom_activated:
                self.zoom_window.zoom_window.set_image_from_array(self.displayed_image)
            else:
                self.central_widget.top_left_widget.set_image_from_array(self.displayed_image)

    def action_zoom_camera_changed(self):
        self.camera.set_exposure(self.zoom_window.get_exposure() * 1000)
        self.central_widget.options_widget.update_parameters(auto_min_max=True)

    def action_zoom_closed(self, event):
        self.zoom_activated = False
        self.zoom_window.deleteLater()
        self.central_widget.submenu_widget.set_button_enabled(2, True)
        event.accept()

    def resizeEvent(self, event):
        """
        Action performed when the main window is resized.
        :param event: Object that triggered the event.
        """
        if self.camera_thread.running:
            self.central_widget.update_size()
        elif self.images_opened and self.main_mode != 'aberrations':
            self.central_widget.update_size()

    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.camera_thread.running:
                self.camera_thread.stop()
            if self.camera_connected:
                self.camera.stop_acquisition()
                self.camera.disconnect()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())