# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys

import cv2
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np

if __name__ == '__main__':
    from x_y_chart_widget import XYChartWidget
else:
    from widgets.x_y_chart_widget import XYChartWidget

from process.initialization_parameters import *

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.images.conversion import array_to_qimage, resize_image_ratio

import nidaqmx
import time

PI = np.pi

# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30  # px

local_system = nidaqmx.system.System.local()
driver_version = local_system.driver_version

# %% Widget
class PiezoCalibrationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

        # Layout
        # ------
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Master
        # ------
        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_calibration_menu = QLabel(translate('Calibration'))
        self.label_title_calibration_menu.setStyleSheet(styleH1)

        # Explanation
        # -----------
        self.label_explanation = QLabel("Montez le miroir plan et formez une teinte plate.\nVeillez à ce que rien ne perturbe le système de franges.")
        self.label_explanation.setStyleSheet(styleH3)

        # Graph
        # -----
        self.graph_calibration = XYChartWidget()
        self.graph_calibration.set_background('white')
        self.graph_calibration.set_x_label('Voltage (V)')
        self.graph_calibration.set_y_label('Phase (°)')
        self.graph_calibration.refresh_chart()

        # Button
        # ------
        self.button_start_calibration = QPushButton(translate('Start calibration'))
        self.button_start_calibration.setStyleSheet(unactived_button)
        self.button_start_calibration.clicked.connect(self.button_start_calibration_isClicked)

        # Label progression
        # -----------------
        self.label_progression = QLabel('')
        self.label_progression.setStyleSheet(styleH3)

        # Add widgets to the main layout
        self.layout.addWidget(self.label_title_calibration_menu)
        self.layout.addWidget(self.label_explanation)
        self.layout.addWidget(self.graph_calibration)
        self.layout.addWidget(self.button_start_calibration)
        self.layout.addWidget(self.label_progression)

        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def button_start_calibration_isClicked(self):
        self.button_start_calibration.setStyleSheet(actived_button)
        image_for_all_voltages = []
        number_measures = 1

        start_voltage = 0  # Tension de départ en volts
        end_voltage = 5 # Tension finale en volts
        num_steps = 100  # Nombre de pas dans la rampe

        print("============================= START CALIBRATION ===================================")

        # Stop thread

        self.parent.camera_thread.stop()
        self.parent.camera.init_camera()
        self.parent.camera.alloc_memory()
        self.parent.camera.start_acquisition()

        # Calcul des paramètres de la rampe
        ramp = np.linspace(start_voltage, end_voltage, num_steps)
        step_val = ramp[1] - ramp[0]

        # Créer une tâche pour générer la rampe de tension
        with nidaqmx.Task() as task:
            # Ajouter un canal de sortie analogique
            task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=start_voltage, max_val=end_voltage)

            # Démarrer la tâche
            task.start()

            import matplotlib.pyplot as plt

            n, m, p = (self.parent.camera_widget.camera.get_image().copy()).shape

            x_moy, y_moy = n // 2, m//2
            delta_x, delta_y = n // 16 , m // 16

            x_min, x_max = x_moy-delta_x, x_moy+delta_x
            y_min, y_max = y_moy-delta_y, y_moy+delta_y
            average_for_all_voltages = []

            # Générer la rampe de tension en écrivant chaque valeur successivement
            for i in range(number_measures):
                image_for_all_voltages = []
                for j,voltage in enumerate(ramp):
                    # Affichage debug
                    self.label_progression.setText(f"{i + 1}e mesure / {number_measures} mesures | Voltage = {voltage:.2f} V /{end_voltage:.2f} V")
                    self.label_progression.repaint()

                    task.write(voltage)
                    time.sleep(0.2)

                    raw_array = self.parent.camera_widget.camera.get_image().copy()[x_min:x_max, y_min:y_max]/number_measures
                    image_for_all_voltages.append(raw_array)
                average_for_all_voltages.append(image_for_all_voltages)
            average_for_all_voltages = np.mean(np.array(average_for_all_voltages), axis=0)

            average_for_all_voltages = np.squeeze(np.array(average_for_all_voltages))
            phi = np.array(list(map(lambda img:img-average_for_all_voltages[0], average_for_all_voltages)))

            print(f"Il y a au moins un NaN dans 'phi' ? {np.isnan(phi).any()}")
            print(f"Le maxilum est nul ? {(np.nanmax(phi[1:20], axis=0) == 0).any()}")

            plt.figure()
            plt.title('phi[10]')
            plt.imshow(phi[10])
            plt.colorbar()
            plt.show()

            phase = np.nanmean(np.nanmean(phi, axis=2), axis=1)
            phase -= (np.nanmax(phase) + np.nanmin(phase))/2
            phase /= (np.nanmax(phase) - np.nanmin(phase))/2

            fig, ax1 = plt.subplots()
            ax1.plot(phase)

            phase = np.rad2deg(np.arcsin(phase))

            ax2 = ax1.twinx()
            ax2.plot(phase, c='r')
            #phase = np.mean(np.mean(phi, axis=2), axis=1)
            print(phase.shape)
            plt.show()

            diff_phase = np.abs(np.diff(phase, prepend=0))
            
            #phase[0] = 0
            for i in range(1, len(phase)):
                phase[i] = phase[i-1] + diff_phase[i]#/step_val

            # phase *= 2
            phase -= phase[num_steps//5]

            task.write(0)

            ## Arrêter la tâche
            task.stop()

        self.parent.camera.stop_acquisition()
        self.parent.camera.free_memory()
        self.parent.camera_thread.start()

        self.graph_calibration.clear_graph()
        self.graph_calibration.set_data(ramp, phase)
        self.graph_calibration.refresh_chart()

        self.button_start_calibration.setStyleSheet(unactived_button)

        print(ramp.shape)

        eps = 5 # °
        V_1 = np.round(np.nanmean(ramp[(phase >= 0 - eps) & (phase <= 0 + eps)]), 3)
        V_2 = np.round(np.nanmean(ramp[(phase >= 90 - eps) & (phase <= 90 + eps)]), 3)
        V_3 = np.round(np.nanmean(ramp[(phase >= 180 - eps) & (phase <= 180 + eps)]), 3)
        V_4 = np.round(np.nanmean(ramp[(phase >= 270 - eps) & (phase <= 270 + eps)]), 3)
        V_5 = np.round(np.nanmean(ramp[(phase >= 360 - eps) & (phase <= 360 + eps)]), 3)

        print(f"V(phi=0°)={V_1:.3f} V")
        print(f"V(phi=90°)={V_2:.3f} V")
        print(f"V(phi=180°)={V_3:.3f} V")
        print(f"V(phi=270°)={V_4:.3f} V")
        print(f"V(phi=180°)={V_5:.3f} V")
        print(f"V(phi=180°)-V(phi=0°)={V_5-V_1:.3f} V")

        if any([V_1, V_2, V_3, V_4, V_5]) == None:
            print('aie')
        else:
            modify_parameter_value('config.txt', 'Piezo voltage', f"{V_1},{V_2},{V_3},{V_4},{V_5}")
        
        msg_box = QMessageBox()
        msg_box.setStyleSheet(styleH3)
        msg_box.information(self, "Information", "Piezo calibrée.\nLes valeurs ont été modifiées dans le fichier de configuration.")

        print("============================= END CALIBRATION ===================================")

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from ids_peak import ids_peak

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle('Test - Piezo calibration')
            self.setGeometry(300, 300, 1000, 600)

            self.central_widget = PiezoCalibrationWidget()
            self.setCentralWidget(self.central_widget)

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
    main.show()
    sys.exit(app.exec())
