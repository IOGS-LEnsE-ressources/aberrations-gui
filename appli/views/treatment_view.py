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
from lensepy.images.conversion import resize_image_ratio, resize_image
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
    If the slope is too big, the program will invert the axis by default and return the associated slice
    '''
    size = image.shape
    assert size[0] != 0 and size[1] != 0 and image is not None, "The data is not suitable : 0-dimensional array"
    if not axis:
        ax = 0
    else:
        ax = 1
    if int(size[ax] * slope) > size[not ax]:
        ax = not ax
        slope = 1/slope

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

    return plot_x, plot_y, round(angle, 3)


if __name__ == "__main__":
    class TreatmentWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.layout = QVBoxLayout()
            self.fourier = FourierManager()
            self.coefficients, self.size = self.fourier.test_params()
            self.rf, self.psf_diff_lim, self.psf_image = self.fourier.find_rf_from_coefs(self.coefficients, self.size)
            self.mtf_image = self.fourier.MTF_from_PSF(self.psf_image)
            self.mtf_diff = self.fourier.MTF_from_PSF(self.psf_diff_lim)

            self.psf_button = QPushButton("PSF")
            self.airy_button = QPushButton("Airy")
            self.mtf_button = QPushButton("MTF")
            self.foca_button = QPushButton("Focal view")

            self.layout.addWidget(self.psf_button)
            self.layout.addWidget(self.airy_button)
            self.layout.addWidget(self.mtf_button)
            self.layout.addWidget(self.foca_button)

            self.setLayout(self.layout)

            self.airy_view = AiryView(self)
            self.psf_view = PSFView(self)
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
            self.mtf_view.close()
            self.focal_view.close()

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

        bounds = self.parent.airy_view.get_bounds()
        lims = max(bounds[0]//2, bounds[1]//2)

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            psf_diff_lim, psf_image = self.parent.calculate_psf_from_coefs(coefficients, size)
        else:
            self.fourier = self.parent.fourier
            size = self.parent.size
            psf_image = self.parent.psf_image
            psf_diff_lim = self.parent.psf_diff_lim

        h, w = size
        psf_image = psf_image[h//2 - lims:h//2 + lims, w//2 - lims:w//2 + lims]
        psf_diff_lim = psf_diff_lim[h//2 - lims:h//2 + lims, w//2 - lims:w//2 + lims]

        psf_image = resize_image_ratio(psf_image, 900, 900)
        psf_diff_lim = resize_image_ratio(psf_diff_lim, 900, 900)
        self.left_widget.set_image(psf_image)
        self.right_widget.set_image(psf_diff_lim)

    """def display_phase(self, coefficients, size):
        return self.fourier.afficher_pupille(coefficients, size)"""

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
            rf, psf_diff, psf_image = self.fourier.find_rf_from_coefs(coefficients, size)
        else:
            self.fourier = self.parent.fourier
            coefficients, size = self.parent.coefficients, self.parent.size
            rf, psf_diff, psf_image = self.parent.rf, self.parent.psf_diff_lim, self.parent.psf_image

        self.rf_text = QLabel(f"Rf = {rf}")

        size = psf_image.shape
        self.slice0_abe = slice_image(psf_image, 0, False)
        self.slice45_abe = slice_image(psf_image, size[1] / size[0], False)
        self.slice90_abe = slice_image(psf_image, 0, True)
        self.slice135_abe = slice_image(psf_image, -size[0] / size[1], True)

        self.slice0_dif = slice_image(psf_diff, 0, False)
        self.slice45_dif = slice_image(psf_diff, size[1] / size[0], False)
        self.slice90_dif = slice_image(psf_diff, 0, True)
        self.slice135_dif = slice_image(psf_diff, -size[0] / size[1], True)

        self.main_layout = QVBoxLayout()

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.top_left_widget = ChartDisplayWidget(self)
        self.top_right_widget = ChartDisplayWidget(self)
        self.bot_left_widget = ChartDisplayWidget(self)
        self.bot_right_widget = ChartDisplayWidget(self)

        self.top_left_widget.set_array(self.slice0_abe[0], self.slice0_abe[1], self.slice0_dif[1])
        self.top_right_widget.set_array(self.slice45_abe[0], self.slice45_abe[1], self.slice45_dif[1])
        self.bot_left_widget.set_array(self.slice90_abe[0], self.slice90_abe[1], self.slice90_dif[1])
        self.bot_right_widget.set_array(self.slice135_abe[0], self.slice135_abe[1], self.slice135_dif[1])

        self.top_left_widget.set_title(f"Coupe à {self.slice0_abe[2]}°")
        self.top_right_widget.set_title(f"Coupe à {self.slice45_abe[2]}°")
        self.bot_left_widget.set_title(f"Coupe à {self.slice90_abe[2]}°")
        self.bot_right_widget.set_title(f"Coupe à {self.slice135_abe[2]}°")

        self.layout.addWidget(self.top_left_widget, 0, 0)
        self.layout.addWidget(self.top_right_widget, 0, 1)
        self.layout.addWidget(self.bot_left_widget, 1, 0)
        self.layout.addWidget(self.bot_right_widget, 1, 1)

        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.rf_text)

        self.setLayout(self.main_layout)

        if self.linked:
            self.fourier = self.parent.fourier
        else:
            self.fourier = FourierManager()

    def get_bounds(self):
        X, _, _ = self.top_left_widget.shorten_bounds(self.slice90_abe[0], self.slice90_abe[1])
        Y, _, _ = self.top_left_widget.shorten_bounds(self.slice0_abe[0], self.slice0_abe[1])
        return len(X), len(Y)


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
            psf_diff_lim, psf_image = self.parent.calculate_psf_from_coefs(coefficients, size)
            mtf_image = self.fourier.MTF_from_PSF(psf_image)
            mtf_diff = self.fourier.MTF_from_PSF(psf_diff_lim)
        else:
            self.fourier = self.parent.fourier
            mtf_image = self.parent.mtf_image
            mtf_diff = self.parent.mtf_diff

        size = mtf_image.shape
        self.slice0_abe = slice_image(mtf_image, 0, False)
        self.slice45_abe = slice_image(mtf_image, size[1]/size[0], False)
        self.slice90_abe = slice_image(mtf_image, 0, True)
        self.slice135_abe = slice_image(mtf_image, -size[0]/size[1], True)

        self.slice0_dif = slice_image(mtf_diff, 0, False)
        self.slice45_dif = slice_image(mtf_diff, size[1] / size[0], False)
        self.slice90_dif = slice_image(mtf_diff, 0, True)
        self.slice135_dif = slice_image(mtf_diff, -size[0] / size[1], True)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.top_left_widget = ChartDisplayWidget(self)
        self.top_right_widget = ChartDisplayWidget(self)
        self.bot_left_widget = ChartDisplayWidget(self)
        self.bot_right_widget = ChartDisplayWidget(self)

        self.top_left_widget.set_array(self.slice0_abe[0], self.slice0_abe[1], self.slice0_dif[1])
        self.top_right_widget.set_array(self.slice45_abe[0], self.slice45_abe[1], self.slice45_dif[1])
        self.bot_left_widget.set_array(self.slice90_abe[0], self.slice90_abe[1], self.slice90_dif[1])
        self.bot_right_widget.set_array(self.slice135_abe[0], self.slice135_abe[1], self.slice135_dif[1])

        self.top_left_widget.set_title(f"Coupe à {self.slice0_abe[2]}°")
        self.top_right_widget.set_title(f"Coupe à {self.slice45_abe[2]}°")
        self.bot_left_widget.set_title(f"Coupe à {self.slice90_abe[2]}°")
        self.bot_right_widget.set_title(f"Coupe à {self.slice135_abe[2]}°")

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

        self.layout = QHBoxLayout()

        self.maximum_slider = 200
        self.minimum_slider = -200
        self.maximum_c3 = 7
        self.minimum_c3 = self.minimum_slider * self.maximum_c3/self.maximum_slider
        self.Nstep = 30
        self.color = (255, 150, 10)

        self.c3_text = QLabel(f"C3 = 0")
        self.c3_text.setFixedWidth(75)

        if not self.linked:
            self.fourier = FourierManager()
            coefficients, size = self.fourier.test_params()
            self.scan = self.fourier.focal_scan(coefficients, size, self.Nstep, self.minimum_c3, self.maximum_c3)
        else:
            self.fourier = self.parent.fourier
            coefficients, size = self.parent.coefficients[:], self.parent.size
            self.scan = self.fourier.focal_scan(coefficients, size, self.Nstep, self.minimum_c3, self.maximum_c3)

        self.slider = QSlider()
        self.maximum_slider = self.maximum_slider + int(coefficients[3] * self.maximum_slider/self.maximum_c3)
        self.minimum_slider = self.minimum_slider + int(coefficients[3] * self.maximum_slider/self.maximum_c3)
        self.slider.setMaximum(self.maximum_slider)
        self.slider.setMinimum(self.minimum_slider)
        self.slider.setSliderPosition(int(coefficients[3] * self.maximum_slider/self.maximum_c3))

        self.hslice = self.scan[int(self.Nstep//2), :, :]
        self.vslice = self.scan[:, self.fourier.rpupil, :]
        self.slider.valueChanged.connect(self.slider_update)

        self.hslice_display = PSFDisplayWidget()
        self.hslice = resize_image_ratio(self.hslice, 900, 900)
        self.hslice = self.hslice_display.normalize_image(self.hslice)
        self.hslice_display.set_image(self.hslice)
        self.hslice_display.set_title("coupe horizontale")

        self.vslice_display = PSFDisplayWidget()
        self.vslice = self.vslice_display.shorten_horizontal(self.vslice)
        self.vslice = resize_image(self.vslice, 900, 900)
        self.vslice = self.vslice_display.normalize_image(self.vslice)

        value = self.slider.value()
        ratio = (value - self.minimum_slider) / (self.maximum_slider - self.minimum_slider)
        vslice_copy = self.vslice_display.color_line(self.vslice, ratio, 2, self.color)
        self.vslice_display.set_image(vslice_copy)

        self.vslice_display.set_image(vslice_copy)
        self.vslice_display.set_title("coupe verticale")

        self.layout.addWidget(self.c3_text)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.hslice_display)
        self.layout.addWidget(self.vslice_display)

        self.setLayout(self.layout)

    def slider_update(self):
        value = self.slider.value()
        ratio = (self.maximum_slider - value)/(self.maximum_slider - self.minimum_slider)
        index = int(ratio * self.Nstep) - 1
        if index < 0:
            index = 0

        self.hslice = self.scan[index, :, :]
        self.hslice = self.hslice_display.normalize_image(self.hslice)

        self.c3_text.setText(f"C3 = {round(ratio * (self.maximum_c3 - self.minimum_c3) + self.minimum_c3, 3)}")
        self.hslice = resize_image_ratio(self.hslice, 900, 900)
        self.hslice_display.set_image(self.hslice)

        vslice_copy = self.vslice_display.color_line(self.vslice, ratio, 2, self.color)
        self.vslice_display.set_image(vslice_copy)


class PSFDisplayWidget(QWidget):
    def __init__(self, parent = None, set_bounds = 1):
        super().__init__()
        self.parent = parent

        self.title = QLabel("")
        self.image_display = ImagesDisplayView()

        if set_bounds:
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

    """def set_max_size(self, size):
        self.image_display.setMaximumSize(size[0], size[1])"""

    def shorten_horizontal(self, image, margin: int = 4, lower_bound: float = 1e-05):
        '''This function crops the unnecessary zeroes on the sides of an image'''
        new_image = image.copy()
        size = image.shape[1]
        i = 0
        while max(image[:, i]) < lower_bound and max(image[:, size - i - 1]) < lower_bound:
            do_pop = i - margin >= 0
            if do_pop:
                new_image = np.delete(new_image, 0, axis=1)
                new_image = np.delete(new_image, -1, axis=1)
            i += 1
        return new_image

    def shorten_vertical(self, image, margin: int = 4, lower_bound: float = 1e-05):
        '''This function crops the unnecessary zeroes on top and bottom of an image'''
        new_image = image.copy()
        size = image.shape[0]
        i = 0
        while max(image[i, :]) < lower_bound and max(image[size - i - 1, :]) < lower_bound:
            do_pop = i - margin >= 0
            if do_pop:
                new_image = np.delete(new_image, 0, axis=0)
                new_image = np.delete(new_image, -1, axis=0)
            i += 1
        return new_image

    def shorten_bounds(self, image, margin: int = 4, lower_bound: float = 1e-05):
        self.shorten_vertical(image, margin, lower_bound)
        self.shorten_horizontal(image, margin, lower_bound)
        return image

    """def resize_image_to(self, image, h, w, keep_proportions = True):
        '''This function can be used to create a new image that is resized to the desired height(h)
        and width(w)'''
        size = image.shape
        y_factor = h/size[0]
        x_factor = w/size[1]
        assert y_factor > 0 and x_factor > 0, "invalid arguments"
        if keep_proportions:
            factor = min(y_factor, x_factor)
            y_factor = factor
            x_factor = factor

        resized_image = np.zeros([int(y_factor*size[0]), int(x_factor*size[1])])

        sample_L_x = 1/x_factor
        sample_L_y = 1/y_factor
        for i in range(int(y_factor*size[0])):
            y_index = sample_L_y * i
            y_index_float = y_index - float(y_index)
            y_next_index = int(y_index + sample_L_y)
            if y_next_index > size[0] - 1:
                y_next_index = size[0] - 1
            for j in range(int(x_factor*size[1])):
                x_index = sample_L_x*j
                x_index_float = x_index - float(x_index)
                x_next_index = int(x_index + sample_L_x)
                if x_next_index > size[1] - 1:
                    x_next_index = size[1] - 1
                topleft = (1 - x_index_float) * (1 - y_index_float) * image[int(y_index), int(x_index)]
                topright = x_index_float * (1 - y_index_float) * image[y_next_index, int(x_index)]
                botleft = (1 - x_index_float) * y_index_float * image[int(y_index), x_next_index]
                botright = x_index_float * y_index_float * image[y_next_index, x_next_index]
                resized_image[i][j] = topleft + topright + botleft + botright

        return resized_image"""

    def toRGB(self, image):
        '''Converts a grayscale image to RGB'''
        height, width, *channels = image.shape
        if not channels or channels[0] == 1:
            image_grayscale = image.astype(np.uint8)
            image = np.stack((image_grayscale,) * 3, axis=-1)
        return image

    def color_line(self, image, ratio, height, color : tuple):
        '''draws a horizontal line from the specified color at a given ratio of the image's height'''
        modified_image = self.toRGB(image.copy())
        h = modified_image.shape[0]

        line_index_min = int(h * ratio) - height
        line_index_min = max(0, min(h - 1, line_index_min))
        line_index_max = int(h * ratio) + height
        line_index_max = max(0, min(h - 1, line_index_max))

        modified_image[line_index_min:line_index_max, :, :] = np.array(color, dtype=np.uint8)
        return modified_image


class ChartDisplayWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.image_display = XYChartWidget()
        self.image_display.setMinimumSize(400, 400)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_display)

        self.setLayout(self.layout)
    def set_array(self, X, Y, Z = None):
        self.image_display.set_background("white")
        X, Y, Z = self.shorten_bounds(X, Y, Z)
        if Z is None:
            self.image_display.set_data(X, Y)
        else:
            self.image_display.set_data(X, [Y, Z])
        self.image_display.refresh_chart()

    def set_title(self, title: str):
        self.image_display.set_title(title)

    def shorten_bounds(self, x_array, y_array, second_y=None, margin: int = 4, lower_bound: float = 1e-05):
        '''This function performs an element_wise search in a list and tries to get the external zeroes out to get a
        smoother result

        the variable margin represents the nuber of zeroes that are left out so that the plot doesn't have non-zero
        values at the boundaries
        lower_bound is the threshold under which the values are considered to be zero

        The function is also built to ensure the graph remains centered'''
        two_graphs = second_y is not None
        if not two_graphs:
            second_y = None
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
                if two_graphs:
                    second_y = np.delete(second_y, 0)
                    second_y = np.delete(second_y, -1)
            i += 1
        return x_array, new_array, second_y

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreatmentWindow()
    window.show()
    sys.exit(app.exec())