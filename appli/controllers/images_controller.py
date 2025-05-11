# -*- coding: utf-8 -*-
"""*images_controller.py* file.

./controllers/images_controller.py contains ImagesController class to manage "images" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os

import matplotlib.pyplot as plt
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.images_choice_view import ImagesChoiceView
from views.html_view import HTMLView
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import QWidget, QFileDialog
from models.dataset import DataSetModel
from utils.dataset_utils import generate_images_grid
from utils.pyqt6_utils import message_box

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager

class ImagesController:
    """
    Images mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModeManager).
        """
        self.manager: "ModesManager" = manager
        self.data_set: DataSetModel = self.manager.data_set
        self.main_widget: MainView = self.manager.main_widget
        self.images_loaded = (self.data_set.images_sets.get_number_of_sets() >= 1)
        self.masks_loaded = (len(self.data_set.get_masks_list()) >= 1)
        # Graphical elements
        self.top_left_widget = ImagesDisplayView()        # Display first image of a set
        self.top_right_widget = ImagesDisplayView()       # Display grid of images
        self.bot_right_widget = HTMLView()                # HTML Help on images
        # Submenu
        self.submenu = SubMenu(translate('submenu_images'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/images_menu.txt')
        else:
            self.submenu.load_menu('menu/images_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1 / Option 2
        self.options_widget = QWidget()        # Image Choice (if images are loaded)

        #Init view
        self.init_view()

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/images.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/images.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        # Images loaded ?
        if self.images_loaded:
            # Display first image in top left
            images = self.manager.data_set.get_images_sets(1)
            self.top_left_widget.set_image_from_array(images[0])
            g_images = generate_images_grid(images)
            self.top_right_widget.set_image_from_array(g_images)
        # Update menu
        self.update_submenu_view("")

    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, False)
        self.submenu.set_button_enabled(1, True)
        ## Activate button depending on data
        # Images loaded ?
        if self.images_loaded:
            self.submenu.set_button_enabled(2, True)
        # Data acquired ? Saving images is ok
        ### TO DO
        ## Update menu
        match submode:
            case 'open_images':
                self.submenu.set_activated(1)
            case 'display_images':
                self.submenu.set_activated(2)

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'open_images':
                state = self.open_mat_file()
                if state:
                    # Erase old data
                    self.manager.phase.reset_phase()
                    # Update submenu to display images
                    self.update_submenu("display_images")
                else:
                    self.update_submenu("")
            case 'display_images':
                if self.data_set.images_sets.get_number_of_sets() >= 1:
                    # Display first image in top left
                    images = self.data_set.get_images_sets(1)
                    self.top_left_widget.set_image_from_array(images[0])
                    g_images = generate_images_grid(images)
                    self.top_right_widget.set_image_from_array(g_images)
                    self.options_widget = ImagesChoiceView(self)
                    self.manager.main_widget.set_options_widget(self.options_widget)
            case 'save_images':
                pass

    def open_mat_file(self) -> bool:
        """
        Load a MAT file after controller click.
        :return: True if the file is opened and images are present.
        """
        file_dialog = QFileDialog()
        # Check default_path in default_parameters !

        default_path = os.path.expanduser(".") + '/_data/'
        file_path, _ = file_dialog.getOpenFileName(self.main_widget, translate('dialog_open_image'),
                                                   default_path, "Matlab (*.mat)")
        if file_path != '':
            self.images_loaded = self.data_set.load_images_set_from_file(file_path)
            if self.images_loaded is False:
                msg = "No images in the files or bad format of data."
                message_box("Warning - No Images Loaded", msg)
                return self.images_loaded
            else:
                self.masks_loaded = self.data_set.load_mask_from_file(file_path)
                if self.masks_loaded is False:
                    msg = "No masks in the files."
                    message_box("Warning - No Mask Loaded", msg)
                return True
        else:
            msg = "No Image File was loaded..."
            message_box("Warning - No File Loaded", msg)
            return False


if __name__ == "__main__":
    from zygo_lab_app import ZygoApp
    from PyQt6.QtWidgets import QApplication
    from controllers.modes_manager import ModesManager
    from views.main_menu import MainMenu

    app = QApplication(sys.argv)
    m_app = ZygoApp()
    data_set = DataSetModel()
    m_app.data_set = data_set
    m_app.main_widget = MainView()
    m_app.main_menu = MainMenu()
    m_app.main_menu.load_menu('')
    manager = ModesManager(m_app)


    # Test controller
    manager.mode_controller = ImagesController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())

