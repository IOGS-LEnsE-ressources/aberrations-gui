# -*- coding: utf-8 -*-
"""*camera.py* file.

This file contains graphical elements to display images in a widget from a camera.
Image is coming from a file (JPG, PNG...) or an industrial camera (IDS, Basler...).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import *
from lensepy.images.conversion import *
from lensecam.basler.camera_basler_widget import CameraBaslerListWidget
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsListWidget
from lensecam.ids.camera_ids import CameraIds, get_bits_per_pixel
from lensecam.ids.camera_list import CameraList as CameraIdsList
from lensecam.basler.camera_list import CameraList as CameraBaslerList
from matplotlib import pyplot as plt
from widgets.images import *

cam_list_brands = {
    'Basler': CameraBaslerList,
    'IDS': CameraIdsList,
}
cam_list_widget_brands = {
    'Select...': 'None',
    'Basler': CameraBaslerListWidget,
    'IDS': CameraIdsListWidget,
}
cam_from_brands = {
    'Basler': CameraBasler,
    'IDS': CameraIds,
}


class CameraChoice(QWidget):
    """Camera Choice."""

    brand_selected = pyqtSignal(str)
    camera_selected = pyqtSignal(dict)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QGridLayout()

        self.label_camera_choice_title = QLabel(translate("label_camera_choice_title"))
        self.label_camera_choice_title.setStyleSheet(styleH1)
        self.label_camera_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.brand_choice_label = QLabel(translate('brand_choice_label'))
        self.brand_choice_label.setStyleSheet(styleH2)
        self.brand_choice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_choice_list = QComboBox()
        self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
        self.brand_select_button = QPushButton(translate('brand_select_button'))
        self.brand_select_button.clicked.connect(self.action_brand_select_button)

        self.selected_label = QLabel()
        self.brand_return_button = QPushButton(translate('brand_return_button'))
        self.brand_return_button.clicked.connect(self.action_brand_return_button)

        self.brand_refresh_button = QPushButton(translate('brand_refresh_button'))
        self.brand_refresh_button.clicked.connect(self.action_brand_return_button)

        self.cam_choice_widget = QWidget()
        self.brand_choice = None
        self.selected_camera = None

        self.layout.addWidget(self.label_camera_choice_title, 0, 0)
        self.layout.addWidget(self.brand_choice_label, 1, 0)
        self.layout.addWidget(self.brand_refresh_button, 2, 0)
        self.layout.addWidget(self.brand_choice_list, 3, 0) # 3,0 choice_list
        self.layout.addWidget(self.brand_select_button, 4, 0) # 4,0 brand_select_button
        # Add a blank space at the end (spacer)
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(self.spacer, 5, 0)

        self.brand_select_button.setEnabled(False)
        self.setLayout(self.layout)
        self.init_brand_choice_list()
        self.action_brand_return_button(None)

    def init_brand_choice_list(self):
        """Action ..."""
        # create list from dict cam_list_widget_brands
        self.brand_choice_list.clear()
        for item, (brand, camera_widget) in enumerate(cam_list_widget_brands.items()):
            if brand != 'Select...':
                number_of_cameras = cam_list_brands[brand]().get_nb_of_cam()
                if number_of_cameras != 0:
                    text_value = f'{brand} ({number_of_cameras})'
                    self.brand_choice_list.addItem(text_value)
            else:
                self.brand_choice_list.addItem(brand)
        self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
        self.brand_select_button.setEnabled(False)
        self.brand_select_button.clicked.connect(self.action_brand_select_button)

    def action_brand_select_button(self, event) -> None:
        """Action performed when the brand_select button is clicked."""
        self.clear_layout(5, 0)
        self.clear_layout(4, 0)
        self.clear_layout(3, 0)
        self.brand_choice = self.brand_choice_list.currentText()
        self.brand_choice = self.brand_choice.split(' (')[0]
        self.selected_label = QLabel()
        self.brand_return_button = QPushButton(translate('brand_return_button'))
        self.brand_return_button.clicked.connect(self.action_brand_return_button)
        self.selected_label.setText(self.brand_choice)
        self.layout.addWidget(self.selected_label, 3, 0) # 3,0 choice_list
        self.layout.addWidget(self.brand_return_button, 4, 0) # 4,0 brand_select_button
        self.brand_refresh_button.setEnabled(False)
        self.layout.addItem(self.spacer, 5, 0)
        self.brand_selected.emit('brand:'+self.brand_choice)
        self.cam_choice_widget = cam_list_widget_brands[self.brand_choice]()
        self.cam_choice_widget.connected.connect(self.action_camera_selected)
        self.layout.addWidget(self.cam_choice_widget, 5, 0)

    def action_camera_selected(self, event):
        selected_camera = self.cam_choice_widget.get_selected_camera_index()
        self.brand_return_button.setEnabled(False)
        dict_brand = {'brand': self.brand_choice, 'cam_dev': selected_camera}
        self.camera_selected.emit(dict_brand)

    def action_brand_return_button(self, event) -> None:
        """Action performed when the brand_return button is clicked."""
        try:
            self.clear_layout(6, 0)
            self.clear_layout(5, 0)
            self.clear_layout(4, 0)
            self.clear_layout(3, 0)
            # create list from dict cam_list_widget_brands
            self.brand_choice_list = QComboBox()
            self.brand_choice_list.clear()
            for item, (brand, camera_widget) in enumerate(cam_list_widget_brands.items()):
                if brand != 'Select...':
                    number_of_cameras = cam_list_brands[brand]().get_nb_of_cam()
                    if number_of_cameras != 0:
                        text_value = f'{brand} ({number_of_cameras})'
                        self.brand_choice_list.addItem(text_value)
                else:
                    self.brand_choice_list.addItem(brand)
            self.layout.addWidget(self.brand_choice_list)
            self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
            self.brand_select_button = QPushButton(translate('brand_select_button'))
            self.brand_select_button.clicked.connect(self.action_brand_select_button)
            self.brand_select_button.setEnabled(False)
            self.layout.addWidget(self.brand_choice_list, 3, 0)
            self.layout.addWidget(self.brand_select_button, 4, 0)
            self.layout.addItem(self.spacer, 5, 0)
            self.brand_refresh_button.setEnabled(True)
            self.brand_selected.emit('nobrand:')
        except Exception as e:
            print(f'Exception - action_brand_return {e}')

    def action_brand_choice_list(self, event) -> None:
        """Action performed when the combo 'Choice List' item is changed."""
        try:
            selected_item = self.brand_choice_list.currentText()
            selected_item = selected_item.split(' (')[0]
            if cam_list_widget_brands[selected_item] == 'None':
                self.brand_select_button.setEnabled(False)
            else:
                self.brand_select_button.setEnabled(True)
        except Exception as e:
            print(f'Exception - list {e}')

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)


class CameraSettingsWidget(QWidget):

    settings_changed = pyqtSignal(str)

    def __init__(self, parent = None, camera: CameraIds or CameraBasler = None):
        """

        """
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.camera = camera

        # Title
        # -----
        self.label_title_camera_settings = QLabel(translate('title_camera_settings'))
        self.label_title_camera_settings.setStyleSheet(styleH1)

        # Camera ID
        # ---------
        self.subwidget_camera_id = QWidget()
        self.sublayout_camera_id = QHBoxLayout()

        self.label_title_camera_id = QLabel(translate("label_title_camera_id"))
        self.label_title_camera_id.setStyleSheet(styleH2)

        self.label_value_camera_id = QLabel(translate("label_value_camera_id"))
        self.label_value_camera_id.setStyleSheet(styleH3)

        self.sublayout_camera_id.addWidget(self.label_title_camera_id)
        self.sublayout_camera_id.addStretch()
        self.sublayout_camera_id.addWidget(self.label_value_camera_id)
        self.sublayout_camera_id.setContentsMargins(0, 0, 0, 0)

        self.subwidget_camera_id.setLayout(self.sublayout_camera_id)

        # Settings
        # --------
        self.max_expo_time_value = -1
        self.slider_exposure_time = SliderBloc(name='name_slider_exposure_time', unit='ms', min_value=0, max_value=10)
        self.slider_exposure_time.slider_changed.connect(self.slider_exposure_time_changing)

        self.slider_black_level = SliderBloc(name='name_slider_black_level', unit='gray',
                                              min_value=0, max_value=255, integer=True)
        self.slider_black_level.slider_changed.connect(self.slider_black_level_changing)

        self.layout.addWidget(self.label_title_camera_settings)
        self.layout.addWidget(self.subwidget_camera_id)
        self.layout.addWidget(self.slider_exposure_time)
        self.layout.addWidget(self.slider_black_level)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def slider_exposure_time_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            exposure_time_value = self.slider_exposure_time.get_value() * 1000
            self.camera.set_exposure(exposure_time_value)
            self.settings_changed.emit('camera_settings_changed')
        else:
            print('No Camera Connected')

    def slider_black_level_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            black_level_value = self.slider_black_level.get_value()
            self.camera.set_black_level((black_level_value//4) * 4)
            self.settings_changed.emit('changed')
        else:
            print('No Camera Connected')

    def set_maximum_exposure_time(self, value):
        """Set the maximum value of the exposure time.
        :param value: Value of the maximum exposure time (in ms).
        """
        self.max_expo_time_value = value

    def update_parameters(self, auto_min_max: bool = False) -> None:
        """Update displayed parameters values, from the camera.
        :param auto_min_max: if True, adjust the minimum and maximum value of the slider to
        camera range.
        """
        if auto_min_max:
            exposure_min, exposure_max = self.camera.get_exposure_range()
            if self.max_expo_time_value > 0:
                exposure_max = self.max_expo_time_value*1000
            if exposure_max > 400000:
                exposure_max = 400000
            if exposure_min < 100:
                exposure_min = 100
            self.slider_exposure_time.set_min_max_slider_values(exposure_min // 1000, exposure_max // 1000)
            bl_min, bl_max = self.camera.get_black_level_range()
            self.slider_black_level.set_min_max_slider_values(bl_min, bl_max)
        exposure_time = self.camera.get_exposure()
        self.slider_exposure_time.set_value(exposure_time / 1000)
        bl = self.camera.get_black_level()
        self.slider_black_level.set_value(bl)


class CameraInfosWidget(QWidget):
    def __init__(self, parent = None):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.first_display = True

        # Title
        # -----
        self.label_title_camera_settings = QLabel(translate('title_camera_infos_view'))
        self.label_title_camera_settings.setStyleSheet(styleH1)

        # Camera Name
        # ---------
        self.subwidget_camera_name = QWidget()
        self.sublayout_camera_name = QHBoxLayout()
        self.label_title_camera_name = QLabel(translate("label_title_camera_name"))
        self.label_title_camera_name.setStyleSheet(styleH2)
        self.label_value_camera_name = QLabel()
        self.label_value_camera_name.setStyleSheet(styleH3)
        self.sublayout_camera_name.addWidget(self.label_title_camera_name)
        self.sublayout_camera_name.addStretch()
        self.sublayout_camera_name.addWidget(self.label_value_camera_name)
        self.sublayout_camera_name.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_name.setLayout(self.sublayout_camera_name)

        # Camera ID
        # ---------
        self.subwidget_camera_id = QWidget()
        self.sublayout_camera_id = QHBoxLayout()
        self.label_title_camera_id = QLabel(translate("label_title_camera_id"))
        self.label_title_camera_id.setStyleSheet(styleH2)
        self.label_value_camera_id = QLabel()
        self.label_value_camera_id.setStyleSheet(styleH3)
        self.sublayout_camera_id.addWidget(self.label_title_camera_id)
        self.sublayout_camera_id.addStretch()
        self.sublayout_camera_id.addWidget(self.label_value_camera_id)
        self.sublayout_camera_id.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_id.setLayout(self.sublayout_camera_id)

        # Camera Size
        # ---------
        self.subwidget_camera_size = QWidget()
        self.sublayout_camera_size = QHBoxLayout()
        self.label_title_camera_size = QLabel(translate("label_title_camera_size"))
        self.label_title_camera_size.setStyleSheet(styleH2)
        self.label_value_camera_size = QLabel()
        self.label_value_camera_size.setStyleSheet(styleH3)
        self.sublayout_camera_size.addWidget(self.label_title_camera_size)
        self.sublayout_camera_size.addStretch()
        self.sublayout_camera_size.addWidget(self.label_value_camera_size)
        self.sublayout_camera_size.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_size.setLayout(self.sublayout_camera_size)

        # Camera Main Parameters / Exposure Time
        self.subwidget_camera_expo = QWidget()
        self.sublayout_camera_expo = QHBoxLayout()
        self.label_title_camera_exposure = QLabel(translate("label_title_camera_exposure"))
        self.label_title_camera_exposure.setStyleSheet(styleH2)
        self.label_value_camera_exposure = QLabel()
        self.label_value_camera_exposure.setStyleSheet(styleH3)
        self.sublayout_camera_expo.addWidget(self.label_title_camera_exposure)
        self.sublayout_camera_expo.addStretch()
        self.sublayout_camera_expo.addWidget(self.label_value_camera_exposure)
        self.sublayout_camera_expo.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_expo.setLayout(self.sublayout_camera_expo)
        # Camera Main Parameters / FPS
        self.subwidget_camera_fps = QWidget()
        self.sublayout_camera_fps = QHBoxLayout()
        self.label_title_camera_fps = QLabel(translate("label_title_camera_fps"))
        self.label_title_camera_fps.setStyleSheet(styleH2)
        self.label_value_camera_fps = QLabel()
        self.label_value_camera_fps.setStyleSheet(styleH3)
        self.sublayout_camera_fps.addWidget(self.label_title_camera_fps)
        self.sublayout_camera_fps.addStretch()
        self.sublayout_camera_fps.addWidget(self.label_value_camera_fps)
        self.sublayout_camera_fps.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_fps.setLayout(self.sublayout_camera_fps)

        # Add elements
        self.layout.addWidget(self.label_title_camera_settings)
        self.layout.addWidget(self.subwidget_camera_name)
        self.layout.addWidget(self.subwidget_camera_id)
        self.layout.addWidget(self.subwidget_camera_size)
        self.layout.addStretch()
        self.layout.addWidget(self.subwidget_camera_expo)
        self.layout.addWidget(self.subwidget_camera_fps)
        self.setLayout(self.layout)
        self.update_parameters()

    def update_parameters(self):
        if self.parent.parent.camera is not None:
            serial_no, camera_name = self.parent.parent.camera.get_cam_info()
            self.label_value_camera_name.setText(camera_name)
            self.label_value_camera_id.setText(serial_no)
            max_width, max_height = self.parent.parent.camera.get_sensor_size()
            self.label_value_camera_size.setText(f'W={max_width} x H={max_height} px')
            fps = self.parent.parent.camera.get_frame_rate()
            self.label_value_camera_fps.setText(f'{fps} Frame/s (fps)')
            expo = self.parent.parent.camera.get_exposure() / 1000
            self.label_value_camera_exposure.setText(f'{expo} ms')
        else:
            self.label_value_camera_name.setText('No Camera')
            self.label_value_camera_id.setText('No Camera')


class ZoomImagesWidget(QWidget):
    """
    Widget to display an image in a full screen window.
    Exposure time can be adjusted.
    """

    slider_changed = pyqtSignal(str)

    def __init__(self, zygo_lab):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__(parent=None)
        self.zygo_lab = zygo_lab
        self.layout = QGridLayout()
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, 95)
        self.expo_time = SliderBloc(translate('slider_expo_time'), 'ms', 0, 10)
        self.expo_time.slider_changed.connect(lambda: self.slider_changed.emit('expo_time'))
        self.layout.addWidget(self.expo_time, 0, 0)
        self.zoom_window = ImagesDisplayWidget(self)
        self.layout.addWidget(self.zoom_window, 1, 0)
        self.setLayout(self.layout)
        screen_geometry = self.screen().geometry()
        self.width = screen_geometry.width() - 20
        self.height = screen_geometry.height() - 30
        self.setFixedSize(self.width, self.height)

    def set_slider_range(self, min_value: float, max_value: float):
        """Set the minimum and maximum values for the exposure time slider.
        :param min_value: Minimum value for the exposure time. In ms.
        :param max_value: Maximum value for the exposure time. In ms.
        """
        self.expo_time.set_min_max_slider_values(round(min_value, 3), round(max_value, 1))

    def set_slider_value(self, value: float):
        """Set the value of the exposure time slider.
        :param value: Value of the exposure time. In ms.
        """
        self.expo_time.set_value(round(value, 2))

    def get_exposure(self):
        """Return the exposure time from the slider.
        :return: Exposure time in ms.
        """
        return self.expo_time.get_value()

    def resizeEvent(self, event):
        try:
            self.zoom_window.update_size(self.width-20, self.height-40)
        except Exception as e:
            print(f'Image Display - resize : {e}')


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = CameraChoice(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())