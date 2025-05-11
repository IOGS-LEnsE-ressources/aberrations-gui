# -*- coding: utf-8 -*-
"""*display_zernike_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)

import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from lensepy import translate
import process.graphe as g
from lensepy.css import *

if __name__ == '__main__':
    from table_from_numpy import TableFromNumpy
else:
    from widgets.table_from_numpy import TableFromNumpy

PDF_PATH = os.path.join("assets", "Niu_2022_J._Opt._24_123001-10.pdf")

styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

BUTTON_HEIGHT = 30 # px
COEFFICIENTS_ROUND_RANGE = 4 # decimals

class ZernikeDisplayWidget(QWidget):
    def __init__(self, coeffs):
        super().__init__(parent=None)

        self.coeffs = coeffs

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        self.label_title_results = QLabel("Coefficients de Zernike")
        self.label_title_results.setStyleSheet(styleH1)

        # Label
        self.label = QLabel('Les coefficients sont donnés en λ.')
        self.label.setStyleSheet(styleH3)

        # Table
        array = coeffs[1:].reshape(4, 9)
        array = np.round(array, COEFFICIENTS_ROUND_RANGE)
        labels = np.array(['C1-C9', 'C10-C18', 'C19-C27', 'C28-C36']).reshape(4, 1)
        final_array = np.hstack((labels, array))
        self.table_results = TableFromNumpy(final_array)

        # Display graph button
        self.button_show_graph = QPushButton('Afficher le graphique')
        self.button_show_graph.setStyleSheet(unactived_button)
        self.button_show_graph.setFixedHeight(BUTTON_HEIGHT)
        self.button_show_graph.clicked.connect(self.show_graph)

        # PDF button
        self.button_pdf = QPushButton('Signification des coefficients')
        self.button_pdf.setStyleSheet(unactived_button)
        self.button_pdf.setFixedHeight(BUTTON_HEIGHT)
        self.button_pdf.clicked.connect(self.open_pdf_file)

        # Add widgets to the layout
        self.layout.addWidget(self.label_title_results)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.table_results)
        # self.layout.addWidget(self.button_show_graph)
        self.layout.addWidget(self.button_pdf)
        self.layout.addStretch()

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def show_graph(self):
        self.button_show_graph.setStyleSheet(actived_button)

        fig, ax = g.new_plot(fig_output=True)
        fig.set_size_inches(15, 8)
        ax = g.lin_XY(ax, title='', x_label=r'OSA index $i$', x_unit='', y_label=r'$C_i$', y_unit=r'en $\lambda$', axis_intersect=(-.5, 0))
        ax.set_xticks(list(range(len(self.coeffs))))
        ax.bar(list(range(len(self.coeffs))), self.coeffs, color=ORANGE_IOGS)
        
        plt.show()
        self.button_show_graph.setStyleSheet(unactived_button)

    def open_pdf_file(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(PDF_PATH))

class SeidelDisplayWidget(QWidget):
    def __init__(self, coeffs):
        super().__init__(parent=None)

        self.coeffs = coeffs

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        self.label_title_results = QLabel("Coefficients de Seidel")
        self.label_title_results.setStyleSheet(styleH1)

        # Label
        self.label = QLabel('Les coefficients sont donnés en λ.')
        self.label.setStyleSheet(styleH3)

        # Table
        array = self.convert_zernike_seidel()
        self.table_results = TableFromNumpy(array)

        # Add widgets to the layout
        self.layout.addWidget(self.label_title_results)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.table_results)
        self.layout.addStretch()

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def convert_zernike_seidel(self):
        """
        Dans les conventions actuelles, on a:

        Aberration  | Amplitude     | Angle
        ---------------------------------------------------
        Tilt        | √(C3²+C2²)    | arctan(C3/C2)
        Defocus     | 2*C4          |    no
        Astigmatism | √(C5²+C6²)    | 1/2 * arctan(C6/C5)
        Coma        | 3*√(C8²+C7²)  | arctan(C8/C7)
        Sph. Ab.    | 6*C11         |    no
        """
        c = self.coeffs

        # Tilt
        # ----
        tilt_magnitude = np.sqrt(c[3]**2 + c[2]**2)
        tilt_angle = np.rad2deg(np.arctan2(c[3], c[2]))

        # Defocus
        # -------
        defocus_amplitude = 2*c[4]

        # Astigmatism
        # -----------
        astigmatism_magnitude = 2 * np.sqrt(c[6]**2+c[5]**2)
        astigmatism_angle = np.rad2deg(1/2* np.arctan2(c[6], c[5]))

        # Coma
        # ----
        coma_amplitude = 3 * np.sqrt(c[7]**2+c[8]**2)
        coma_angle = np.rad2deg(np.arctan2(c[8], c[7]))

        # Spherical aberration
        # --------------------
        sp_ab_magnitude = 6*c[11]

        # Round
        # -----
        tilt_magnitude = np.round(tilt_magnitude, COEFFICIENTS_ROUND_RANGE)
        tilt_angle = np.round(tilt_angle, COEFFICIENTS_ROUND_RANGE)
        defocus_amplitude = np.round(defocus_amplitude, COEFFICIENTS_ROUND_RANGE)
        astigmatism_magnitude = np.round(astigmatism_magnitude, COEFFICIENTS_ROUND_RANGE)
        astigmatism_angle = np.round(astigmatism_angle, COEFFICIENTS_ROUND_RANGE)
        coma_amplitude = np.round(coma_amplitude, COEFFICIENTS_ROUND_RANGE)
        coma_angle = np.round(coma_angle, COEFFICIENTS_ROUND_RANGE)
        sp_ab_magnitude = np.round(sp_ab_magnitude, COEFFICIENTS_ROUND_RANGE)

        # Array
        # -----
        arr = np.array([
            ['',            'Tilt',         'Defocus',          'Astigmatism',          'Coma',         'Sph. Ab'       ],
            ['Amplitude',   tilt_magnitude, defocus_amplitude,  astigmatism_magnitude,  coma_amplitude, sp_ab_magnitude ],
            ['Angle',       tilt_angle, '∅',  astigmatism_angle,  coma_angle, '∅' ]
        ])
        return arr

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(translate("Coefficients de Zernike"))
        self.setGeometry(300, 300, 500, 500)

        # Exemple de coefficients aléatoires pour les tests
        random_coeffs = 2 * np.random.rand(37) - 1

        self.central_widget = SeidelDisplayWidget(random_coeffs)
        self.setCentralWidget(self.central_widget)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quitter', 'Voulez-vous vraiment quitter ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
