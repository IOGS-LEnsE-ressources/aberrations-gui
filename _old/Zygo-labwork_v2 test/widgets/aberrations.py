# -*- coding: utf-8 -*-
"""*aberrations.py* file.

This file contains graphical elements to manage aberrations correction.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : feb/2025
"""

import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import *
from lensepy.images.conversion import *
from lensepy.pyqt6 import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

if __name__ == '__main__':
    sys.path.insert(0, '../process')
    from zernike_coefficients import *
else:
    from process.zernike_coefficients import *


COEFFICIENTS_ROUND_RANGE = 4 # decimals


def convert_zernike_seidel(coeffs):
        """
        Process Seidel coefficients from Zernike coefficients.

        Actual convention:

        Aberration  | Amplitude     | Angle
        ---------------------------------------------------
        Tilt        | √(C3²+C2²)    | arctan(C3/C2)
        Defocus     | 2*C4          |    no
        Astigmatism | √(C5²+C6²)    | 1/2 * arctan(C6/C5)
        Coma        | 3*√(C8²+C7²)  | arctan(C8/C7)
        Sph. Ab.    | 6*C11         |    no
        """
        c = coeffs

        # Tilt
        # ----
        tilt_magnitude = np.sqrt(coeffs[3]**2 + c[2]**2)
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
  
# %% Axes modifiers
def lin_XY(ax, title='', x_label='', x_unit='', y_label='', y_unit='', axis_intersect=(0, 0)):
    """
    Set the style of a plot to a plot with linear axis.

    Parameters
    ----------
    ax : matplotlib.Axis
        The axis we want to modify.
    title : str, optional
        The title of the plot.
        LaTeX writing is available.
        The default is ''.
    x_label : str, optional
        The label of the X axis.
        LaTeX writing is available.
        The default is ''.
    x_unit : str, optional
        The unit of the X axis.
        LaTeX writing is available.
        The default is ''.
    y_label : str, optional
        The label of the Y axis.
        LaTeX writing is available.
        The default is ''.
    y_unit : str, optional
        The unit of the Y axis.
        LaTeX writing is available.
        The default is ''.
    axis_intersect : tuple, optional
        The coordinates of the intersection point between X and Y.
        The default is (0, 0).

    Returns
    -------
    ax : matplotlib.Axis
        The axis modified.

    """
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines[['right', 'top']].set_color('none')

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    if x_unit == '':
        ax.set_xlabel(r"{}".format(x_label), loc='right')
    else:
        ax.set_xlabel(r"{} ({})".format(x_label, x_unit), loc='right')
    if y_unit == '':
        ax.set_ylabel(r"{}".format(y_label), loc='top')
    else:
        ax.set_ylabel(r"{} ({})".format(y_label, y_unit), loc='top')

    x0, y0 = axis_intersect
    ax.spines['left'].set_position(['data', x0])
    ax.spines['bottom'].set_position(['data', y0])

    ax.set_title(title)
    return ax


