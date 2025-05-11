# -*- coding: utf-8 -*-
"""*masks_controller.py* file.

./controllers/masks_controller.py contains MasksController class to manage "masks" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os

import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views import *
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6 import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QDialog
)
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.masks_options_view import MasksOptionsView
from views.masks_view import MasksView
from models.dataset import DataSetModel
from utils.pyqt6_utils import message_box

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager


class MasksController:
    """
    Masks mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModeManager).
        """
        self.manager: "ModesManager" = manager
        self.main_widget: MainView = self.manager.main_widget
        self.data_set: DataSetModel = self.manager.data_set
        self.images_loaded = (self.data_set.images_sets.get_number_of_sets() >= 1)
        # Graphical elements
        self.top_left_widget = ImagesDisplayView()      # Display first image of a set
        self.top_right_widget = ImagesDisplayView()     # Display first image with the global mask
        self.bot_right_widget = HTMLView()              # HTML Help on masks
        # Submenu
        self.submenu = SubMenu(translate('submenu_masks'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/masks_menu.txt')
        else:
            self.submenu.load_menu('menu/masks_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)
        # Option 1
        self.options1_widget = MasksOptionsView(self)   # Masks options
        # Option 2
        self.options2_widget = QWidget()        # ??
        # Update menu and view
        self.update_submenu_view("")
        self.init_view()

    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.clear_all()
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../docs/html/masks.html', '../docs/html/styles.css')
        else:
            self.bot_right_widget.set_url('docs/html/masks.html', 'docs/html/styles.css')
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)
        self.options1_widget.masks_changed.connect(self.masks_changed)
        # Update first image
        first_image = self.data_set.get_images_sets(1)[0]
        self.top_left_widget.set_image_from_array(first_image)

    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()
        for k in range(len(self.submenu.buttons_list)):
            self.submenu.set_button_enabled(k + 1, True)
        ## Activate button depending on data
        match submode:
            case 'circular_masks':
                self.submenu.set_activated(1)
            case 'rectangular_masks':
                self.submenu.set_activated(2)
            case 'polygon_masks':
                self.submenu.set_activated(3)

    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        first_image = self.data_set.get_images_sets(1)[0]
        # Update Action
        if event == 'first':
            # Update first image and global mask in the top right area
            mask = self.data_set.get_global_mask()
            if mask is not None:
                first_image = first_image * mask
                # TO DO -> MainMenu update / Add nomask in options_list
            self.top_right_widget.set_image_from_array(first_image)

        if '_masks' in event:
            if 'circular' in event:
                type = 'circular'
                help = 'Select 3 different points and then Click Enter'
                type_m = 'circ'
            elif 'rectangular' in event:
                type = 'rectangular'
                help = 'Select 2 different points (diagonal of the rectangle) and then Click Enter'
                type_m = 'rect'
            elif 'polygon' in event:
                type = 'polygon'
                help = ('Select N different points, the last one must be at the same place'
                        ' as the first one and then Click Enter')
                type_m = 'poly'
            dialog = MasksView(first_image, type, help)
            result = dialog.exec()
            if result == QDialog.DialogCode.Rejected:
                message_box('No mask added', 'No mask will be added to the list of masks.')
                #print('NO MASK ADDED !')
            else:
                mask = dialog.mask.copy()
                # Add mask to the data_set
                self.data_set.add_mask(mask, type_m)

                # Test if no mask -> update options_list
                if 'nomask' in self.manager.options_list:
                    self.manager.options_list.remove('nomask')
                    self.manager.main_menu.update_menu_display()
                # Refresh list
                self.options1_widget.masks_list.update_display()


    def masks_changed(self, event):
        """
        Update controller data and views when options changed.
        :param event: Signal that triggers the event.
        """
        change = event.split(',')
        print(change)


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

    # Update data
    manager.data_set.load_images_set_from_file("../_data/test4.mat")
    manager.data_set.load_mask_from_file("../_data/test4.mat")

    # Test controller
    manager.mode_controller = MasksController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())
