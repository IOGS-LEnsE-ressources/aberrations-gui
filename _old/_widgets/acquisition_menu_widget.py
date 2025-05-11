# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys, os, time
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, QThread, Qt
import numpy as np
from skimage.restoration import unwrap_phase

from lensepy import load_dictionary, translate
from lensepy.css import *

from process.unwrap import suppression_bord
from process.acquisition_images import get_phase, check_alpha
from process.surface_statistics import statistique_surface
from process.export_images import *
from process.zernike_coefficents import *

if __name__ == '__main__':
    from lineedit_bloc import LineEditBloc
else:
    from widgets.lineedit_bloc import LineEditBloc

from timeit import default_timer as timer
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

import cv2


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

# Zernkike coefficients calculation
class ZernikeThread(QThread):
    def __init__(self, parent):
        self.parent = parent

    def run(self):
        print('Run Thread Zernike')
        if not (hasattr(self.parent, 'coeffs')):
            self.parent.corrected_wavefront, self.parent.coeffs, self.parent.polynomials = (
                remove_aberration(self.parent.phase, self.parent.aberrations_considered))
        elif hasattr(self.parent, 'polynomials'):
            self.parent.corrected_wavefront, self.parent.coeffs, self.parent.polynomials = (
                remove_aberration(self.parent.phase, self.parent.aberrations_considered,
                                  self.parent.coeffs, self.parent.polynomials))
        else:
            self.parent.corrected_wavefront, self.parent.coeffs, self.parent.polynomials = (
                remove_aberration(self.parent.phase, self.parent.aberrations_considered,
                                  self.parent.coeffs))


