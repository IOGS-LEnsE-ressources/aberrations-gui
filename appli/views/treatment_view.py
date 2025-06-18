'''This class handles the display of the treatment of unwrapped phase images. That is, displaying the PSF, the MTF,
the encircled energy and near-focal point energy distribution. Is components use external windows to display their contents,
each of which is composed of smaller display units (...DisplayWidget)
-------------------------------     -------------------------
|  Display#1   |  Display#2   |     |           |           |
|              |              |     |           |           |
|--------------|--------------|  or | Display#1 | Display#2 |
|  Display#3   |  Display#4   |     |           |           |
|              |              |     |           |           |
-------------------------------     -------------------------
'''

import numpy as np

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QLabel, QCheckBox,
    QGridLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QApplication, QPushButton, QSlider
)
from PyQt6.QtCore import Qt
from views.bar_graph_view import BarGraphView
from views.images_display_view import ImagesDisplayView
from lensepy.pyqt6.widget_xy_chart import XYChartWidget
from models.fourier_manager import FourierManager

def slice_image(image, slope : float, axis : bool = False):
    '''This global function is used in the following objects, it creates a plot from an image by slicing through it

    axis = False means the slice will be horizontal
    axis = True  means the slice will be vertical

    the sign and magnitude of the slope indicate the direction in which the slice will be taken, using this coordinate
    system:
            ^ y
            |
    --------|------> x    axis0 -> axis0 + 1
            |             axis1 -> axis1 + slope
            |
    If the slope is too big, the program will invert the axis by default and return a horizontal (resp. vertical) slice
    '''
    size = image.shape
    assert size[0] != 0 and size[1] != 0 and image is not None, "The data is not suitable : 0-dimensional array"
    if not axis:
        ax = 0
    else:
        ax = 1
    if int(size[ax] * slope) > size[not ax]:
        ax = not ax
        slope = 0

    plot_x = np.linspace(0, size[ax], size[ax])
    plot_y = np.zeros(size[ax])

    for i in range(size[ax]):
        if not ax:
            plot_y[i] = image[int(slope * (i - size[ax]/2) + size[ax]/2)][i]
        else:
            plot_y[i] = image[i][int(slope * (i - size[ax]/2) + size[ax]/2)-1]

    if not ax:
        angle = np.arctan(slope) * 180/np.pi
    else:
        angle = 90 - np.arctan(slope) * 180/np.pi

    if __name__ == "__main__":
        print(f"slope = {slope}")

    return plot_x, plot_y, angle


if __name__ == "__main__":
    class TreatmentWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.layout = QVBoxLayout()
            self.fourier = FourierManager()
            self.coefficients, self.size = self.fourier.test_params()
            self.psf_diff_lim, self.psf_image = self.calculate_psf_from_coefs(self.coefficients, self.size)
            self.mtf = self.fourier.MTF_from_PSF(self.psf_image)

            self.psf_button = QPushButton("PSF")
            self.airy_button = QPushButton("Airy")
            self.mtf_button = QPushButton("MTF")
            self.foca_button = QPushButton("Focal view")

            self.layout.addWidget(self.psf_button)
            self.layout.addWidget(self.airy_button)
            self.layout.addWidget(self.mtf_button)
            self.layout.addWidget(self.foca_button)

            self.setLayout(self.layout)

            self.psf_view = PSFView(self)
            self.airy_view = AiryView(self)
            self.mtf_view = MTFView(self)
            self.focal_view = FocalView(self)

            self.psf_button.clicked.connect(self.update_action)
            self.airy_button.clicked.connect(self.update_action)
            self.mtf_button.clicked.connect(self.update_action)
            self.foca_button.clicked.connect(self.update_action)

        def update_action(self):
            sender = self.sender()
            match sender:
                case self.psf_button:
                    self.close_all()
                    self.psf_view.show()
                case self.airy_button:
                    self.close_all()
                    self.airy_view.show()
                case self.mtf_button:
                    self.close_all()
                    self.mtf_view.show()
                case self.foca_button:
                    self.close_all()
                    self.focal_view.show()
        def close_all(self):
            self.psf_view.close()
            self.airy_view.close()

        def closeEvent(self, event):
            self.close_all()

        def calculate_psf_from_coefs(self, coefficients, size):
            _, psf_diff_lim, psf_image = self.fourier.find_rf_from_coefs(coefficients, size)
            return psf_diff_lim, psf_image

        def calculate_psf_from_image(self, phase_map):
            _, psf_diff_lim, psf_image = self.fourier.find_rf_from_image(phase_map)
            return psf_diff_lim.astype(np.uint8), psf_image.astype(np.uint8)


