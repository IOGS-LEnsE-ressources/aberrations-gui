# -*- coding: utf-8 -*-
"""*analysis_app.py* file.

*analysis_app* file that contains :class::AnalysisApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : https://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-PolyAberrations.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QDialog,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QSignalMapper
from PyQt6.QtGui import QPixmap, QIcon, QCloseEvent

from lensepy import load_dictionary, translate, dictionary

from widgets.title_widget import TitleWidget
from widgets.analysis_menu_widget import AnalysisMenuWidget
from widgets.display_zernike_widget import *
from widgets.bar_chart_widget import BarChartWidget
from widgets.psf_view import *
from widgets.mtf_view import *

from process.zernike_coefficents import *

class AnalysisApp(QWidget):
    """
    /!\ NEED TO RECEIVE DATA TO PROCESS ANALYSIS / phase ? coeff ?
    """

    window_closed = pyqtSignal(str)
    WAVELENGTH = 632.8e-9 # m

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)

        self.parent = parent

        self.focal = 150 # mm
        self.f_number = 0.08

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Columns stretch: 10%, 45%, 45%
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 45)
        self.layout.setColumnStretch(2, 45)

        # Rows stretch: 4%, 48%, 48%
        self.layout.setRowStretch(0, 4)
        self.layout.setRowStretch(1, 48)
        self.layout.setRowStretch(2, 48)

        # Permanent Widgets
        # -----------------
        # Title Widget: first row of the grid layout
        self.title_widget = TitleWidget()
        self.title_widget.set_title("Contrôles interférométriques | Analyses poussées")
        self.layout.addWidget(self.title_widget, 0, 0, 1, 3)

        # Analysis Menu Widget: fist column of the grid layout
        self.main_menu_widget = AnalysisMenuWidget(self)
        self.layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)

        if parent is not None:
            self.parent.analysis_requested.connect(self.check_data)
        self.main_menu_widget.analysis_selected.connect(self.analysis_is_selected)

        if parent is None:
            #Only for testing
            self.zernike_coefficients = 2 * np.random.rand(37) - 1

            x = y = np.linspace(-5, 5, 1024)
            X, Y = np.meshgrid(x, y)
            phase_test = np.ones_like(X)
            phase_test[X**2 + Y**2 > 4**2] = 0
            aberration_term = (np.sqrt(8)*X*(X**2+Y**2)-2)*0.003 # Coma
            self.wavefront = phase_test*np.exp(2*I*PI*aberration_term)

        # Signals
        # -------
        self.main_menu_widget.focal_changed.connect(self.on_focal_changed)
        self.main_menu_widget.f_number_changed.connect(self.on_f_number_changed)

    def check_data(self):
        try:
            self.wavefront = self.parent.phase
            self.aberrations_considered = self.parent.aberrations_considered
            
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", f"Il n'y a pas de donner à analyser. \n {e}")
            self.close()  # Close the window to trigger closeEvent
            return
        
        try:
            self.zernike_coefficients = self.parent.acquisition_menu_widget.submenu_remove_faults.coeffs
        except:
            self.zernike_coefficients = get_zernike_coefficient(self.wavefront)
        self.wavefront, self.zernike_coefficients, _ = remove_aberration(self.wavefront, self.aberrations_considered, self.zernike_coefficients)
        
        print(self.zernike_coefficients)
        self.zernike_coefficients *= 1-self.aberrations_considered

    def analysis_is_selected(self, event):
        """
        Manage menu selection.
        Depending on the analysis required, layout is changing.
        """
        self.reset_layout()
        if event == 'zernike':
            zernike_display = ZernikeDisplayWidget(self.zernike_coefficients)
            seidel_display = SeidelDisplayWidget(self.zernike_coefficients)
            zernike_graph = BarChartWidget()
            zernike_graph.set_data(list(range(len(self.zernike_coefficients))), self.zernike_coefficients)

            self.layout.addWidget(zernike_display, 1, 1)
            self.layout.addWidget(seidel_display, 1, 2)
            self.layout.addWidget(zernike_graph, 2, 1, 1, 2)

        elif event == 'psf':
            psf_display = PointSpreadFunctionDisplay(self)
            psf = psf_display.update_psf()
            self.zoom = psf_display.zoom
            self.grid_size = psf_display.grid_size
            psf_slice = PointSpreadFunctionSlice(psf, self)
            psf_circled_energy = PointSpreadFunctionCircledEnergy(psf, self)
            psf_defoc = PointSpreadFunctionDefoc(self)

            self.layout.addWidget(psf_display, 1, 1)
            self.layout.addWidget(psf_slice, 1, 2)
            self.layout.addWidget(psf_circled_energy, 2, 1)
            self.layout.addWidget(psf_defoc, 2, 2)

        elif event == 'mtf':
            mtf_display = ModulationTransfertFunctionDisplay(self)
            mtf = mtf_display.update_mtf()
            self.zoom = mtf_display.zoom
            self.grid_size = mtf_display.grid_size
            mtf_slice = ModulationTransfertFunctionSlice(mtf, self)
            mtf_defoc = ModulationTransfertFunctionDefoc(self)

            self.layout.addWidget(mtf_display, 1, 1)
            self.layout.addWidget(mtf_slice, 1, 2)
            self.layout.addWidget(mtf_defoc, 2, 1, 1, 2)


    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout without deleting them.

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

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.main_menu_widget.reset_menu()
        self.reset_layout()
        self.window_closed.emit('analysis_window_closed')

    def reset_layout(self):
        self.clear_layout(1,1)
        self.clear_layout(1,2)
        self.clear_layout(2,1)
        self.clear_layout(2,2)

    def resizeEvent(self, event):
        """Action performed when the window is resized.
        """
        super().resizeEvent(event)

    # Signals binding
    # ---------------
    def on_focal_changed(self, text):
        self.focal = float(text)
        print(f"Focale changed: {self.focal}")

    def on_f_number_changed(self, text):
        self.f_number = float(text)
        print(f"f-number changed: {self.f_number}")

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Define Window title
            self.setWindowTitle(translate("Zygo-IDS Labwork APP"))
            self.setWindowIcon(QIcon('assets\IOGS-LEnsE-icon.jpg'))
            self.setGeometry(50, 50, 700, 700)

            self.central_widget = AnalysisApp()
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            pass
            """reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if self.central_widget.camera is not None:
                    self.central_widget.camera_widget.disconnect()
                event.accept()
            else:
                event.ignore()"""


    app = QApplication(sys.argv)
    main = MyWindow()
    main.showMaximized()
    sys.exit(app.exec())