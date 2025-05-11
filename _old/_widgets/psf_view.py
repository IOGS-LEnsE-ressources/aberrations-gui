# -*- coding: utf-8 -*-
"""*psf_view.py* file.

*psf_view* file that contains :class::AnalysisApp

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
    from imshow_pyqtgraph import ImageWidget
    from x_y_chart_widget import *
else:
    from widgets.lineedit_bloc import LineEditBloc
    from widgets.imshow_pyqtgraph import ImageWidget
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

# PSF Display
# ===========
class PointSpreadFunctionDisplay(QWidget):
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
        self.label_title = QLabel('PSF - Niveaux de gris')
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

        # PSF
        # ---
        self.psf_display = ImageWidget()

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.sublayout)
        self.layout.addWidget(self.psf_display)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def on_grid_size_change(self):
        self.grid_size = int(self.lineedit_grid_size.text())
        self.update_psf()

    def on_zoom_change(self):
        self.zoom = float(self.lineedit_zoom.text())
        self.update_psf()

    def update_psf(self):
        psf = get_psf(self.phase, self.zoom, self.grid_size)
        #psf = get_psf(self.phase, 4, 1024)

        psf_for_display = thresholed_log(psf)
        psf_for_display -= psf_for_display.min()
        psf_for_display /= psf_for_display.max()
        self.psf_display.set_image_data(psf_for_display, 'gray')
        return psf

# PSF Slice
# ===========
class PointSpreadFunctionSlice(QWidget):
    def __init__(self, psf, parent=None):
        super().__init__(parent=None)

        self.parent = parent
        self.psf = psf

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('PSF - Coupes')
        self.label_title.setStyleSheet(styleH1)

        # Strehl ratio
        # ------------
        self.label_strehl_ratio_name = QLabel('Rapport de Strehl:')
        self.label_strehl_ratio_name.setStyleSheet(styleH2)
        self.label_strehl_ratio_value = QLabel(f"{100*psf.max():.2f} %")
        self.label_strehl_ratio_value.setStyleSheet(styleH3)
        self.strehl_sublayout = QHBoxLayout()
        self.strehl_sublayout.addWidget(self.label_strehl_ratio_name)
        self.strehl_sublayout.addWidget(self.label_strehl_ratio_value)
        self.strehl_sublayout.addStretch()

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

        # PSF
        # ---
        self.psf_display = XYChartWidget()
        self.psf_display.set_background('white')

        self.psf_display.set_y_label('PSF normalisée', unit=None)

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.strehl_sublayout)
        self.layout.addLayout(self.sublayout)
        self.layout.addWidget(self.psf_display)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        self.Ne = self.psf.shape[0]

        self.x_slice = self.psf[self.Ne//2, :]
        self.y_slice = self.psf[:, self.Ne//2]

        self.get_X_axis_array()

        self.parent.main_menu_widget.f_number_changed.connect(self.get_X_axis_array)

    def get_X_axis_array(self):
        px_psf = (self.parent.WAVELENGTH*self.parent.f_number)*2**(-self.parent.zoom)
        self.X = np.linspace(-self.Ne//2*px_psf, self.Ne//2*px_psf, self.Ne)
        self.psf_display.clear_graph()
        self.button_x_axis_isClicked()

    def button_x_axis_isClicked(self):
        self.button_y_axis.setStyleSheet(unactived_button)
        self.button_x_axis.setStyleSheet(actived_button)

        self.psf_display.set_data(self.X[3*self.Ne//8: 5*self.Ne//8], self.x_slice[3*self.Ne//8: 5*self.Ne//8])
        self.psf_display.set_x_label('Y', unit='m')
        self.psf_display.refresh_chart()

    def button_y_axis_isClicked(self):
        self.button_x_axis.setStyleSheet(unactived_button)
        self.button_y_axis.setStyleSheet(actived_button)

        self.psf_display.set_data(self.X[3*self.Ne//8: 5*self.Ne//8], self.y_slice[3*self.Ne//8: 5*self.Ne//8])
        self.psf_display.set_x_label('X', unit='m')
        self.psf_display.refresh_chart()

# Circled energy
# ==============
class PointSpreadFunctionCircledEnergy(QWidget):
    def __init__(self, psf, parent=None):
        super().__init__(parent=None)

        self.parent = parent
        self.psf = psf

        if parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.wavefront

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('PSF - Énergie encerclée')
        self.label_title.setStyleSheet(styleH1)

        # Legend
        # ------
        self.label_legend = QLabel('En orange: avec aberrations. En bleu, sans aberrations.')
        self.label_legend.setStyleSheet(styleH3)

        # Circled energy
        # --------------
        self.psf_display = MultiCurveChartWidget()
        self.psf_display.set_background('white')
        self.psf_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.label_title)
        self.layout.addWidget(self.label_legend)
        self.layout.addWidget(self.psf_display, stretch=1)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)
        
        self.action()

        self.parent.main_menu_widget.f_number_changed.connect(self.action)

    def action(self):
        self.psf_display.clear_graph()

        self.Ne = self.psf.shape[0]

        self.x_slice = self.psf[self.Ne//2, :]
        self.y_slice = self.psf[:, self.Ne//2]

        x_centroid, y_centroid = calculate_centroid(self.psf)

        y_dim, x_dim = self.psf.shape
        x = np.arange(x_dim)
        y = np.arange(y_dim)
        X, Y = np.meshgrid(x, y)

        _X = X - x_centroid * np.ones_like(X)
        _Y = Y - y_centroid * np.ones_like(Y)
        R = np.sqrt(_X**2 + _Y**2)

        psf = get_psf(self.phase, self.parent.zoom, self.parent.grid_size)
        theorical_psf = get_psf(np.abs(self.phase), self.parent.zoom, self.parent.grid_size)

        psf /= psf.max()
        theorical_psf /= theorical_psf.max()

        circled_energy = np.array([np.sum(psf[R<ray]) for ray in range(x_dim//8)])/np.sum(psf)
        theorical_circled_energy = np.array([np.sum(theorical_psf[R<ray]) for ray in range(x_dim//8)])/np.sum(theorical_psf)

        px_psf = (self.parent.WAVELENGTH*self.parent.f_number)*2**(-self.parent.zoom)
        r = np.linspace(0, x_dim/8*px_psf, x_dim//8)

        self.psf_display.add_curve(r, circled_energy, ORANGE_IOGS, 2, 'Circled Energy')
        self.psf_display.add_curve(r, theorical_circled_energy, BLUE_IOGS, 1, 'Theoretical Circled Energy')
        self.psf_display.set_x_label('Rayon', unit='m')
        self.psf_display.set_y_label('Énergie encerclée normalisée')
        self.psf_display.refresh_chart()

class PointSpreadFunctionDefoc(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

        if parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.wavefront
        self.defoc_max_delta_z = 1 # mm

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('PSF - Défocalisation')
        self.label_title.setStyleSheet(styleH1)

        # Legend 1
        # --------
        self.label_legend1 = QLabel('Défocalisation de -λ/2 à λ/2.')
        self.label_legend1.setStyleSheet(styleH2)
        self.button_big_defoc_lambda = QPushButton(' Agrandir ')
        self.button_big_defoc_lambda.setStyleSheet(unactived_button)
        self.button_big_defoc_lambda.clicked.connect(self.button_big_defoc_lambda_isClicked)
        self.sublayout_legend_defoc_lambda = QHBoxLayout()
        self.sublayout_legend_defoc_lambda.addWidget(self.label_legend1)
        self.sublayout_legend_defoc_lambda.addStretch()
        self.sublayout_legend_defoc_lambda.addWidget(self.button_big_defoc_lambda)

        # Defoc. PSF | lambda
        # -------------------
        self.sublayout_defoc_lambda = QHBoxLayout()

        # Legend 2
        # --------
        self.label_legend2 = QLabel('Défocalisation de -1 mm à +1 mm.')
        self.label_legend2.setStyleSheet(styleH2)
        self.lineedit_defoc = LineEditBloc('Maximum defoc (mm):', txt='1')
        self.lineedit_defoc.editing_finished_signal().connect(self.on_lineedit_defoc_change)
        self.button_big_defoc_delta_z = QPushButton(' Agrandir ')
        self.button_big_defoc_delta_z.clicked.connect(self.button_big_defoc_delta_z_isClicked)
        self.button_big_defoc_delta_z.setStyleSheet(unactived_button)
        self.sublayout_legend_defoc_delta_z = QHBoxLayout()
        self.sublayout_legend_defoc_delta_z.addWidget(self.label_legend2)
        self.sublayout_legend_defoc_delta_z.addWidget(self.lineedit_defoc)
        self.sublayout_legend_defoc_delta_z.addStretch()
        self.sublayout_legend_defoc_delta_z.addWidget(self.button_big_defoc_delta_z)

        # Defoc. PSF | delta Z
        # --------------------
        self.sublayout_defoc_delta_z = QHBoxLayout()

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.sublayout_legend_defoc_lambda)
        self.layout.addLayout(self.sublayout_defoc_lambda, stretch=1)
        self.layout.addLayout(self.sublayout_legend_defoc_delta_z)
        self.layout.addLayout(self.sublayout_defoc_delta_z, stretch=1)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        self.action()
        self.parent.main_menu_widget.f_number_changed.connect(self.action)

    def action(self):
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

        self.psf_defoc_lambda = []
        for delta_lambda in [-1/2, -1/4, 0, 1/4, 1/2]:
            defoc = delta_lambda * np.sqrt(3)*(2*r**2-1)

            psf = get_psf(self.phase * np.exp(np.exp(2*I*PI*defoc)), self.parent.zoom, self.parent.grid_size)
            psf_for_display = thresholed_log(psf)
            psf_for_display = psf_for_display[psf.shape[0]//4:3*psf.shape[0]//4, psf.shape[0]//4:3*psf.shape[0]//4]
            psf_for_display -= psf_for_display.min()
            psf_for_display /= psf_for_display.max()
            self.psf_defoc_lambda.append(psf_for_display)

            widget = ImageWidget()
            widget.set_image_data(psf_for_display, 'gray')
            self.sublayout_defoc_lambda.addWidget(widget)

        conversion = self.defoc_max_delta_z * (1-np.cos(1/(2*self.parent.f_number))) / self.parent.WAVELENGTH
        self.psf_defoc_delta_z = []
        for delta_lambda in [-1/2, -1/4, 0, 1/4, 1/2]:
            print('ok')
            defoc = delta_lambda * np.sqrt(3)*(2*r**2-1) * conversion

            psf = get_psf(self.phase * np.exp(np.exp(2*I*PI*defoc)), self.parent.zoom, self.parent.grid_size)
            psf_for_display = thresholed_log(psf)
            psf_for_display = psf_for_display[psf.shape[0]//4:3*psf.shape[0]//4, psf.shape[0]//4:3*psf.shape[0]//4]
            psf_for_display -= psf_for_display.min()
            psf_for_display /= psf_for_display.max()
            self.psf_defoc_delta_z.append(psf_for_display)

            widget = ImageWidget()
            widget.set_image_data(psf_for_display, 'gray')
            self.sublayout_defoc_delta_z.addWidget(widget)

    def button_big_defoc_lambda_isClicked(self):
        self.button_big_defoc_lambda.setStyleSheet(actived_button)

        list_defoc = [-1/2, -1/4, 0, 1/4, 1/2]

        plt.figure(figsize=(15, 10))
        for i in range(5):
            plt.subplot(2, 3, i+1)
            plt.imshow(self.psf_defoc_lambda[i], 'gray')
            plt.title(f"Défoc. de {list_defoc[i]}"+r"$\lambda$")
            plt.axis('off')
        plt.show()

        self.button_big_defoc_lambda.setStyleSheet(unactived_button)

    def button_big_defoc_delta_z_isClicked(self):
        self.button_big_defoc_delta_z.setStyleSheet(actived_button)

        list_defoc = [-1/2, -1/4, 0, 1/4, 1/2]
        conversion = self.defoc_max_delta_z * (1-np.cos(1/(2*self.parent.f_number))) / self.parent.WAVELENGTH

        plt.figure(figsize=(15, 10))
        for i in range(5):
            plt.subplot(2, 3, i+1)
            plt.imshow(self.psf_defoc_delta_z[i], 'gray')
            plt.title(f"Écart normal de {list_defoc[i]*conversion:.1f} mm")
            plt.axis('off')
        plt.show()

        self.button_big_defoc_delta_z.setStyleSheet(unactived_button)

    def on_lineedit_defoc_change(self):
        self.defoc_max_delta_z = float(self.lineedit_defoc.text())
        self.label_legend2.setText(f"Défocalisation de -{self.defoc_max_delta_z} mm à +{self.defoc_max_delta_z} mm.")
        
        self.clean_layout(self.sublayout_defoc_lambda)
        self.clean_layout(self.sublayout_defoc_delta_z)

        self.action()

    def clean_layout(self, layout):
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

            self.display = PointSpreadFunctionDisplay()
            psf = self.display.update_psf()
            self.slice = PointSpreadFunctionSlice(psf)
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