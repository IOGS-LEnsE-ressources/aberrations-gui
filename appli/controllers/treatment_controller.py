# -*- coding: utf-8 -*-
"""*analyses_controller.py* file.

./controllers/analyses_controller.py contains AnalysesController class to manage "analyses" mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
import threading, time
import numpy as np
from matplotlib import pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from views.main_structure import MainView
from views.sub_menu import SubMenu
from views.images_display_view import ImagesDisplayView
from views.html_view import HTMLView
from views.surface_2D_view import Surface2DView
from views.bar_graph_view import BarGraphView
from lensepy import load_dictionary, translate, dictionary
from models.phase import process_statistics_surface
from views.aberrations_options_view import AberrationsOptionsView
from views.aberrations_start_view import AberrationsStartView
from views.aberrations_choice_view import AberrationsChoiceView
from views.table_view import TableView
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget
)
from models.zernike_coefficients import Zernike, aberrations_type, aberrations_list
from utils.dataset_utils import generate_images_grid, DataSetState
#from views.treatment_views import TreatmentView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.modes_manager import ModesManager
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

class TreatmentController:
    """
    Analyses mode manager.
    """

    def __init__(self, manager: "ModesManager"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModesManager).
        """
        self.manager: "ModesManager" = manager
        self.data_set: DataSetModel = self.manager.data_set
        self.phase: "PhaseModel"= self.manager.phase
        self.zernike_coeffs: Zernike = Zernike(self.phase)
        self.main_widget: MainView = self.manager.main_widget
        self.sub_mode = ''
        self.corrected_aberrations_list = []
        self.corrected_initial_list = ['piston','tilt']
        #
        self.masks_loaded = self.data_set.get_global_mask()
        plt.figure()
        plt.imshow(self.masks_loaded)
        plt.show()
        self.lambda_check = False
        self.lambda_value = 632.8

        # Graphical elements
        self.top_left_widget = QWidget()
        self.top_right_widget = Surface2DView('Unwrapped Phase')
        self.bot_right_widget = HTMLView()
        self.colors = []
        # Submenu
        self.submenu = SubMenu(translate('submenu_postprocess'))
        if __name__ == "__main__":
            self.submenu.load_menu('../menu/postprocess_menu.txt')
        else:
            self.submenu.load_menu('menu/postprocess_menu.txt')
        self.submenu.menu_changed.connect(self.update_submenu)

        # Option 1
        self.options1_widget = QWidget()         # ??
        # Option 2
        self.options2_widget = QWidget()        # ??

        # Update menu and view
        self.init_view()


    def init_view(self):
        """
        Initializes the main structure of the interface.
        """
        self.main_widget.set_sub_menu_widget(self.submenu)
        self.main_widget.set_top_left_widget(self.top_left_widget)
        self.main_widget.set_top_right_widget(self.top_right_widget)
        self.main_widget.set_options_widget(self.options1_widget)

        ## Test 2D or 3D ??
        unwrapped = self.phase.get_unwrapped_phase()
        unwrapped_array = unwrapped.filled(np.nan)
        # Display wrapped in 2D
        self.top_right_widget.set_array(unwrapped_array)

        # Process Zernike coefficients
        for k in range(self.zernike_coeffs.max_order + 1):
            self.zernike_coeffs.process_zernike_coefficient(k)

        self.display_bar_graph_coeff()


    def update_submenu_view(self, submode: str):
        """
        Update the view of the submenu to display new options.
        :param submode: Submode name : [open_images, display_images, save_images]
        """
        self.manager.update_menu()
        self.submode = submode
        ## Erase enabled list for buttons
        self.submenu.inactive_buttons()

        # Update views
        self.main_widget.clear_bot_right()
        self.main_widget.clear_options()
        # For all submodes
        self.display_bar_graph_coeff()

        self.bot_right_widget = HTMLView()
        url = 'docs/html/FR/aberrations.html'
        css = 'docs/html/styles.css'
        if __name__ == "__main__":
            self.bot_right_widget.set_url('../' + url, '../' + css)
        else:
            self.bot_right_widget.set_url(url, css)
        self.main_widget.set_bot_right_widget(self.bot_right_widget)

        # Specific submodes
        match self.submode:
            case 'psf_process':
                pass
            case 'airy_process':
                pass


    def update_submenu(self, event):
        """
        Update data and views when the submenu is clicked.
        :param event: Sub menu click.
        """
        # Update view
        self.update_submenu_view(event)
        # Update Action
        match event:
            case 'psf_process':
                pass


    def display_bar_graph_coeff(self, disp_correct: bool = False, first: bool = False):
        """
        Display the Zernike coefficients in a bargraph, in the top left area.
        :param disp_correct: True if all the coefficients must be displayed.
        :param first: True if only the first coefficients (piston, tilt and defocus) must be set to 0.
        """
        self.main_widget.clear_top_left()
        # Create bargraph
        self.top_left_widget = BarGraphView()
        self.main_widget.set_top_left_widget(self.top_left_widget)
        # Labels
        x_axis_label = translate('coeff_noll_index')
        if self.lambda_check:
            unit = ' (um)'
        else:
            unit = ' (\u03BB)'
        y_axis_label = translate('coeff_y_axis_label') + unit
        # Data
        max_order = self.zernike_coeffs.max_order
        x_axis = np.arange(max_order + 1)
        coeffs_disp = self.zernike_coeffs.get_coeffs().copy()

        self.update_color_aberrations()
        # Force to 0 corrected coefficients
        if first:
            for jj, aberration in enumerate(self.corrected_initial_list):
                for k in aberrations_type[aberration]:
                    coeffs_disp[k] = 0
        if disp_correct:
            for jj, aberration in enumerate(self.corrected_aberrations_list):
                for k in aberrations_type[aberration]:
                    coeffs_disp[k] = 0
        y_axis = np.array(coeffs_disp)
        self.top_left_widget.set_data(x_axis, y_axis, color_x=self.colors)
        self.top_left_widget.set_labels(x_axis_label, y_axis_label)


    def display_2D_ab_init(self, defocus: bool = False):
        """
        Display tilt and piston corrected phase in the top right corner.
        :param defocus: If defocus aberration has to be corrected on display.
        """
        self.main_widget.clear_top_right()
        # Display wrapped in 2D
        self.top_right_widget = Surface2DView(translate('initial_corrected_phase'))
        self.main_widget.set_top_right_widget(self.top_right_widget)
        # Correction of the phase with tilt and piston
        # Check if defocus has to be corrected
        if defocus:
            if 'defocus' not in self.corrected_aberrations_list:
                self.corrected_aberrations_list.append('defocus')
        else:
            if 'defocus' in self.corrected_aberrations_list:
                self.corrected_aberrations_list.remove('defocus')

        new_list = self.corrected_initial_list + self.corrected_aberrations_list
        wedge_factor = self.phase.get_wedge_factor()
        _, corrected = self.zernike_coeffs.process_surface_correction(new_list)
        unwrapped_array = corrected * wedge_factor
        z_label = translate('phase_value_in') + ' (\u03BB)'
        if self.lambda_check:
            unwrapped_array = unwrapped_array * self.lambda_value * 1e-9 * 1e6
            z_label = translate('phase_value_in') + ' (um)'
        unwrapped_array = unwrapped_array.filled(np.nan)
        # Statistics
        self.top_right_widget.set_array(unwrapped_array)
        self.top_right_widget.set_z_axis_label(z_label)
        pv, rms = process_statistics_surface(unwrapped_array)
        # TO DO : depending on lambda or nm -> PV RMS to modify (and units !)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')

    def display_2D_ab_corrected(self):
        """
        Display tilt and piston corrected phase in the top right corner.
        """
        self.main_widget.clear_bot_right()
        # Display wrapped in 2D
        self.bot_right_widget = Surface2DView(translate('ab_corrected_phase'))
        self.main_widget.set_bot_right_widget(self.bot_right_widget)
        # Correction of the phase with tilt and piston
        wedge_factor = self.phase.get_wedge_factor()
        correction_list = self.corrected_initial_list + self.corrected_aberrations_list
        _, corrected = self.zernike_coeffs.process_surface_correction(correction_list)
        unwrapped_array = corrected * wedge_factor
        if self.lambda_check:
            unwrapped_array = unwrapped_array * self.lambda_value * 1e-9 * 1e6
        unwrapped_array = unwrapped_array.filled(np.nan)
        # Statistics
        self.bot_right_widget.set_array(unwrapped_array)
        '''
        pv, rms = process_statistics_surface(unwrapped_array)
        self.options1_widget.set_pv_uncorrected(pv, '\u03BB')
        self.options1_widget.set_rms_uncorrected(rms, '\u03BB')
        '''

    def update_color_aberrations(self):
        """
        Return a list of color to apply on Zernike bar graph.
        Orange : corrected value, blue : order 1, ...
        """
        self.colors = [None] * (self.zernike_coeffs.max_order + 1)
        #
        for k, ab_type in enumerate(aberrations_list):
            if '3' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#0f4d7a'
            elif '5' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1567a5'
            elif '7' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1a82cf'
            elif '9' in ab_type:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#1f9cfa'
            else:
                for jj in aberrations_type[ab_type]:
                    self.colors[jj] = '#051725'

        for jj, aberration in enumerate(self.corrected_aberrations_list):
            for k in aberrations_type[aberration]:
                self.colors[k] = ORANGE_IOGS

        for jj, aberration in enumerate(self.corrected_initial_list):
            for k in aberrations_type[aberration]:
                self.colors[k] = ORANGE_IOGS

        if self.colors[k] is None:
            self.colors[k] = BLUE_IOGS


if __name__ == "__main__":
    from zygo_lab_app import ZygoApp
    from PyQt6.QtWidgets import QApplication
    from controllers.modes_manager import ModesManager
    from views.main_menu import MainMenu
    from models.dataset import DataSetModel
    from models.phase import PhaseModel

    app = QApplication(sys.argv)
    m_app = ZygoApp()
    data_set = DataSetModel()
    m_app.data_set = data_set
    m_app.phase = PhaseModel(m_app.data_set)
    m_app.main_widget = MainView()
    m_app.main_menu = MainMenu()
    m_app.main_menu.load_menu('')
    manager = ModesManager(m_app)
    # Update data
    manager.data_set.load_images_set_from_file("../_data/test3.mat")
    manager.data_set.load_mask_from_file("../_data/test3.mat")
    manager.phase.prepare_data()
    manager.phase.process_wrapped_phase()
    manager.phase.process_unwrapped_phase()

    # Test controller
    manager.mode_controller = TreatmentController(manager)
    m_app.main_widget.showMaximized()
    sys.exit(app.exec())