class PSFView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        self.layout = QHBoxLayout()

        self.left_widget = PSFDisplayWidget(self)
        self.right_widget = PSFDisplayWidget(self)

        self.left_widget.set_title("PSF with aberrations")
        self.right_widget.set_title("Diffraction limit PSF (no aberrations)")

        self.layout.addWidget(self.left_widget)
        self.layout.addWidget(self.right_widget)

        self.setLayout(self.layout)

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            psf_diff_lim, psf_image = self.parent.calculate_psf_from_coefs(coefficients, size)
            self.left_widget.set_image(psf_image)
            self.right_widget.set_image(psf_diff_lim)
        else:
            self.fourier = self.parent.fourier
            psf_image = self.parent.psf_image
            psf_diff_lim = self.parent.psf_diff_lim
            self.left_widget.set_image(psf_image)
            self.right_widget.set_image(psf_diff_lim)

    def afficher_phase(self, coefficients, size):
        return self.fourier.afficher_pupille(coefficients, size)

class AiryView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            _, psf_image = self.parent.calculate_psf_from_coefs(coefficients, size)
        else:
            self.fourier = self.parent.fourier
            psf_image = self.parent.psf_image

        size = psf_image.shape
        self.slice0 = slice_image(psf_image, 0, False)
        self.slice45 = slice_image(psf_image, size[1]/size[0], False)
        self.slice90 = slice_image(psf_image, 0, True)
        self.slice135 = slice_image(psf_image, -size[0]/size[1], True)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.top_left_widget = ChartDisplayWidget(self)
        self.top_right_widget = ChartDisplayWidget(self)
        self.bot_left_widget = ChartDisplayWidget(self)
        self.bot_right_widget = ChartDisplayWidget(self)

        self.top_left_widget.set_array(self.slice0[0], self.slice0[1])
        self.top_right_widget.set_array(self.slice45[0], self.slice45[1])
        self.bot_left_widget.set_array(self.slice90[0], self.slice90[1])
        self.bot_right_widget.set_array(self.slice135[0], self.slice135[1])

        self.top_left_widget.set_title(f"Coupe à {self.slice0[2]}°")
        self.top_right_widget.set_title(f"Coupe à {self.slice45[2]}°")
        self.bot_left_widget.set_title(f"Coupe à {self.slice90[2]}°")
        self.bot_right_widget.set_title(f"Coupe à {self.slice135[2]}°")

        self.layout.addWidget(self.top_left_widget, 0, 0)
        self.layout.addWidget(self.top_right_widget, 0, 1)
        self.layout.addWidget(self.bot_left_widget, 1, 0)
        self.layout.addWidget(self.bot_right_widget, 1, 1)

        self.setLayout(self.layout)

        if self.linked:
            self.fourier = self.parent.fourier
        else:
            self.fourier = FourierManager()


