# -*- coding: utf-8 -*-
"""*main_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os
import threading, time

import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QTextEdit,
    QMessageBox, QFileDialog, QDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.images.conversion import *
from widgets.camera import *
from widgets.images import *
from widgets.masks import *
from widgets.analysis import *
from widgets.piezo import *
from widgets.acquisition import *
from widgets.aberrations import *
from widgets.xyz_chart_widget import *
from process.hariharan_algorithm import *
from process.zernike_coefficients import *
from skimage.restoration import unwrap_phase
from scipy.ndimage import gaussian_filter

BOT_HEIGHT, TOP_HEIGHT = 45, 50
LEFT_WIDTH, RIGHT_WIDTH = 45, 45
TOP_LEFT_ROW, TOP_LEFT_COL = 1, 1
TOP_RIGHT_ROW, TOP_RIGHT_COL = 1, 2
BOT_LEFT_ROW, BOT_LEFT_COL = 2, 1
BOT_RIGHT_ROW, BOT_RIGHT_COL = 2, 2
SUBMENU_ROW, SUBMENU_COL = 0, 0
OPTIONS_ROW, OPTIONS_COL = 0, 1
SUBOPTIONS_ROW, SUBOPTIONS_COL = 0, 2


# Other functions
def load_menu(file_path: str, menu):
    """
    Load parameter from a CSV file.
    """
    if os.path.exists(file_path):
        # Read the txt file, ignoring lines starting with '#'
        data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the txt file
        for element, title, signal, _ in data:
            if element == 'B':  # button
                menu.add_button(translate(title), signal)
            elif element == 'O':  # options button
                menu.add_button(translate(title), signal, option=True)
            elif element == 'L':  # label title
                menu.add_label_title(translate(title))
            elif element == 'S':  # blank space
                menu.add_space()
        menu.display_layout()
    else:
        print('MENU File error')


def statistics_surface(surface):
    # Process (Peak-to-Valley)
    PV = np.round(np.nanmax(surface) - np.nanmin(surface), 3)
    RMS = np.round(np.nanstd(surface), 3)
    return PV, RMS


# %% Widgets
class MenuWidget(QWidget):
    """
    Main menu of the application
    """

    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None, title: str = 'label_title_main_menu', sub: bool = False):
        """
        Default Constructor.
        :param parent:
        :param title:
        :param sub:
        """
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.submenu = sub
        self.setLayout(self.layout)
        self.buttons_list = []
        self.buttons_signal = []
        self.buttons_enabled = []
        self.actual_button = None

        self.label_title_main_menu = QLabel(translate(title))
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label_title_main_menu)

    def display_layout(self):
        """
        Update the layout with all the elements.
        """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                self.layout.addWidget(element)
            else:
                self.layout.addStretch()

    def add_button(self, title: str, signal: str = None, option: bool = False):
        """
        Add a button into the interface.
        :param title: Title of the button.
        :param signal: Signal triggered by the button.
        :param option: True if the button is an option button (smaller height).
        :return:
        """
        button = QPushButton(translate(title))
        button.setStyleSheet(unactived_button)
        if option:
            button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        else:
            button.setFixedHeight(BUTTON_HEIGHT)
        button.clicked.connect(self.menu_is_clicked)
        self.buttons_list.append(button)
        self.buttons_signal.append(signal)
        self.buttons_enabled.append(True)

    def add_label_title(self, title):
        """
        Add a space in the menu.
        :param title: Title of the label.
        """
        label = QLabel(title)
        label.setStyleSheet(styleH1)
        self.buttons_list.append(label)
        self.buttons_signal.append(None)
        self.buttons_enabled.append(True)

    def inactive_buttons(self):
        """ Switches all buttons to inactive style """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.buttons_enabled[i]:
                    element.setStyleSheet(unactived_button)

    def set_button_enabled(self, button_index: int, value: bool):
        """
        Set a button enabled.
        :param button_index: Index of the button to update.
        :param value: True if the button must be enabled.
        """
        self.buttons_enabled[button_index - 1] = value
        self.buttons_list[button_index - 1].setEnabled(value)
        if value:
            self.buttons_list[button_index - 1].setStyleSheet(unactived_button)
        else:
            self.buttons_list[button_index - 1].setStyleSheet(disabled_button)

    def add_space(self):
        """
        Add a space in the menu.
        :param title:
        :param signal:
        :return:
        """
        self.buttons_list.append(None)
        self.buttons_signal.append(None)
        self.buttons_enabled.append(True)

    def menu_is_clicked(self):
        self.inactive_buttons()
        sender = self.sender()
        self.actual_button = sender

        for i, element in enumerate(self.buttons_list):
            if sender == element:
                if self.submenu is False:
                    # Update Sub Menu
                    self.parent.submenu_widget = MenuWidget(self.parent,
                                                            title=f'sub_menu_{self.buttons_signal[i]}',
                                                            sub=True)
                    self.parent.submenu_widget.menu_clicked.connect(self.submenu_is_clicked)
                    file_name = f'./config/{self.buttons_signal[i]}_menu.txt'
                    load_menu(file_name, self.parent.submenu_widget)

                    self.parent.set_sub_menu_widget(self.parent.submenu_widget)
                    self.parent.submenu_widget.display_layout()
                # Change button style
                sender.setStyleSheet(actived_button)
                # Send signal
                self.menu_clicked.emit(self.buttons_signal[i])

    def update_menu_display(self):
        """Update the menu."""
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.actual_button == element:
                    element.setStyleSheet(actived_button)
                    element.setEnabled(True)
                elif self.buttons_enabled[i] is True:
                    element.setStyleSheet(unactived_button)
                    element.setEnabled(True)
                else:
                    element.setStyleSheet(disabled_button)
                    element.setEnabled(False)

    def set_enabled(self, index: int, value: bool = True):
        """
        Set enabled a button.
        :param index:
        :param value:
        """
        menu = self.parent.get_list_menu('off_menu')
        if isinstance(index, list):
            for i in index:
                if i not in menu:
                    self.buttons_enabled[i - 1] = value
                else:
                    self.buttons_enabled[i - 1] = False
        else:
            if index not in menu:
                self.buttons_enabled[index - 1] = value
            else:
                self.buttons_enabled[index - 1] = False
        self.update_menu_display()

    def set_activated(self, index: int):
        """
        Set activated a button.
        :param index:
        """
        self.inactive_buttons()
        if isinstance(index, list):
            for i in index:
                self.buttons_list[i - 1].setStyleSheet(actived_button)
        else:
            self.buttons_list[index - 1].setStyleSheet(actived_button)

    def submenu_is_clicked(self, event):
        self.menu_clicked.emit(event)


class TitleWidget(QWidget):
    """
    Widget containing the title of the application and the LEnsE logo.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the title widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.label_title = QLabel(translate('label_title'))
        self.label_title.setStyleSheet(styleH1)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_subtitle = QLabel(translate('label_subtitle'))
        self.label_subtitle.setStyleSheet(styleH3)
        self.label_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lense_logo = QLabel('Logo')
        self.lense_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QPixmap("./assets/IOGS-LEnsE-logo_small.jpg")
        # logo = logo_.scaled(imageSize.width()//4, imageSize.height()//4, Qt.AspectRatioMode.KeepAspectRatio)
        self.lense_logo.setPixmap(logo)

        self.layout.addWidget(self.label_title, 0, 0)
        self.layout.addWidget(self.label_subtitle, 1, 0)
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 5)
        self.layout.addWidget(self.lense_logo, 0, 1, 2, 1)

        self.setLayout(self.layout)