class AberrationsOptionsWidget(QWidget):
    """Aberrations Options."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.coeffs = self.parent.parent.zernike.coeff_list
        if not isinstance(self.coeffs, np.ndarray):
            self.coeffs = np.array(self.coeffs)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Title
        self.label_aberrations_title = QLabel(translate("label_aberrations_title"))
        self.label_aberrations_title.setStyleSheet(styleH1)
        self.label_aberrations_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_Zernike_table(self):
        # Table 
        self.zernike_table = AberrationsTableWidget(self)
        # Add graphical elements to the layout
        self.layout.addWidget(self.label_aberrations_title)
        self.layout.addWidget(self.zernike_table)

    def show_Seidel_table(self):
        # Table 
        self.seidel_table = SeidelTableWidget(self)
        # Add graphical elements to the layout
        self.layout.addWidget(self.label_aberrations_title)
        self.layout.addWidget(self.seidel_table)


    def show_graph(self):
        if not(None in self.coeffs) and len(self.coeffs) > 0:
            fig,ax=plt.subplots(1,1)
            fig.set_size_inches(15, 8)
            ax = lin_XY(ax, title='', x_label=r'OSA index $i$', x_unit='', y_label=r'$C_i$', y_unit=r'en $\lambda$', axis_intersect=(-.5, 0))
            ax.set_xticks(list(range(1,len(self.coeffs))))
            ax.bar(list(range(1,len(self.coeffs))), self.coeffs[1:], color=ORANGE_IOGS)
            canvas = FigureCanvas(fig)
            self.layout.addWidget(canvas)  
        else:
            print(self.coeffs)
            print(len(self.coeffs))
            print("Error: self.coeffs contains a None element")
    

class AberrationsChoiceWidget(QWidget):
    """Aberrations Choice for selecting aberrations to compensate."""

    aberrations_choice_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        # Data
        self.check_boxes = []
        self.signal_list = []
        self.aberrations_list = []
        # Graphical objects
        self.max_cols = 6
        self.max_rows = 6
        self.layout = QGridLayout()
        for k in range(self.max_cols):
            self.layout.setColumnStretch(k, 1)
        for k in range(self.max_rows):
            self.layout.setRowStretch(k, 1)
        self.setLayout(self.layout)
        self.load_file('./config/aberrations_choice.txt')

    def load_file(self, file_path: str):
        """
        Load choice from a txt file.
        Each line of the file contains :
        Name; Row; Col; List_of_orders; Global; type;
        Commentary lines start with #
        """
        if os.path.exists(file_path):
            # Read the CSV file, ignoring lines starting with '//'
            data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
            # Populate the dictionary with key-value pairs from the CSV file
            for ab_name, ab_row, ab_col, ab_orders, ab_global, ab_type, _ in data:
                if ab_global == 'Y':
                    check = QCheckBox(translate(ab_name))
                    check.stateChanged.connect(self.action_checked)
                    self.check_boxes.append(check)
                    self.signal_list.append(str(ab_type))
                    self.layout.addWidget(check, int(ab_row), int(ab_col), 2, 1)
                else:
                    label = QLabel(translate(ab_name))
                    self.layout.addWidget(label, int(ab_row), int(ab_col), 2, 1)
                    orders = ab_orders.split(',')
                    col_counter = 2
                    for order in orders:
                        if order != '':
                            check_signal = ab_type + order
                            check = QCheckBox(order)
                            check.stateChanged.connect(self.action_checked)
                            self.check_boxes.append(check)
                            self.signal_list.append(check_signal)
                            self.layout.addWidget(check, int(ab_row), col_counter)
                        col_counter += 1
        else:
            print('CHOICE File error')

    def action_checked(self):
        self.aberrations_list = []
        for i, check in enumerate(self.check_boxes):
            if check.isChecked():
                self.aberrations_list.append(self.signal_list[i])
        self.aberrations_choice_changed.emit('choice_changed')

'''
class CorrectionTable(QTableWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.parent = parent

        # Set the corrected coeffs
        self.corrected_coeffs=np.zeros_like(self.parent.coeffs)
        # Set the window title and size

        self.setGeometry(100, 100, 600, 400)
        self.setMinimumSize(100, 100)

        # Create the table widget
        self.list=aberrations_list
        self.dict=aberrations_type
        # Set the number of rows and columns
        self.setRowCount(len(self.list)//2+1)  # 11 rows
        self.setColumnCount(4)  # 4 columns

        # Set the header labels
        self.setHorizontalHeaderLabels(["Aberration", "Correction","Aberration","Correction"])

        # Set checkbox list
        self.checkbox_list = []

        # Populate the table with names and checkboxes
        for row in range(len(self.list)//2+1):
            name_item = QTableWidgetItem(self.list[2*row])
            self.setItem(row, 0, name_item)  # Set name in the first column

            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(self.correction_checkbox_changed)
            self.checkbox_list.append(checkbox)
            self.setCellWidget(row, 1, checkbox)  # Set checkbox in the second column
            if not(row==(len(self.list)//2)):
                name_item = QTableWidgetItem(self.list[2*row+1])
                self.setItem(row, 2, name_item)  # Set name in the first column

                checkbox = QCheckBox()
                checkbox.setChecked(False)
                checkbox.stateChanged.connect(self.correction_checkbox_changed)
                self.checkbox_list.append(checkbox)
                self.setCellWidget(row, 3, checkbox)  # Set checkbox in the second column


        self.resizeColumnsToContents()


    def correction_checkbox_changed(self):
        checkbox=self.sender()
        if checkbox.isChecked():
            aberr=self.list[self.checkbox_list.index(checkbox)]
            if len(self.dict[aberr]) == 1:
                self.corrected_coeffs[self.dict[aberr][0]]=self.parent.coeffs[self.dict[aberr][0]]
            else: #2 self.dict[aberr] elemnts 
                self.corrected_coeffs[self.dict[aberr][0]]=self.parent.coeffs[self.dict[aberr][0]]
                self.corrected_coeffs[self.dict[aberr][1]]=self.parent.coeffs[self.dict[aberr][1]]
        else:
            aberr=self.list[self.checkbox_list.index(checkbox)]
            if len(self.dict[aberr]) == 1:
                self.corrected_coeffs[self.dict[aberr][0]]=0
            else: #2 self.dict[aberr] elemnts 
                self.corrected_coeffs[self.dict[aberr][0]]=0
                self.corrected_coeffs[self.dict[aberr][1]]=0
        _, new_surface = self.parent.parent.parent.zernike.phase_correction(self.corrected_coeffs)
        self.parent.parent.display_3D_adjusted_phase(new_surface)
'''

class SeidelTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.parent=parent

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
        array = convert_zernike_seidel(self.parent.parent.parent.zernike.coeff_list)
        self.table_results = TableFromNumpy(array)

        # Add widgets to the layout
        self.layout.addWidget(self.label_title_results)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.table_results)
        self.layout.addStretch()

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        
class AberrationsTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.parent=parent
        self.coeffs=self.parent.parent.parent.zernike.coeff_list
        if not isinstance(self.coeffs, np.ndarray):
            self.coeffs = np.array(self.coeffs)

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
        array = self.coeffs[1:].reshape(4, 9)
        array = np.round(array, COEFFICIENTS_ROUND_RANGE)
        labels = np.array(['C1-C9', 'C10-C18', 'C19-C27', 'C28-C36']).reshape(4, 1)
        final_array = np.hstack((labels, array))
        self.table_results = TableFromNumpy(final_array)
        # Add widgets to the layout
        self.layout.addWidget(self.label_title_results)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.table_results)

        self.layout.addStretch()

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)




if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = AberrationsChoiceWidget(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
    
