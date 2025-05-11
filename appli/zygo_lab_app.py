# -*- coding: utf-8 -*-
"""*zygo_lab_app.py* file.

*zygo_lab_app* file that contains :class::ZygoLabApp

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Abdallah MRABTI (Promo 2026)
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

.. version:: 3.0
"""
import sys, os
from PyQt6.QtWidgets import QApplication
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from utils.pyqt6_utils import load_default_dictionary
from utils.dataset_utils import load_default_parameters
from views.main_structure import MainView
from views.main_menu import MainMenu
from controllers.modes_manager import ModesManager
from models.dataset import DataSetModel
from models.phase import PhaseModel

version_app = 'r1.0'


class ZygoApp:

    def __init__(self):
        """Constructor of the application."""
        load_default_dictionary("FR")
        self.data_set = DataSetModel()
        self.phase = PhaseModel(self.data_set)
        self.main_widget = MainView(self)
        self.main_menu = MainMenu()
        self.main_menu.load_menu('menu/menu.txt')
        self.main_widget.set_main_menu(self.main_menu)
        self.mode_manager = ModesManager(self)
        self.default_parameters = load_default_parameters('./config.txt')


if __name__ == "__main__":
    print(f'Zygo App - Version {version_app}')
    app = QApplication(sys.argv)
    zygo_app = ZygoApp()
    zygo_app.main_widget.showMaximized()
    sys.exit(app.exec())