class HTMLWidget(QWidget):
    """
    Widget displaying an HTML content.
    """

    def __init__(self, url: str = '', css: str = ''):
        """Default constructor.
        :param url: filepath or url to the HTML page. Default ''.
        """
        super().__init__()
        self.url = url
        self.css = css
        self.html_page = QTextEdit()
        self.html_page.setReadOnly(True)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.html_page)
        self.setLayout(self.layout)
        if url != '':
            self.set_url(self.url, self.css)

    def set_url(self, url: str, css: str = ''):
        """
        Set the URL of the mini browser.
        :param url: filepath or url to the HTML page.
        :param css: filepath to a css file. Default ''.
        """
        self.url = url
        self.css = css

        css_content = ''
        with open(url, "r", encoding="utf-8") as file:
            html_content = file.read()
        if self.css != '':
            with open(css, "r", encoding="utf-8") as file:
                css_content = file.read()

        full_html_content = f"""
        <html>
        <head>
            <style>
            {css_content}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        self.html_page.setHtml(full_html_content)


class MainWidget(QWidget):
    """
    Main central widget of the application.
    """

    main_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        # GUI Structure
        self.layout = QGridLayout()
        self.title_label = TitleWidget(self)
        self.main_menu = MenuWidget(self)
        self.top_left_widget = QWidget()
        self.top_right_widget = QWidget()
        self.bot_right_widget = QWidget()
        # Submenu and option widgets in the bottom left corner of the GUI
        self.bot_left_widget = QWidget()
        self.bot_left_layout = QGridLayout()
        self.bot_left_widget.setLayout(self.bot_left_layout)
        self.bot_left_layout.setColumnStretch(0, 50)
        self.bot_left_layout.setColumnStretch(1, 50)
        self.bot_left_layout.setColumnStretch(2, 50)
        self.submenu_widget = QWidget()
        self.options_widget = QWidget()
        self.suboptions_widget = QWidget()
        self.layout.addWidget(self.title_label, 0, 0, 1, 3)
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)
        self.bot_left_layout.addWidget(self.suboptions_widget, SUBOPTIONS_ROW, SUBOPTIONS_COL)
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)
        # Add elements to the main layout
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

        self.main_menu.menu_clicked.connect(self.menu_action)

        # Adding elements in the layout
        self.layout.addWidget(self.main_menu, 1, 0, 2, 1)
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, LEFT_WIDTH)
        self.layout.setColumnStretch(2, RIGHT_WIDTH)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, TOP_HEIGHT)
        self.layout.setRowStretch(2, BOT_HEIGHT)
        self.setLayout(self.layout)

    def update_menu(self):
        """Update menu depending on the actual mode."""
        # Update menu
        menu = self.get_list_menu('all_menu')
        self.main_menu.set_enabled(menu, True)
        menu = []
        if self.parent.mask_created is False:
            menu += self.get_list_menu('nomask')
        if self.parent.acquisition_done is False and self.parent.images_opened is False:
            menu += self.get_list_menu('nodata')
        if self.parent.camera_connected is False:
            menu += self.get_list_menu('nocam')
        if self.parent.piezo_connected is False:
            menu += self.get_list_menu('nopiezo')
        if self.parent.analysis_completed is False:
            menu += self.get_list_menu('noanalysis')
        self.main_menu.set_enabled(menu, False)

    def menu_action(self, event):
        """
        Action performed when a button of the main menu is clicked.
        Only GUI actions are performed in this section.
        :param event: Event that triggered the action.
        """
        self.main_signal.emit(event)

        # Test if masks changed
        if self.parent.masks_changed:
            self.parent.reset_data()
            self.parent.masks_changed = False

        mode = event
        submode = ''
        if "_" in event:
            modes = event.split('_')
            mode = modes[1]
            submode = modes[0]
        self.parent.main_mode = mode
        self.parent.main_submode = submode

        print(f'Mode = {mode}')
        print(f'SubMode = {submode}')



        # Manage application
        self.main_mode_action()
        self.main_submode_action()

        # Update menu
        self.update_menu()

    def main_mode_action(self):
        """Display information depending on the main mode."""
        if self.parent.main_mode == 'camera':
            '''Camera Mode'''
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            self.action_camera()
            # open html
            html_page = HTMLWidget('./docs/html/camera.html', './docs/html/styles.css')
            self.set_bot_right_widget(html_page)

        elif self.parent.main_mode == 'images':
            '''Images Mode'''
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            # display first image if present
            self.display_first_image()
            # activate item in the submenu
            if self.parent.acquisition_done is False and self.parent.images_opened is False:
                self.submenu_widget.set_button_enabled(2, False)
                self.submenu_widget.set_button_enabled(4, False)
            else:
                self.submenu_widget.set_button_enabled(2, True)
                self.submenu_widget.set_button_enabled(4, True)
            # open html
            html_page = HTMLWidget('./docs/html/images.html', './docs/html/styles.css')
            self.set_bot_right_widget(html_page)

        elif self.parent.main_mode == 'masks':
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            try:
                self.action_masks_visualization()
            except Exception as e:
                print(f'mode Masks : {e}')

        elif self.parent.main_mode == 'piezo':
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            # Display options widget with Masks Options
            self.set_options_widget(PiezoOptionsWidget(self))
            html_page = HTMLWidget('./docs/html/piezo.html', './docs/html/styles.css')
            self.set_bot_right_widget(html_page)

        elif self.parent.main_mode == 'acquisition':
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            self.action_acquisition()
            html_page = HTMLWidget('./docs/html/acquisition.html', './docs/html/styles.css')
            self.set_bot_right_widget(html_page)

        elif self.parent.main_mode == 'simpleanalysis':
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            try:
                self.action_simple_analysis()
            except Exception as e:
                print(f'mode Simple : {e}')

        elif self.parent.main_mode == 'aberrations':
            self.set_top_left_widget(AberrationsOptionsWidget(self))
            self.set_bot_right_widget(AberrationsOptionsWidget(self))
            self.top_left_widget.show_graph()
            self.action_aberrations()

    def main_submode_action(self):
        print(f'\t\tSubmode = {self.parent.main_submode}')
        ## Camera
        if self.parent.main_submode == 'zoom':
            self.action_zoom_camera()

        ## Images
        elif self.parent.main_submode == 'open':
            '''Images Mode / Open SubMode'''
            self.action_menu_open_images()

        elif self.parent.main_submode == 'display':
            self.action_menu_display_images()

        elif self.parent.main_submode == 'save':
            self.action_menu_save_images()
            self.menu_action('display_images')

        elif self.parent.main_submode == 'delete':
            reply = QMessageBox.question(self, 'Delete images', 'Do you really want to delete images ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.parent.images = Images()
                self.parent.masks = Masks()
                self.parent.images_opened = False
                self.parent.mask_created = False
                self.parent.wrapped_phase_done = False
                self.parent.unwrapped_phase_done = False
                self.parent.acquisition_done = False
                self.menu_action('images')

        ## Piezo
        elif self.parent.main_submode == 'move':
            # Display options widget with Masks Options
            self.clear_sublayout(OPTIONS_COL)
            self.set_options_widget(PiezoMoveOptionsWidget(self))
            self.options_widget.voltage_changed.connect(self.action_piezo_move)

        ## Acquisition
        elif self.parent.main_submode == 'simple':
            self.action_simple_acquisition()

        ## Masks
        elif self.parent.main_submode == 'circular':
            if self.parent.images_opened:
                image = self.parent.images.get_image_from_set(1)
            elif self.parent.camera_connected:
                image = self.parent.displayed_image.copy()
            dialog = CircularMaskSelection(image)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                print('NO MASK ADDED !')
            else:
                mask = dialog.mask
                # Add mask to the existing list
                self.parent.masks.add_mask(mask.squeeze(), 'Circ')
                self.parent.mask_created = True
                self.options_widget.set_masks(self.parent.masks)
                self.options_widget.update_display()
                self.parent.masks_changed = True
            self.submenu_widget.set_button_enabled(1, True)
            # Update interface
            self.update_interface(nosub=True)

        elif self.parent.main_submode == 'rectangular':
            if self.parent.images_opened:
                image = self.parent.images.get_image_from_set(1)
            elif self.parent.camera_connected:
                image = self.parent.displayed_image.copy()
            dialog = RectangularMaskSelection(image)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                print('NO MASK ADDED !')
            else:
                mask = dialog.mask
                # Add mask to the existing list
                self.parent.masks.add_mask(mask.squeeze(), 'Rect')
                self.parent.mask_created = True
                self.options_widget.set_masks(self.parent.masks)
                self.options_widget.update_display()
                self.parent.masks_changed = True
            self.submenu_widget.set_button_enabled(2, True)
            # Update interface
            self.update_interface(nosub=True)

        elif self.parent.main_submode == 'polygon':
            if self.parent.images_opened:
                image = self.parent.images.get_image_from_set(1)
            elif self.parent.camera_connected:
                image = self.parent.displayed_image.copy()
            dialog = PolygonalMaskSelection(image)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                print('NO MASK ADDED !')
            else:
                mask = dialog.mask
                # Add mask to the existing list
                self.parent.masks.add_mask(mask.squeeze(), 'Poly')
                self.parent.mask_created = True
                self.options_widget.set_masks(self.parent.masks)
                self.options_widget.update_display()
                self.parent.masks_changed = True
            self.submenu_widget.set_button_enabled(3, True)
            # Update interface
            self.update_interface(nosub=True)

        ## Simple Analysis
        elif self.parent.main_submode == 'wrappedphase':
            if self.parent.images_opened:
                image = self.parent.images.get_image_from_set(1)
                mask = self.parent.masks.get_global_mask()
                if mask is not None:
                    self.top_left_widget.set_image_from_array(image * mask)
                else:
                    self.top_left_widget.set_image_from_array(image)
            self.display_3D_wrapped_phase()

        elif self.parent.main_submode == 'unwrappedphase':
            if self.parent.images_opened:
                image = self.parent.images.get_image_from_set(2)
                mask = self.parent.masks.get_global_mask()
                if mask is not None:
                    self.top_left_widget.set_image_from_array(image * mask)
                else:
                    self.top_left_widget.set_image_from_array(image)
                self.set_suboptions_widget(SimpleAnalysisSubOptionsWidget(self))
                self.suboptions_widget.aberrations_selected.connect(
                    self.aberrations_correction_selected)
                if self.parent.coeff_counter > 3: # Tilt
                   self.suboptions_widget.set_tilt_enabled()
                else:
                    self.suboptions_widget.set_tilt_enabled(False)
            self.display_3D_unwrapped_phase()

        ## Aberrations
        elif self.parent.main_submode == 'Zernikecoefficients':
            self.bot_right_widget.show_Zernike_table()

        elif self.parent.main_submode == 'Seidelcoefficients':
            self.bot_right_widget.show_Seidel_table()

        elif self.parent.main_submode == 'coefficientscorrection':
            self.set_suboptions_widget(AberrationsOptionsWidget(self))
            
            self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
            self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
            (self.SUBOPTIONS_ROW, self.SUBOPTIONS_COL)=(0,1)
            self.set_suboptions_widget(AberrationsChoiceWidget(self))
            self.suboptions_widget.aberrations_choice_changed.connect(self.action_aberrations)
            if self.parent.display_3D:
                # TOP RIGHT - 3D surface with unwrapped phase
                self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
                self.set_top_right_widget(Surface3DWidget(self))
                mask = self.parent.cropped_mask_phase
                displayed_surface = self.parent.unwrapped_phase * self.parent.wedge_factor
                if mask is not None:
                    self.top_right_widget.set_data(displayed_surface, mask,
                                                   bar_title=r"Default magnitude ('$\lambda$')", size=20)
                # BOT RIGHT - 3D surface with corrected phase - auto update when signal ...

            else:
                # TOP RIGHT - 2D surface with unwrapped phase
                # BOT RIGHT - 2D surface with corrected phase
                print('2D')

    def clear_layout(self, row: int, column: int) -> None:
        """
        Remove widgets from a specific position in the layout.
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

    def clear_sublayout(self, column: int) -> None:
        """
        Remove widgets from a specific position in the layout of the bottom left area.
        :param column: Column index of the layout.
        """
        item = self.bot_left_layout.itemAtPosition(0, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

    def set_top_left_widget(self, widget):
        """
        Modify the top left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.top_left_widget = widget
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)

    def set_top_right_widget(self, widget):
        """
        Modify the top right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)

    def set_bot_left_widget(self, widget):
        """
        Modify the bottom left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_LEFT_ROW, BOT_LEFT_COL)
        self.bot_left_widget = widget
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

    def set_bot_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.bot_right_widget = widget
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def set_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL, 2, 1)

    def set_sub_menu_widget(self, widget):
        """
        Modify the sub menu widget.
        :param widget: Widget of the sub menu.
        """
        self.clear_sublayout(SUBMENU_COL)
        self.submenu_widget = widget
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)

    def set_options_widget(self, widget):
        """
        Modify the options widget.
        :param widget: Widget of the options.
        """
        self.clear_sublayout(OPTIONS_COL)
        self.options_widget = widget
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)

    def set_suboptions_widget(self, widget):
        """
        Modify the options widget.
        :param widget: Widget of the options.
        """
        self.clear_sublayout(SUBOPTIONS_COL)
        self.suboptions_widget = widget
        self.bot_left_layout.addWidget(self.suboptions_widget, SUBOPTIONS_ROW, SUBOPTIONS_COL)

    def update_interface(self, nosub=False):
        """Update interface"""
        mode = self.parent.main_mode
        submode = self.parent.main_submode
        str_menu = mode
        if submode is not None and nosub is False:
            str_menu = submode + '_' + mode
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.menu_action(str_menu)

    def aberrations_correction_selected(self, event):
        _, new_surface = self.parent.zernike.process_surface_correction(event)
        PV, RMS = statistics_surface(new_surface)
        self.suboptions_widget.set_values([PV], [RMS])
        self.display_3D_unwrapped_phase(new_surface)

    def display_right(self):
        # Display image with mask in the top right widget
        self.set_top_right_widget(ImagesDisplayWidget(self))
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width * RIGHT_WIDTH) // 100
        he = (height * TOP_HEIGHT) // 100
        self.top_right_widget.update_size(wi, he)

        images = self.parent.images.get_images_set(0)
        mask = self.parent.masks.get_global_mask()
        if mask is not None:
            # Crop images around the mask
            top_left, bottom_right = find_mask_limits(mask)
            height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
            pos_x, pos_y = top_left[1], top_left[0]
            self.parent.cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
            images_c = crop_images(images, (height, width), (pos_x, pos_y))
        else:
            images_c = images
        self.top_right_widget.set_image_from_array(images_c[0])

    def update_size(self, aoi: bool = False):
        """
        Update the size of the main widget.
        """
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width * LEFT_WIDTH) // 100
        he = (height * TOP_HEIGHT) // 100
        self.top_left_widget.update_size(wi, he, aoi)

        if isinstance(self.top_right_widget, ImagesDisplayWidget):
            new_size = self.parent.size()
            width = new_size.width()
            height = new_size.height()
            wi = (width * RIGHT_WIDTH) // 100
            he = (height * TOP_HEIGHT) // 100
            self.top_right_widget.update_size(wi, he, False)

    def get_list_menu(self, menu):
        """ """
        if menu in self.parent.default_parameters:
            return [int(x) for x in self.parent.default_parameters[menu].split(',')]

    def display_first_image(self):
        """Display the first image in the top left widget."""
        if self.parent.images_opened:
            image = self.parent.images.get_image_from_set(1)
            self.top_left_widget.set_image_from_array(image)
            self.update_size()
        elif self.parent.camera_connected:
            '''
            image = self.parent.displayed_image.copy()
            self.top_left_widget.set_image_from_array(image)
            self.update_size()
            '''
            pass

    def display_masked_image(self):
        """Display the first image in the top left widget."""
        if self.parent.images_opened:
            image = self.parent.images.get_image_from_set(1)
        elif self.parent.camera_connected:
            image = self.parent.displayed_image.copy()
        if self.parent.mask_created:
            mask = self.parent.masks.get_global_mask()
            self.top_left_widget.set_image_from_array(image * mask)
        else:
            self.top_left_widget.set_image_from_array(image)
        self.update_size()

    def display_3D_wrapped_phase(self):
        """Display a 3D surface in the right part of the interface."""
        self.set_right_widget(Surface3DWidget(self))
        mask = self.parent.cropped_mask_phase
        displayed_surface = self.parent.wrapped_phase * self.parent.wedge_factor
        if mask is not None:
            self.top_right_widget.set_data(displayed_surface, mask,
                                           bar_title=r"Default magnitude ('$\lambda$')", size=20)
        else:
            print('No mask !')

    def display_3D_unwrapped_phase(self, image = None):
        """Display a 3D surface in the right part of the interface."""
        self.set_right_widget(Surface3DWidget(self))
        mask = self.parent.cropped_mask_phase
        if image is None:
            displayed_surface = self.parent.unwrapped_phase * self.parent.wedge_factor
        else:
            displayed_surface = image * self.parent.wedge_factor
        if mask is not None:
            self.top_right_widget.set_data(displayed_surface, mask,
                                           bar_title=r"Default magnitude ('$\lambda$')", size=20)
            
    def display_3D_phase(self, image = None):
        """Display a 3D surface in the top!!! right part of the interface."""
        self.set_top_right_widget(Surface3DWidget(self))
        mask = self.parent.cropped_mask_phase
        if image is None:
            displayed_surface = self.parent.unwrapped_phase * self.parent.wedge_factor
        else:
            displayed_surface = image * self.parent.wedge_factor
        if mask is not None:
            self.top_right_widget.set_data(displayed_surface, mask,
                                           bar_title=r"Default magnitude ('$\lambda$')", size=20)
        else:
            print('No mask !')

    def display_3D_adjusted_phase(self, image):
        """Display a 3D surface in the bot!!! right part of the interface."""
        self.set_bot_right_widget(Surface3DWidget(self))
        mask = self.parent.cropped_mask_phase
        displayed_surface = image * self.parent.wedge_factor
        if mask is not None:
            self.bot_right_widget.set_data(displayed_surface, mask,
                                           bar_title=r"Default magnitude ('$\lambda$')", size=20)

    def action_camera(self):
        """Action performed when Camera is clicked in the menu."""
        camera_setting = CameraSettingsWidget(self, self.parent.camera)
        self.set_options_widget(camera_setting)
        if 'Max Expo Time' in self.parent.default_parameters:
            self.options_widget.set_maximum_exposure_time(
                float(self.parent.default_parameters['Max Expo Time']))  # in ms
        self.options_widget.update_parameters(auto_min_max=True)
        self.parent.camera_thread.start()

    def action_zoom_camera(self):
        self.parent.camera_thread.start()

    def action_menu_open_images(self):
        """Action performed when the open submode of images is called."""
        try:
            # Display a dialog box to open a MAT file
            self.parent.images, self.parent.masks = self.open_images()
            # Update the submenu and the display - /!\ masks BEFORE images
            if self.parent.masks is not None:
                self.parent.mask_created = True
            else:
                self.parent.mask_created = False
            if self.parent.images is not None:
                pass
                self.parent.images_opened = True
                self.submenu_widget.set_button_enabled(2, True)
                self.submenu_widget.set_activated(2)
                self.submenu_widget.set_button_enabled(4, True)
                self.parent.reset_data()
                self.action_menu_display_images()
            else:
                self.parent.images_opened = False
                self.submenu_widget.set_button_enabled(1, True)
                self.submenu_widget.set_button_enabled(2, False)
                self.submenu_widget.set_button_enabled(4, False)
                self.top_left_widget.reset_image()
        except Exception as e:
            print(f'Open Images : {e}')

    def open_images(self):
        """Action performed when a MAT file has to be loaded."""
        file_dialog = QFileDialog()
        if 'Dir Images' in self.parent.default_parameters:
            default_path = self.parent.default_parameters['Dir Images']
        else:
            default_path = os.path.expanduser("~") + '/Images/'
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_path, "Matlab (*.mat)")

        if file_path != '':
            masks = Masks()
            images = Images()
            data = read_mat_file(file_path)
            images_mat = data['Images']
            images_d = split_3d_array(images_mat)
            if 'Masks' in data:
                mask_mat = data['Masks']
                mask_d = split_3d_array(mask_mat, size=1)
                if isinstance(mask_d, list):
                    for i, maskk in enumerate(mask_d):
                        masks.add_mask(maskk.squeeze())
            if isinstance(images_d, list):
                if len(images_d) % 5 == 0 and len(images_d) > 1:
                    self.parent.wrapped_phase_done = False
                    self.parent.unwrapped_phase_done = False
                    for i in range(int(len(images_d) / 5)):
                        images.add_set_images(images_d[i:i + 5])
                    return images, masks
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("Number of images in this file is not adapted to Hariharan algorithm.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return None, None
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return None, None

    def action_menu_save_images(self):
        """Action performed when a MAT file has to be loaded."""
        self.submenu_widget.set_activated(4)
        file_dialog = QFileDialog()
        if 'Dir Images' in self.parent.default_parameters:
            default_path = self.parent.default_parameters['Dir Images']
        else:
            default_path = os.path.expanduser("~") + '/Images/'
        file_path, _ = file_dialog.getSaveFileName(self, translate('dialog_save_image'),
                                                   default_path, "Matlab (*.mat)")
        if file_path != '':
            images = self.parent.images.get_images_as_list()
            new_data = np.stack((images), axis=2).astype(np.uint8)
            if self.parent.masks.get_masks_number() != 0:
                masks = self.parent.masks.get_mask_list()
                new_mask = np.stack((masks), axis=2).astype(np.uint8)
                write_mat_file(file_path, new_data, new_mask)
            else:
                write_mat_file(file_path, new_data)
                pass
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Data Saved")
            dlg.setText("Data are saved in a MAT file.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
        else:
            self.submenu_widget.set_button_enabled(4, True)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()

    def action_menu_display_images(self):
        """Action performed when images are displayed."""
        # display first image if present on left area and all images on right area
        self.display_first_image()
        self.set_top_right_widget(ImagesDisplayWidget(self))
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width * RIGHT_WIDTH) // 100
        he = (height * TOP_HEIGHT) // 100
        self.top_right_widget.update_size(wi, he, False)

        if self.parent.images_opened:
            set_of_images = self.parent.images.get_images_set(1)
            image = generate_images_grid(set_of_images)
            self.top_right_widget.set_image_from_array(image)
        # Update options widget
        self.set_options_widget(ImagesChoice(self))
        self.submenu_widget.set_button_enabled(2, True)
        self.submenu_widget.set_activated(2)
        self.submenu_widget.set_button_enabled(4, True)
        if self.parent.images_opened or self.parent.acquisition_done:
            self.options_widget.set_images_status(True, index=1)
        else:
            self.options_widget.set_images_status(False)
        if self.parent.mask_created:
            number = self.parent.masks.get_masks_number()
            self.options_widget.set_masks_status(True, number)
        else:
            self.options_widget.set_masks_status(False)

    def action_masks_visualization(self, event=None):
        """Action performed when masks are displayed."""
        try:
            if self.parent.mask_created is False:
                self.parent.masks = Masks()
            # display first image if present
            #self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
            #self.set_top_left_widget(ImagesDisplayWidget(self))
            self.display_first_image()
            # Display options widget with Masks Options
            self.set_options_widget(MasksOptionsWidget(self))
            # Display image with mask in the top right widget
            self.set_top_right_widget(ImagesDisplayWidget(self))
            new_size = self.parent.size()
            width = new_size.width()
            height = new_size.height()
            wi = (width * RIGHT_WIDTH) // 100
            he = (height * TOP_HEIGHT) // 100
            self.top_right_widget.update_size(wi, he)
            if self.parent.images_opened:
                image = self.parent.images.get_image_from_set(1)
            elif self.parent.camera_connected:
                image = self.parent.displayed_image.copy()
            if event is None:
                mask = self.parent.masks.get_global_mask()
                if mask is not None:
                    self.top_right_widget.set_image_from_array(image * mask)
                else:
                    print('No Mask !')
            elif event.isdigit():
                mask, _ = self.parent.masks.get_mask(int(event))
                self.top_right_widget.set_image_from_array(image * mask)
        except Exception as e:
            print(f'Mask Visu : {e}')

    def action_piezo_move(self):
        """Action performed when the voltage slider of the piezo changed."""
        try:
            if self.parent.piezo_connected:
                voltage = self.options_widget.get_voltage()
                self.parent.piezo.write_dac(voltage)
        except Exception as e:
            print(f'Piezo Move : {e}')

    def action_simple_acquisition(self):
        """Action performed when a simple acquisition is required."""
        # If piezo and camera are connected
        if self.parent.piezo_connected and self.parent.camera_connected:
            # Delete old data
            self.parent.images = Images()
            self.parent.acquisition_done = False
            self.parent.images_opened = False
            self.parent.wrapped_phase_done = False
            self.parent.unwrapped_phase_done = False
            # Start thread for acquiring images
            thread = threading.Thread(target=self.thread_simple_acquisition)
            thread.start()
        else:
            if self.parent.piezo_connected is False and self.parent.camera_connected is False:
                text = "Piezo and camera are not connected."
            elif self.parent.camera_connected is False:
                text = "Piezo is not connected."
            else:
                text = "Camera is not connected."
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No Piezo or Camera Connected")
            dlg.setText(text)
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()

    def action_acquisition(self):
        # display masked image if present
        self.display_masked_image()
        # Display options widget with Masks Options
        self.set_options_widget(AcquisitionOptionsWidget(self))
        # Display acquiring Image in the top right widget
        self.set_top_right_widget(ImagesDisplayWidget(self))
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width * RIGHT_WIDTH) // 100
        he = (height * TOP_HEIGHT) // 100
        self.top_right_widget.update_size(wi, he)

    def thread_simple_acquisition(self):
        """Thread to acquire 5 images."""
        print('Start Acquiring...')
        if 'Piezo Voltage' in self.parent.default_parameters:
            voltage_list = self.parent.default_parameters['Piezo Voltage'].split(',')
            voltage_list = [float(i) for i in voltage_list]
            print(f'Voltage List : {len(voltage_list)}')
        else:
            voltage_list = [0.80, 1.62, 2.43, 3.24, 4.05]
        for i in range(5):
            # Move piezo
            self.parent.piezo.write_dac(voltage_list[i])
            # Wait end of movement
            time.sleep(0.6)
            # Acquire image
            image = self.parent.displayed_image.copy().squeeze().astype(np.float32)

            self.options_widget.add_image(image, voltage_list[i])
            self.top_right_widget.set_image_from_array(image, text=f'Image {i + 1}')
            time.sleep(0.2)

        self.parent.images.add_set_images(self.options_widget.images_table.images_list)
        self.parent.acquisition_done = True
        self.main_menu.set_enabled(7, True)
        self.main_menu.set_enabled(8, True)
        image = generate_images_grid(self.options_widget.images_table.images_list)
        self.top_right_widget.set_image_from_array(image, text=f'ALL')

        if self.parent.main_mode == 'acquisition':
            self.submenu_widget.set_button_enabled(2, True)

    def action_simple_analysis(self):
        """Action performed when a simple analysis is required.
        Wrapped, then unwrapped phase processes are started in a thread.
        """
        self.set_options_widget(SimpleAnalysisOptionsWidget())
        self.options_widget.set_wedge_factor(self.parent.wedge_factor)
        self.options_widget.wedge_changed.connect(self.action_wedge_changed)
        if self.parent.wrapped_phase_done is False:
            self.submenu_widget.set_button_enabled(1, False)
            self.submenu_widget.set_button_enabled(2, False)
            thread = threading.Thread(target=self.thread_wrapped_phase_calculation)
            thread.start()
        else:
            if self.parent.unwrapped_phase_done is False:
                self.submenu_widget.set_button_enabled(2, False)
                thread = threading.Thread(target=self.thread_unwrapped_phase_calculation)
                thread.start()
        if self.parent.images_opened:
            image = self.parent.images.get_image_from_set(1)
            self.top_left_widget.set_image_from_array(image)
        html_page = HTMLWidget('./docs/html/simple_analysis.html', './docs/html/styles.css')
        self.set_bot_right_widget(html_page)
        self.parent.acquisition_number = 1

        if self.parent.main_mode == 'simpleanalysis' and self.parent.analysis_completed:
            self.options_widget.set_values(self.parent.pv_stats, self.parent.rms_stats)

    def action_wedge_changed(self):
        """Action performed when the wedge factor changed."""
        # Change the wedge factor
        self.parent.wedge_factor = self.options_widget.get_wedge_factor()
        # Update 3D surface display
        if self.parent.main_submode == 'wrappedphase':
            self.display_3D_wrapped_phase()
        elif self.parent.main_submode == 'unwrappedphase':
            self.suboptions_widget.uncheck_tilt()
            self.display_3D_unwrapped_phase()

    def thread_wrapped_phase_calculation(self):
        """Thread to calculate wrapped phase from 5 images."""
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        images = self.parent.images.get_images_set(k)
        mask = self.parent.masks.get_global_mask()
        if mask is not None:
            # Crop images around the mask
            top_left, bottom_right = find_mask_limits(mask)
            height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
            pos_x, pos_y = top_left[1], top_left[0]
            self.parent.cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
            images_c = crop_images(images, (height, width), (pos_x, pos_y))
            # Filtering images to avoid noise
            images_f = list(map(lambda x: gaussian_filter(x, 10), images_c))

            # Process Phase
            wrapped_phase = hariharan_algorithm(images_f, self.parent.cropped_mask_phase)
            self.parent.wrapped_phase = wrapped_phase
            self.parent.wrapped_phase = np.ma.masked_where(np.logical_not(self.parent.cropped_mask_phase), wrapped_phase)
            # End of process
            self.parent.wrapped_phase_done = True
            if self.parent.main_mode == 'simpleanalysis':
                self.submenu_widget.set_button_enabled(1, True)
            thread = threading.Thread(target=self.thread_unwrapped_phase_calculation)
            thread.start()

    def thread_unwrapped_phase_calculation(self):
        """"""
        # Process unwrapping phase
        self.parent.unwrapped_phase = unwrap_phase(self.parent.wrapped_phase) / (2 * np.pi)

        self.parent.unwrapped_phase = np.ma.masked_where(np.logical_not(self.parent.cropped_mask_phase),
                                                         self.parent.unwrapped_phase)
        self.parent.unwrapped_phase_to_correct = self.parent.unwrapped_phase.copy()
        self.parent.unwrapped_phase_to_correct[~self.parent.cropped_mask_phase] = np.nan
        self.parent.unwrapped_phase_done = True
        if self.parent.main_mode == 'simpleanalysis' or self.parent.main_submode == 'wrappedphase':
            self.submenu_widget.set_button_enabled(2, True)
        self.parent.zernike.set_surface(self.parent.unwrapped_phase_to_correct)
        thread = threading.Thread(target=self.thread_statistics_calculation)
        thread.start()

    def thread_statistics_calculation(self):
        """Process PeakValley and RMS statistics on Unwrapped phase."""
        self.parent.pv = []
        self.parent.rms = []
        if self.parent.unwrapped_phase_done:
            for i in range(self.parent.acquisition_number):
                pv, rms = statistics_surface(self.parent.unwrapped_phase_to_correct)
                self.parent.pv_stats.append(pv)
                self.parent.rms_stats.append(rms)
            self.parent.analysis_completed = True
            if self.parent.main_mode == 'simpleanalysis':
                self.options_widget.set_values(self.parent.pv_stats, self.parent.rms_stats)

            thread = threading.Thread(target=self.thread_zernike_calculation)
            thread.start()

    def action_aberrations(self, event=None):
        """Action to do when aberrations correction occured."""
        if event is not None:
            if event == 'choice_changed':
                if self.parent.display_3D:
                    # BOT RIGHT - 3D surface with corrected phase - auto update when signal ...
                    self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
                    self.set_bot_right_widget(Surface3DWidget(self))
                    ab_corr_list = self.suboptions_widget.aberrations_list
                    print(ab_corr_list)
                    mask = self.parent.cropped_mask_phase
                    _, new_surface = self.parent.zernike.process_surface_correction(ab_corr_list)
                    new_surface = new_surface * self.parent.wedge_factor
                    if mask is not None:
                        self.bot_right_widget.set_data(new_surface, mask,
                                                       bar_title=r"Default magnitude ('$\lambda$')",
                                                       size=20)
        else:
            self.set_options_widget(AberrationsOptionsWidget(self))

    def thread_zernike_calculation(self):
        """Process Zernike coefficients for correction."""
        print(f'Zernike [{self.parent.coeff_counter}]')
        self.parent.zernike.process_zernike_coefficient(self.parent.coeff_counter)

        self.parent.coeff_counter += 1
        if self.parent.coeff_counter <= self.parent.coeff_zernike_max:
            thread = threading.Thread(target=self.thread_zernike_calculation)
            time.sleep(0.1)
            thread.start()
        else:
            # At the end, analysis completed !
            self.parent.analysis_completed = True
            time.sleep(0.1)
            self.update_menu()


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = MainWidget(self)
            self.setCentralWidget(self.central_widget)

        def create_gui(self):
            widget1 = QWidget()
            widget1.setStyleSheet('background-color: red;')
            self.central_widget.set_top_left_widget(widget1)
            widget2 = QWidget()
            widget2.setStyleSheet('background-color: blue;')
            self.central_widget.set_top_right_widget(widget2)
            widget3 = QWidget()
            widget3.setStyleSheet('background-color: green;')
            self.central_widget.set_sub_menu_widget(widget3)
            widget4 = QWidget()
            widget4.setStyleSheet('background-color: yellow;')
            self.central_widget.set_bot_right_widget(widget4)

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
    main.create_gui()
    main.show()
    sys.exit(app.exec())