# %% Auxiliary widget
class RemoveFaultsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent=None)

        self.parent = parent
        self.aberrations_considered = self.parent.aberrations_considered
        self.coeff_calculated = False

        self.setStyleSheet(f"background-color: {ORANGE_IOGS};")
        self.layout = QVBoxLayout()

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        
        self.label_title_remove_faults_menu = QLabel("Soustraitre les défauts")
        self.label_title_remove_faults_menu.setStyleSheet(styleH1)
        
        self.subwidget_faults = QWidget()
        self.sublayout_faults = QHBoxLayout()

        # First col
        # ---------
        self.subwidget_left = QWidget()
        self.sublayout_left = QVBoxLayout()

        self.checkbox_remove_tilt = QCheckBox("Retirer le tilt")
        self.checkbox_remove_tilt.setStyleSheet(styleCheckbox)
        self.checkbox_remove_tilt.stateChanged.connect(self.checkbox_remove_tilt_changed)

        self.checkbox_remove_defocus = QCheckBox("Retirer le defocus")
        self.checkbox_remove_defocus.setStyleSheet(styleCheckbox)
        self.checkbox_remove_defocus.stateChanged.connect(self.checkbox_remove_defocus_changed)

        self.checkbox_remove_spherical_aberration = QCheckBox("Retirer l'abération sphérique")
        self.checkbox_remove_spherical_aberration.setStyleSheet(styleCheckbox)
        self.checkbox_remove_spherical_aberration.stateChanged.connect(self.checkbox_remove_spherical_aberration_changed)
        
        self.sublayout_left.addWidget(self.checkbox_remove_tilt)
        self.sublayout_left.addWidget(self.checkbox_remove_defocus)
        self.sublayout_left.addWidget(self.checkbox_remove_spherical_aberration)
        self.sublayout_left.setContentsMargins(0, 0, 0, 0)
        self.subwidget_left.setLayout(self.sublayout_left)
        
        # Second col
        # ----------
        self.subwidget_right = QWidget()
        self.sublayout_right = QVBoxLayout()
        
        self.checkbox_remove_astigmatism = QCheckBox("Retirer l'astigmatisme")
        self.checkbox_remove_astigmatism.setStyleSheet(styleCheckbox)
        self.checkbox_remove_astigmatism.stateChanged.connect(self.checkbox_remove_astigmatism_changed)

        self.checkbox_remove_coma = QCheckBox("Retirer la coma")
        self.checkbox_remove_coma.setStyleSheet(styleCheckbox)
        self.checkbox_remove_coma.stateChanged.connect(self.checkbox_remove_coma_changed)


        self.sublayout_right.addWidget(self.checkbox_remove_astigmatism)
        self.sublayout_right.addWidget(self.checkbox_remove_coma)
        self.sublayout_right.setContentsMargins(0, 0, 0, 0)
        self.subwidget_right.setLayout(self.sublayout_right)
        
        # Combined
        # --------
        self.sublayout_faults.addWidget(self.subwidget_left)
        self.sublayout_faults.addWidget(self.subwidget_right)
        self.sublayout_faults.setContentsMargins(0, 0, 0, 0)
        self.subwidget_faults.setLayout(self.sublayout_faults)
        
        self.layout.addWidget(self.label_title_remove_faults_menu)
        self.layout.addWidget(self.subwidget_faults)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Calculations
        # ------------
        self.zernike_calculated = False
        self.zernike_thread = ZernikeThread(self)
        self.corrected_wavefront = None

    def checkbox_remove_tilt_changed(self, state):
        print(f"Remove tilt [{bool(state//2)}]")

        self.aberrations_considered[1] = state//2
        self.aberrations_considered[2] = state//2

        try:
            self.phase = self.parent.phase
            self.aberrations_considered = self.parent.aberrations_considered

            self.apply_modifications()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", f"Veuillez effectuer une acquisiton.")
            self.checkbox_remove_tilt.setChecked(False)

    def checkbox_remove_defocus_changed(self, state):
        print(f"Remove defocus [{bool(state//2)}]")

        self.aberrations_considered[4] = state//2

        try:
            self.phase = self.parent.phase
            self.aberrations_considered = self.parent.aberrations_considered

            self.apply_modifications()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", f"Veuillez effectuer une acquisiton.")
            self.checkbox_remove_defocus.setChecked(False)

    def checkbox_remove_spherical_aberration_changed(self, state):
        print(f"Remove spherical aberation [{bool(state//2)}]")

        self.aberrations_considered[12] = state//2

        try:
            self.phase = self.parent.phase
            self.aberrations_considered = self.parent.aberrations_considered

            self.apply_modifications()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", f"Veuillez effectuer une acquisiton. \n {e}")
            self.checkbox_remove_spherical_aberration.setChecked(False)

    def checkbox_remove_astigmatism_changed(self, state):
        print(f"Remove astigmatism [{bool(state//2)}]")

        self.aberrations_considered[3] = state//2
        self.aberrations_considered[5] = state//2

        try:
            self.phase = self.parent.phase
            self.aberrations_considered = self.parent.aberrations_considered

            self.apply_modifications()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", f"Veuillez effectuer une acquisiton. \n {e}")
            self.checkbox_remove_astigmatism.setChecked(False)

    def checkbox_remove_coma_changed(self, state):
        print(f"Remove coma [{bool(state//2)}]")

        self.aberrations_considered[8] = state//2
        self.aberrations_considered[7] = state//2

        try:
            self.phase = self.parent.phase
            self.aberrations_considered = self.parent.aberrations_considered

            self.apply_modifications()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", f"Veuillez effectuer une acquisiton. \n {e}")
            self.checkbox_remove_coma.setChecked(False)

    def apply_modifications(self):
        if self.zernike_calculated is False:
            self.zernike_thread.start()
            self.zernike_thread.finished.connect(self.zernike_thread_finished)
        else:
            self.zernike_thread_finished()
        '''
        # corrected_wavefront = remove_aberration(self.phase, self.aberrations_considered)
        print('apply_modifications')
        if not(hasattr(self, 'coeffs')):
            corrected_wavefront, self.coeffs, self.polynomials = remove_aberration(self.phase, self.aberrations_considered)
        elif hasattr(self, 'polynomials'):
            corrected_wavefront, self.coeffs, self.polynomials = remove_aberration(self.phase, self.aberrations_considered, self.coeffs, self.polynomials)
        else:
            corrected_wavefront, self.coeffs, self.polynomials = remove_aberration(self.phase, self.aberrations_considered, self.coeffs)

        # corrected_wavefront *= self.parent.wedge_factor
        corrected_wavefront *= np.sign(self.parent.wedge_factor)
        '''


    def zernike_thread_finished(self):
        self.zernike_calculated = True
        PV, RMS = statistique_surface(self.corrected_wavefront)
        print(f"corrected_interpolated_wavefront min/max: {np.nanmin(self.corrected_wavefront)}/{np.nanmax(self.corrected_wavefront)}")
        array = np.array([
            ['', 1, 2, 3, 4, 5, 'Moyenne'],
            ['PV (λ)', round(PV, 4), np.nan, np.nan, np.nan, np.nan, round(PV, 4)],
            ['RMS (λ)', round(RMS, 4), np.nan, np.nan, np.nan, np.nan, round(RMS, 4)]
        ])

        self.parent.parent.results_menu_widget.array = array
        self.parent.parent.results_menu_widget.table_results.update_table(self.parent.multiply_results_array_by_wedge_factor())

        self.parent.display_phase(self.corrected_wavefront)


    def new_sample(self):
        if hasattr(self, 'coeffs'):
            del self.coeffs
        if hasattr(self, 'polynomials'):
            del self.polynomials


