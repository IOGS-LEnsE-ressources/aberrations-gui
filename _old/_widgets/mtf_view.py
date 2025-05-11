# -*- coding: utf-8 -*-
"""*mtf_view.py* file.

*mtf_view* file that contains :class::AnalysisApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : https://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-PolyAberrations.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)

import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QDialog,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QSignalMapper
from PyQt6.QtGui import QPixmap, QIcon, QCloseEvent

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *

from process.compute_psf_ftm import *

import pyqtgraph as pg

if __name__ == '__main__':
    from lineedit_bloc import LineEditBloc
    from x_y_z_chart_widget import Surface3DWidget
    from x_y_chart_widget import *
else:
    from widgets.lineedit_bloc import LineEditBloc
    from widgets.x_y_z_chart_widget import Surface3DWidget
    from widgets.x_y_chart_widget import *


# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

x = y = np.linspace(-5, 5, 500)
X, Y = np.meshgrid(x, y)
phase_test = np.ones_like(X)
phase_test[X**2 + Y**2 > 4**2] = 0
phase_test = phase_test*np.exp(2*I*PI*(np.sqrt(8)*X*(X**2+Y**2)-2)*0.007) # Coma

# MTF Display
# ===========
class ModulationTransfertFunctionDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent
        
        if parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.wavefront

        self.grid_size = 1024
        self.zoom = 4

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('MTF - 3D')
        self.label_title.setStyleSheet(styleH1)

        # Zero-padding selectors
        # ----------------------
        self.lineedit_grid_size = LineEditBloc(title='Ne', txt=str(self.grid_size))
        self.lineedit_grid_size.editing_finished_signal().connect(self.on_grid_size_change)
        self.lineedit_zoom = LineEditBloc(title='Zoom', txt=str(self.zoom))
        self.lineedit_zoom.editing_finished_signal().connect(self.on_zoom_change)
        self.sublayout = QHBoxLayout()
        self.sublayout.addWidget(self.lineedit_grid_size)
        self.sublayout.addWidget(self.lineedit_zoom)

        # MTF
        # ---
        self.mtf_display = Surface3DWidget()
        self.mtf_display.set_background('lightgray')
        self.mtf_display.setMaximumHeight(300)

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.sublayout)
        self.layout.addWidget(self.mtf_display)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def on_grid_size_change(self):
        self.grid_size = int(self.lineedit_grid_size.text())
        self.update_mtf()

    def on_zoom_change(self):
        self.zoom = float(self.lineedit_zoom.text())
        self.update_mtf()

    def update_mtf(self):
        print('update MTF')
        mtf = get_mtf(self.phase, self.zoom, self.grid_size)
        #mtf = get_mtf(self.phase, 4, 1024)

        mtf_for_display = thresholed_log(mtf)
        
        cutoff_frequency = (self.parent.WAVELENGTH*self.parent.f_number)**(-1)
        X = Y = 2**(-self.zoom) * cutoff_frequency * np.linspace(-self.grid_size/2 * 2**(-self.zoom), self.grid_size/2 * 2**(-self.zoom), self.grid_size)
        X, Y = np.meshgrid(X, Y)

        mtf_for_display *= (np.nanmax(X) - np.nanmin(X))/4 / (np.nanmax(mtf_for_display)-np.nanmin(mtf_for_display))
        mtf_for_display -= np.nanmax(mtf_for_display)/4

        self.mtf_display.set_data(X[mtf.shape[0]//4:3*mtf.shape[0]//4, mtf.shape[0]//4:3*mtf.shape[0]//4], Y[mtf.shape[0]//4:3*mtf.shape[0]//4, mtf.shape[0]//4:3*mtf.shape[0]//4], mtf_for_display[mtf.shape[0]//4:3*mtf.shape[0]//4, mtf.shape[0]//4:3*mtf.shape[0]//4])
        self.mtf_display.refresh_chart()
        return mtf

# MTF Slice
# ===========
class ModulationTransfertFunctionSlice(QWidget):
    def __init__(self, mtf, parent=None):
        super().__init__(parent=None)

        self.parent = parent
        self.mtf = mtf

        if parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.wavefront
        self.theorical_mtf = get_mtf(np.abs(self.phase), self.parent.zoom, self.parent.grid_size)

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('MTF - Coupes')
        self.label_title.setStyleSheet(styleH1)

        # Axis selectors
        # --------------
        self.button_x_axis = QPushButton("Coupe horizontale")
        self.button_y_axis = QPushButton("Coupe verticale")
        self.button_x_axis.setStyleSheet(unactived_button)
        self.button_y_axis.setStyleSheet(unactived_button)
        self.button_x_axis.clicked.connect(self.button_x_axis_isClicked)
        self.button_y_axis.clicked.connect(self.button_y_axis_isClicked)

        self.sublayout = QHBoxLayout()
        self.sublayout.addWidget(self.button_x_axis)
        self.sublayout.addWidget(self.button_y_axis)

        # Legend
        # ------
        self.label_legend = QLabel('En orange: avec aberrations. En bleu, sans aberrations.')
        self.label_legend.setStyleSheet(styleH3)

        # MTF
        # ---
        self.mtf_display = MultiCurveChartWidget()
        self.mtf_display.set_background('white')

        self.mtf_display.set_y_label('MTF normalisée', unit=None)

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.sublayout)
        self.layout.addWidget(self.label_legend)
        self.layout.addWidget(self.mtf_display)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        self.Ne = self.mtf.shape[0]

        self.x_slice = self.mtf[self.Ne//2, :]
        self.y_slice = self.mtf[:, self.Ne//2]

        self.get_X_axis_array()

        self.parent.main_menu_widget.f_number_changed.connect(self.get_X_axis_array)

    def get_X_axis_array(self):
        cutoff_frequency = 1/(self.parent.WAVELENGTH*self.parent.f_number)
        px_mtf = cutoff_frequency * 2**(-self.parent.zoom) * 1e-6
        
        self.X = np.linspace(-self.Ne//2*px_mtf, self.Ne//2*px_mtf, self.Ne)
        self.button_x_axis_isClicked()

    def button_x_axis_isClicked(self):
        self.button_y_axis.setStyleSheet(unactived_button)
        self.button_x_axis.setStyleSheet(actived_button)

        self.mtf_display.clear_graph()

        self.mtf_display.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], self.x_slice[4*self.Ne//8: 5*self.Ne//8], ORANGE_IOGS, 2, 'MTF')
        self.mtf_display.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], self.theorical_mtf[self.Ne//2, :][4*self.Ne//8: 5*self.Ne//8], BLUE_IOGS, 1, 'Theoretical MTF')
        self.mtf_display.set_x_label('Y', unit='mm⁻¹')
        self.mtf_display.refresh_chart()

    def button_y_axis_isClicked(self):
        self.button_x_axis.setStyleSheet(unactived_button)
        self.button_y_axis.setStyleSheet(actived_button)

        self.mtf_display.clear_graph()

        self.mtf_display.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], self.y_slice[4*self.Ne//8: 5*self.Ne//8], ORANGE_IOGS, 2, 'MTF')
        self.mtf_display.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], self.theorical_mtf[:, self.Ne//2][4*self.Ne//8: 5*self.Ne//8], BLUE_IOGS, 1, 'Theoretical MTF')
        self.mtf_display.set_x_label('X', unit='mm⁻¹')
        self.mtf_display.refresh_chart()

class ModulationTransfertFunctionDefoc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

        if parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.wavefront
        self.defoc_max_delta_z = 1 # mm
        self.Ne = self.parent.grid_size

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('MTF - Défocalisation')
        self.label_title.setStyleSheet(styleH1)

        # Legend
        # ------
        self.label_legend = QLabel('Défocalisation de -1 mm à +1 mm.')
        self.label_legend.setStyleSheet(styleH2)
        self.lineedit_defoc = LineEditBloc('Maximum defoc (mm):', txt='1')
        self.lineedit_defoc.editing_finished_signal().connect(self.on_lineedit_defoc_change)
        self.button_big_defoc_delta_z = QPushButton(' Agrandir ')
        self.button_big_defoc_delta_z.clicked.connect(self.button_big_defoc_delta_z_isClicked)
        self.button_big_defoc_delta_z.setStyleSheet(unactived_button)
        self.sublayout_legend_defoc_delta_z = QHBoxLayout()
        self.sublayout_legend_defoc_delta_z.addWidget(self.label_legend)
        self.sublayout_legend_defoc_delta_z.addWidget(self.lineedit_defoc)
        self.sublayout_legend_defoc_delta_z.addStretch()
        self.sublayout_legend_defoc_delta_z.addWidget(self.button_big_defoc_delta_z)

        # Defoc. MTF | axe X
        # ------------------
        self.sublayout_defoc_X = QHBoxLayout()
        self.label_legend_X_axis = QLabel('Axe X')
        self.label_legend_X_axis.setStyleSheet(styleH2)
        self.label_legend_X_axis.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Defoc. MTF | axe Y
        # ------------------
        self.sublayout_defoc_Y = QHBoxLayout()
        self.label_legend_Y_axis = QLabel('Axe Y')
        self.label_legend_Y_axis.setStyleSheet(styleH2)
        self.label_legend_Y_axis.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.sublayout_legend_defoc_delta_z)
        self.layout.addWidget(self.label_legend_X_axis)
        self.layout.addLayout(self.sublayout_defoc_X, stretch=1)
        self.layout.addWidget(self.label_legend_Y_axis)
        self.layout.addLayout(self.sublayout_defoc_Y, stretch=1)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        self.action()
        self.parent.main_menu_widget.f_number_changed.connect(self.action)

    def action(self):
        self.clean_layout(self.sublayout_defoc_X)
        self.clean_layout(self.sublayout_defoc_Y)
        if self.parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.wavefront

        dim_y, dim_x = self.phase.shape
        x = np.linspace(-1, 1, dim_x)
        y = np.linspace(-1, 1, dim_y)
        x, y = np.meshgrid(x, y)
        r = np.sqrt(x**2+y**2)
        r[r>1] = 0

        cutoff_frequency = 1/(self.parent.WAVELENGTH*self.parent.f_number)
        px_mtf = cutoff_frequency * 2**(-self.parent.zoom) * 1e-6
        self.X = np.linspace(-self.Ne//2*px_mtf, self.Ne//2*px_mtf, self.Ne)

        conversion = self.defoc_max_delta_z * (1-np.cos(1/(2*self.parent.f_number))) / self.parent.WAVELENGTH
        self.mtf_defoc_delta_z_slice = []
        self.theorical_mtf_defoc_delta_z_slice = []

        for delta_z in [-1/2, -1/4, 0, 1/4, 1/2]:
            defoc = delta_z * np.sqrt(3)*(2*r**2-1) * conversion

            mtf = get_mtf(self.phase * np.exp(np.exp(2*I*PI*defoc)), self.parent.zoom, self.parent.grid_size)
            theorical_mtf = get_mtf(np.abs(self.phase) * np.exp(np.exp(2*I*PI*defoc)), self.parent.zoom, self.parent.grid_size)

            # X Axis
            # ------
            self.mtf_defoc_delta_z_slice.append(mtf[:, self.Ne//2])
            self.theorical_mtf_defoc_delta_z_slice.append(theorical_mtf[:, self.Ne//2])

            widget = MultiCurveChartWidget()
            widget.set_background('white')
            widget.set_y_label('MTF normalisée', unit=None)
            widget.set_x_label('X', unit='mm⁻¹')

            widget.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], mtf[:, self.Ne//2][4*self.Ne//8: 5*self.Ne//8], ORANGE_IOGS, 2, 'MTF')
            widget.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], theorical_mtf[:, self.Ne//2][4*self.Ne//8: 5*self.Ne//8], BLUE_IOGS, 1, 'MTF')
            self.sublayout_defoc_X.addWidget(widget)

            # Y Axis
            # ------
            self.mtf_defoc_delta_z_slice.append(mtf[self.Ne//2, :])
            self.theorical_mtf_defoc_delta_z_slice.append(theorical_mtf[self.Ne//2, :])

            widget = MultiCurveChartWidget()
            widget.set_background('white')
            widget.set_y_label('MTF normalisée', unit=None)
            widget.set_x_label('Y', unit='mm⁻¹')

            widget.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], mtf[self.Ne//2, :][4*self.Ne//8: 5*self.Ne//8], ORANGE_IOGS, 2, 'MTF')
            widget.add_curve(self.X[4*self.Ne//8: 5*self.Ne//8], theorical_mtf[self.Ne//2, :][4*self.Ne//8: 5*self.Ne//8], BLUE_IOGS, 1, 'MTF')
            self.sublayout_defoc_Y.addWidget(widget)

    def button_big_defoc_delta_z_isClicked(self):
        self.button_big_defoc_delta_z.setStyleSheet(actived_button)
        conversion = self.defoc_max_delta_z * (1-np.cos(1/(2*self.parent.f_number))) / self.parent.WAVELENGTH

        axis = ['X', 'X', 'X', 'X', 'X', 'Y', 'Y', 'Y', 'Y', 'Y']
        list_defoc = [-1/2, -1/4, 0, 1/4, 1/2, -1/2, -1/4, 0, 1/4, 1/2]

        cutoff_frequency = 1/(self.parent.WAVELENGTH*self.parent.f_number)
        px_mtf = cutoff_frequency * 2**(-self.parent.zoom) * 1e-6
        self.X = np.linspace(-self.Ne//2*px_mtf, self.Ne//2*px_mtf, self.Ne)

        plt.figure(figsize=(15, 9))
        plt.suptitle('En orange: avec aberrations. En bleu, sans aberrations.')
        for i in range(10):
            plt.subplot(2, 5, i+1)
            plt.plot(self.X[4*self.Ne//8: 5*self.Ne//8], self.mtf_defoc_delta_z_slice[i][4*self.Ne//8: 5*self.Ne//8], color=ORANGE_IOGS, lw=2)
            plt.plot(self.X[4*self.Ne//8: 5*self.Ne//8], self.theorical_mtf_defoc_delta_z_slice[i][4*self.Ne//8: 5*self.Ne//8], color=BLUE_IOGS, lw=1, alpha=.5)
            plt.xlabel(f"{axis[i]} (mm⁻¹)")
            plt.ylabel('MTF normalisée')
            plt.title(f"Écart normal de {list_defoc[i]*conversion:.1f} mm")
        # plt.tight_layout
        plt.show()

        self.button_big_defoc_delta_z.setStyleSheet(unactived_button)

    def on_lineedit_defoc_change(self):
        self.defoc_max_delta_z = float(self.lineedit_defoc.text())
        self.label_legend.setText(f"Défocalisation de -{self.defoc_max_delta_z} mm à +{self.defoc_max_delta_z} mm.")

        self.action()

    def clean_layout(self, layout):
        print(f"CLEAN LAYOUT - {layout}")
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Define Window title
            self.setWindowTitle(translate("Zygo-IDS Labwork APP"))
            self.setWindowIcon(QIcon('assets\IOGS-LEnsE-icon.jpg'))
            self.setGeometry(50, 50, 500, 500)

            self.widget = QWidget()
            self.layout = QGridLayout()

            self.display = ModulationTransfertFunctionDisplay()
            mtf = self.display.update_mtf()
            self.slice = ModulationTransfertFunctionSlice(mtf)
            self.layout.addWidget(self.display, 1, 1)
            self.layout.addWidget(self.slice,1 ,2)
            self.widget.setLayout(self.layout)
            self.setCentralWidget(self.widget)

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