class MTFView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            _, psf_image = self.parent.calculate_psf_from_coefs(coefficients, size)
            mtf = self.fourier.MTF_from_PSF(psf_image)
        else:
            self.fourier = self.parent.fourier
            mtf = self.parent.mtf

        size = mtf.shape
        self.slice0 = slice_image(mtf, 0, False)
        self.slice45 = slice_image(mtf, size[1]/size[0], False)
        self.slice90 = slice_image(mtf, 0, True)
        self.slice135 = slice_image(mtf, -size[0]/size[1], True)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.top_left_widget = ChartDisplayWidget(self)
        self.top_right_widget = ChartDisplayWidget(self)
        self.bot_left_widget = ChartDisplayWidget(self)
        self.bot_right_widget = ChartDisplayWidget(self)

        self.top_left_widget.set_array(self.slice0[0], self.slice0[1])
        self.top_right_widget.set_array(self.slice45[0], self.slice45[1])
        self.bot_left_widget.set_array(self.slice90[0], self.slice90[1])
        self.bot_right_widget.set_array(self.slice135[0], self.slice135[1])

        self.top_left_widget.set_title(f"Coupe à {self.slice0[2]}°")
        self.top_right_widget.set_title(f"Coupe à {self.slice45[2]}°")
        self.bot_left_widget.set_title(f"Coupe à {self.slice90[2]}°")
        self.bot_right_widget.set_title(f"Coupe à {self.slice135[2]}°")

        self.layout.addWidget(self.top_left_widget, 0, 0)
        self.layout.addWidget(self.top_right_widget, 0, 1)
        self.layout.addWidget(self.bot_left_widget, 1, 0)
        self.layout.addWidget(self.bot_right_widget, 1, 1)

        self.setLayout(self.layout)

        if self.linked:
            self.fourier = self.parent.fourier
        else:
            self.fourier = FourierManager()


class FocalView(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent
        if self.parent is None:
            self.linked = False
        else:
            self.linked = True

        self.layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()

        self.maximum_c3 = 2
        self.minimum_c3 = -2
        self.Nstep = 30

        self.slider = QSlider()
        self.slider.setMaximum(self.maximum_c3)
        self.slider.setMinimum(self.minimum_c3)
        self.slider.setSliderPosition(0)

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            self.scan = self.fourier.focal_scan(coefficients, size, self.Nstep, self.minimum_c3, self.maximum_c3)
        else:
            self.fourier = self.parent.fourier
            self.scan = self.fourier.focal_scan(self.parent.coefficients, self.parent.size, self.Nstep, self.minimum_c3, self.maximum_c3)

        self.top_layout.addWidget(self.slider)
        self.layout.addLayout(self.top_layout)

        self.setLayout(self.layout)


class PSFDisplayWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.title = QLabel("")
        self.image_display = ImagesDisplayView()
        self.image_display.setMinimumSize(400, 400)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.image_display)

        self.setLayout(self.layout)

    def normalize_image(self, image_float):
        if image_float.dtype != np.uint8:
            min_val = image_float.min()
            max_val = image_float.max()
            if max_val > min_val:
                image_norm = (image_float - min_val) / (max_val - min_val)
            else:
                image_norm = np.zeros_like(image_float)

            image_uint8 = (image_norm * 255).astype(np.uint8)
            return image_uint8
        else:
            return image_float

    def set_image(self, image):
        image = self.normalize_image(image)
        self.image_display.set_image_from_array(image)
        self.image_display.fit_images_in_view()

    def set_array(self, X, Y):
        self.image_display = XYChartWidget()
        self.image_display.set_background("white")
        self.image_display.set_data(X, Y)
        self.image_display.refresh_chart()

    def set_title(self, title: str):
        self.title.setText(title)


class ChartDisplayWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.image_display = XYChartWidget()
        self.image_display.setMinimumSize(400, 400)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_display)

        self.setLayout(self.layout)
    def set_array(self, X, Y):
        self.image_display.set_background("white")
        X, Y = self.smoother_bounds(X, Y)
        self.image_display.set_data(X, Y)
        self.image_display.refresh_chart()

    def set_title(self, title: str):
        self.image_display.set_title(title)

    def smoother_bounds(self, x_array, y_array, margin: int = 4, lower_bound: float = 1e-05):
        '''This function performs an element_wise search in a list and tries to get the external zeroes out to get a
        smoother result

        the variable margin represents the nuber of zeroes that are left out so that the plot doesn't have non-zero
        values at the boundaries
        lower_bound is the threshold under which the values are considered to be zero

        The function is also built to ensure the graph remains centered'''
        new_array = y_array[:]
        size = y_array.shape[0]
        i = 0
        while y_array[i] < lower_bound and y_array[size - i - 1] < lower_bound:
            do_pop = i - margin >= 0
            if do_pop:
                new_array = np.delete(new_array, 0)
                x_array = np.delete(x_array, 0)
                new_array = np.delete(new_array, -1)
                x_array = np.delete(x_array, -1)
            i += 1
        return x_array, new_array

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreatmentWindow()
    window.show()
    sys.exit(app.exec())