# %% Widget
class AcquisitionMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent
        self.acquisition_done = False

        if self.parent is None or not hasattr(self.parent, 'wedge_factor'):
            self.wedge_factor = 1
        else:
            self.wedge_factor = self.parent.wedge_factor

        if self.parent is not None and hasattr(self.parent, 'aberrations_considered'):
            self.aberrations_considered = self.parent.aberrations_considered
        else:
            self.aberrations_considered = np.zeros(37, dtype=int)
            self.aberrations_considered[0] = 1

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_acquisition_menu = QLabel("Acquisition")
        self.setStyleSheet(styleH1)
        
        # Subwidget to start acquisition
        # ------------------------------
        self.subwidget_start_acquisiton = QWidget()
        self.sublayout_start_acquisiton = QHBoxLayout()

        self.button_simple_acquisition = QPushButton("Acquisition unique")
        self.button_simple_acquisition.setStyleSheet(unactived_button)
        self.button_simple_acquisition.setFixedHeight(BUTTON_HEIGHT)
        self.button_simple_acquisition.clicked.connect(self.button_simple_acquisition_isClicked)

        self.button_repeated_acquisition = QPushButton("Acquisition répétée")
        self.button_repeated_acquisition.setStyleSheet(unactived_button)
        self.button_repeated_acquisition.setFixedHeight(BUTTON_HEIGHT)
        self.button_repeated_acquisition.clicked.connect(self.button_repeated_acquisition_isClicked)

        self.sublayout_start_acquisiton.addWidget(self.button_simple_acquisition)
        self.sublayout_start_acquisiton.addWidget(self.button_repeated_acquisition)
        self.sublayout_start_acquisiton.setContentsMargins(0, 0, 0, 0)
        self.subwidget_start_acquisiton.setLayout(self.sublayout_start_acquisiton)

        # Wedge factor entry
        #-------------------
        self.lineedit_wedge_factor = LineEditBloc("Wedge factor", txt=str(self.wedge_factor))
        self.lineedit_wedge_factor.keyPressEvent = self.wedge_factor_is_modified

        # Remove faults menu
        # ------------------
        self.submenu_remove_faults = RemoveFaultsWidget(self)

        # Subwidget to save acquisition
        # ------------------------------
        self.subwidget_save_acquisiton = QWidget()
        self.sublayout_save_acquisiton = QHBoxLayout()

        self.button_see_and_save_images = QPushButton("Voir et enregistrer les images")
        self.button_see_and_save_images.setStyleSheet(unactived_button)
        self.button_see_and_save_images.setFixedHeight(BUTTON_HEIGHT)
        self.button_see_and_save_images.clicked.connect(self.button_see_and_save_images_isClicked)

        self.button_save_phase = QPushButton("Enregistrer la phase")
        self.button_save_phase.setStyleSheet(unactived_button)
        self.button_save_phase.setFixedHeight(BUTTON_HEIGHT)
        self.button_save_phase.clicked.connect(self.button_save_phase_isClicked)

        self.sublayout_save_acquisiton.addWidget(self.button_see_and_save_images)
        self.sublayout_save_acquisiton.addWidget(self.button_save_phase)
        self.sublayout_save_acquisiton.setContentsMargins(0, 0, 0, 0)
        self.subwidget_save_acquisiton.setLayout(self.sublayout_save_acquisiton)
        
        # Add widgets to the layout
        # -------------------------
        self.layout.addWidget(self.label_title_acquisition_menu)
        self.layout.addWidget(self.lineedit_wedge_factor)
        self.layout.addWidget(self.subwidget_start_acquisiton)

        if self.acquisition_done:
            self.layout.addWidget(self.submenu_remove_faults)
            self.layout.addWidget(self.subwidget_save_acquisiton)

        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def wedge_factor_is_modified(self, event):
        if (event.key() == Qt.Key.Key_Return) or (event.key() == Qt.Key.Key_Enter):
            try:
                old_wedge_factor = self.wedge_factor
                self.wedge_factor = float(self.lineedit_wedge_factor.text())
                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.information(self, "Information", "Le wedge factor a bien été modifié.")

                if self.parent is not None and hasattr(self.parent, 'results_menu_widget'):
                    if hasattr(self.parent.results_menu_widget, 'table_results') and hasattr(self.parent.results_menu_widget, 'array'):
                        self.parent.results_menu_widget.table_results.update_table(self.multiply_results_array_by_wedge_factor())
                    else:
                        print("L'attribut 'table_results' ou 'array' est manquant dans 'results_menu_widget'")

                    if hasattr(self, 'phase'):
                        self.display_phase(self.phase*self.wedge_factor/old_wedge_factor)
                else:
                    print("Le parent n'existe pas ou n'a pas l'attribut 'results_menu_widget'")

            except ValueError:
                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.warning(self, "Erreur", "Le wedge factor doit être un nombre réel.")

        elif event.key() == Qt.Key.Key_Escape:
            self.lineedit_wedge_factor.clearFocus()
        else:
            # Laissez le QLineEdit gérer les autres touches
            super().keyPressEvent(event)
        print(self.wedge_factor)

    def button_simple_acquisition_isClicked(self):
        self.button_simple_acquisition.setStyleSheet(actived_button)
        time.sleep(0.1)
        print('button_simple_acquisition_isClicked')

        self.submenu_remove_faults.new_sample()

        if self.parent is not None:
            try:
                mask = self.parent.mask
                if mask is None:
                    msg_box = QMessageBox()
                    msg_box.setStyleSheet(styleH3)
                    msg_box.warning(self, "Erreur", "Vous devez définir un masque.")
                    self.button_simple_acquisition.setStyleSheet(unactived_button)  
                    return None

                # Start measuring the time
                timer_start = timer()

                # Get wrapped phase
                wrapped_phase, self.images = get_phase(self.parent, sigma_gaussian_filter=3)
                time_getting_wrapped_phase = timer() - timer_start

                # Check alpha
                average_alpha, std_alpha = check_alpha(self.images)
                
                if average_alpha < 86 or average_alpha > 94 or std_alpha > 8:
                    msg_box = QMessageBox()
                    msg_box.setStyleSheet(styleH3)
                    msg_box.warning(self, "Erreur", f"α={average_alpha:.2f} °: il vaut mieux reprendre la mesure ou attendre que le laser se stabilise.")
                    self.button_simple_acquisition.setStyleSheet(unactived_button)  
                    return None
                else:
                    """plt.figure()
                    plt.imshow(wrapped_phase, cmap='gray')
                    plt.title(f"wrapped | {np.sum(np.isnan(wrapped_phase))} ({np.sum(np.isnan(wrapped_phase))/(wrapped_phase.shape[0]*wrapped_phase.shape[1])*100} %)")
                    plt.show()"""

                    # Unwrap phase
                    unwrapped_phase_start = timer()

                    # unwrapped_phase = unwrap2D(wrapped_phase)[0]
                    unwrapped_phase = unwrap_phase(wrapped_phase)
                    unwrapped_phase[mask == 0] = np.NaN
                    unwrapped_phase = gaussian_filter(unwrapped_phase, 10)

                    time_getting_unwrapped_phase = timer() - unwrapped_phase_start
                    """plt.figure()
                    plt.imshow(unwrapped_phase, cmap='gray')
                    plt.title(f"unwrapped | {np.sum(np.isnan(unwrapped_phase))} ({np.sum(np.isnan(unwrapped_phase))/(wrapped_phase.shape[0]*wrapped_phase.shape[1])*100} %)")
                    plt.show()"""

                    # Suppress borders and mean adjustment
                    final_phase_start = timer()
                    unwrapped_phase = suppression_bord(unwrapped_phase, 3)

                    unwrapped_phase = unwrapped_phase - np.nanmean(unwrapped_phase)
                    self.phase = unwrapped_phase / (2 * PI)
                    time_getting_final_phase = timer() - final_phase_start

                    # Total time
                    total_time = timer() - timer_start

                # Display times
                """print(
                    f"Time to get the wrapped phase: {time_getting_wrapped_phase:.4f} s",
                    f"Time to get the unwrapped phase: {time_getting_unwrapped_phase:.4f} s",
                    f"Time to get the final phase: {time_getting_final_phase:.4f} s",
                    f"Total time: {total_time:.4f} s",
                    sep='\n', end='\n\n'
                )"""
                
                #self.zernike_coefficients = get_zernike_coefficient(self.phase)

                # Calculate statistics
                PV, RMS = statistique_surface(self.phase)
                array = np.array([
                    ['', 1, 2, 3, 4, 5, 'Moyenne'],
                    ['PV (λ)', round(PV, 4), np.nan, np.nan, np.nan, np.nan, round(PV, 4)],
                    ['RMS (λ)', round(RMS, 4), np.nan, np.nan, np.nan, np.nan, round(RMS, 4)]
                ])

                self.parent.results_menu_widget.array = array
                self.parent.results_menu_widget.table_results.update_table(self.multiply_results_array_by_wedge_factor())
                
                # Display phase in 3D
                self.display_phase(self.phase*self.wedge_factor)

            except Exception as e:
                print(f'Exception - button_simple_acquisition_isClicked {e}')
        self.button_simple_acquisition.setStyleSheet(unactived_button)
        self.acquisition_done = True
        self.layout.addWidget(self.submenu_remove_faults)
        self.layout.addWidget(self.subwidget_save_acquisiton)

    def button_repeated_acquisition_isClicked(self):
        self.button_repeated_acquisition.setStyleSheet(actived_button)
        time.sleep(0.1)
        print('button_repeated_acquisition_isClicked')

        self.submenu_remove_faults.new_sample()

        if self.parent is not None:
            try:
                mask = self.parent.mask
                if mask is None:
                    msg_box = QMessageBox()
                    msg_box.setStyleSheet(styleH3)
                    msg_box.warning(self, "Erreur", "Vous devez définir un masque.")
                    self.button_repeated_acquisition.setStyleSheet(unactived_button)  
                    return None

                all_PV = []
                all_RMS = []

                for i in range(5):
                    wrapped_phase, self.images = get_phase(self.parent, sigma_gaussian_filter=3)
                    average_alpha, std_alpha = check_alpha(self.images)
                    
                    if average_alpha<86 or average_alpha>94 or std_alpha>8:
                        msg_box = QMessageBox()
                        msg_box.setStyleSheet(styleH3)
                        msg_box.warning(self, "Erreur", f"α={average_alpha} °: il vaut mieux reprendre la mesure ou attendre que le laser se stabilise.")
                        self.button_repeated_acquisition.setStyleSheet(unactived_button)  
                        return None
                    else:
                        # unwrapped_phase = unwrap2D(wrapped_phase)[0]
                        unwrapped_phase = unwrap_phase(wrapped_phase)
                        unwrapped_phase[mask == 0] = np.NaN
                        unwrapped_phase = gaussian_filter(unwrapped_phase, 10)

                    self.phase = unwrapped_phase/(2*PI)

                    PV, RMS = statistique_surface(self.phase)

                    all_PV.append(PV)
                    all_RMS.append(RMS)

                self.display_phase(self.phase)
                    
                array = np.array([
                    ['', 1, 2, 3, 4, 5, 'Moyenne'],
                    ['PV (λ)', round(all_PV[0], 4), round(all_PV[1], 4), round(all_PV[2], 4), round(all_PV[3], 4), round(all_PV[4], 4), round(np.mean(all_PV), 4)],
                    ['RMS (λ)', round(all_RMS[0], 4), round(all_RMS[1], 4), round(all_RMS[2], 4), round(all_RMS[3], 4), round(all_RMS[4], 4), round(np.mean(all_RMS), 4)]
                ])

                self.parent.results_menu_widget.array = array
                self.parent.results_menu_widget.table_results.update_table(self.multiply_results_array_by_wedge_factor())

                self.display_phase(self.phase*self.wedge_factor)

            except Exception as e:
                print(f'Exception - button_simple_acquisition_isClicked {e}')

        self.button_repeated_acquisition.setStyleSheet(unactived_button)
        self.acquisition_done = True
        self.layout.addWidget(self.submenu_remove_faults)
        self.layout.addWidget(self.subwidget_save_acquisiton)
    
    def button_see_and_save_images_isClicked(self):
        self.button_see_and_save_images.setStyleSheet(actived_button)
        print('button_see_and_save_images_isClicked')

        try:
            default_dir = os.path.expanduser("~/Desktop")
            path = QFileDialog.getExistingDirectory(self, "Sélectionnez un dossier", default_dir)
            if path:
                save_images(self.images, path)
                display_images(self.images)
        except:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", "Vous devez faire un acquisition.")
            self.button_repeated_acquisition.setStyleSheet(unactived_button)  
            return None

        self.button_see_and_save_images.setStyleSheet(unactived_button)

    def button_save_phase_isClicked(self):
        self.button_save_phase.setStyleSheet(actived_button)
        print('button_save_phase_isClicked')

        try:
            default_dir = os.path.expanduser("~/Desktop")
            path = QFileDialog.getExistingDirectory(self, "Sélectionnez un dossier", default_dir)
            if path:
                plt.figure()
                plt.imshow(self.phase-np.nanmin(self.phase), cmap='rainbow')
                cbar = plt.colorbar()
                cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f} λ'))
                plt.axis('off')
                plt.savefig(f"{path}/phase.png")
                plt.title('Phase enregitrée avec succès.')
                plt.show()
        except:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, "Erreur", "Vous devez faire un acquisition.")
            self.button_save_phase.setStyleSheet(unactived_button)  
            return None

        self.button_save_phase.setStyleSheet(unactived_button)
    
    def display_phase(self, phase):
        scale_factor = 0.4
        scaled_image = cv2.resize(phase, (0, 0), fx = scale_factor, fy = scale_factor, interpolation=cv2.INTER_CUBIC)
        phase = scaled_image

        not_nan_indices = np.where(~np.isnan(phase))
        values = phase[not_nan_indices]
        x = not_nan_indices[0]
        y = not_nan_indices[1]

        # Create the grid for interpolation
        x_grid, y_grid = np.meshgrid(np.linspace(0, phase.shape[1], phase.shape[1]), np.linspace(0, phase.shape[0], phase.shape[0]))

        z = phase

        """fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_plot = np.arange(interpolated_values.shape[0])
        y_plot = np.arange(interpolated_values.shape[1])
        x_plot, y_plot = np.meshgrid(x_plot, y_plot)

        ax.plot_surface(x_plot, y_plot, interpolated_values, cmap='magma')

        plt.show()"""

        try:
            z *= (np.nanmax(x) -np.nanmin(x)) * .75 / (np.nanmax(z)-np.nanmin(z))
            z -= np.nanmax(z)/4

            self.parent.graphic_widget.set_data(x_grid, y_grid, z)
            self.parent.graphic_widget.refresh_chart()
        except Exception as e:
            print(f"Affichage 3D - {e}")

    def multiply_results_array_by_wedge_factor(self):
        arr = self.parent.results_menu_widget.array.copy()
        arr[1:, 1:] = np.round(((arr[1:, 1:].astype(float))*np.abs(self.wedge_factor)), 4)
        return arr


# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from ids_peak import ids_peak

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(300, 300, 800, 200)

            self.central_widget = AcquisitionMenuWidget()
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
