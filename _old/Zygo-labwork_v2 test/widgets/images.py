# -*- coding: utf-8 -*-
"""*images_widget.py* file.

This file contains graphical elements to display images in a widget.
Image is coming from a file (JPG, PNG...) or an industrial camera (IDS, Basler...).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys, os
import numpy as np
import scipy
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.images.conversion import *


number_of_images = 5

def read_mat_file(file_path: str) -> dict:
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to load.
    :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
    """
    data = scipy.io.loadmat(file_path)
    return data

def write_mat_file(file_path, images: np.ndarray, masks: np.ndarray = None):
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to write.
    :param images: Set of images to save.
    :param masks: Set of masks to save. Default None.
    """
    data = {
        'Images': images
    }
    if masks is not None:
        data['Masks'] = masks
    scipy.io.savemat(file_path, data)


def split_3d_array(array_3d, size: int = 5):
    # Ensure the array has the expected shape
    if array_3d.shape[2]%size != 0:
        raise ValueError(f"The loaded array does not have the expected third dimension size of {size}.")
    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(array_3d.shape[2])]
    return arrays


def generate_images_grid(images: list[np.ndarray]):
    """Generate a grid with 5 images.
    The 6th image is the mean of the 4 first images.
    :param images: List of 5 images.
    """
    img_height, img_width = images[0].shape
    separator_size = 5
    # Global size
    total_height = 2 * img_height + separator_size  # 2 rows of images
    total_width = 3 * img_width + 2 * separator_size  # 3 columns of images
    # Empty image
    result = np.ones((total_height, total_width), dtype=np.uint8) * 255
    # Add each images
    result[0:img_height, 0:img_width] = images[0]
    result[0:img_height, img_width + separator_size:2 * img_width + separator_size] = images[1]
    result[0:img_height, 2 * img_width + 2 * separator_size:] = images[2]
    result[img_height + separator_size:, 0:img_width] = images[3]
    result[img_height + separator_size:, img_width + separator_size:2 * img_width + separator_size] = images[4]
    sum_image = (images[0] + images[1] + images[2] + images[3])/4
    sum_image = sum_image.astype(np.uint8)
    result[img_height + separator_size:, 2 * img_width + 2 * separator_size:] = sum_image
    return result

class Images:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.images_list = []
        self.images_sets_number = 0

    def add_set_images(self, images: list):
        """Add a new set of images."""
        if isinstance(images, list):
            if len(images) == self.set_size:
                self.images_list.append(images)
                self.images_sets_number += 1

    def reset_all_images(self):
        """Reset all images."""
        self.images_list.clear()
        self.images_sets_number = 0

    def get_number_of_sets(self) -> int:
        """Return the number of stored sets of images.
        :return: Number of stored sets of images.
        """
        return self.images_sets_number

    def get_images_set(self, index: int) -> list[np.ndarray]:
        """Return a set of N images.
        :param index: Index of the set to return.
        :return: List of images from the specified set.
        """
        if index <= self.images_sets_number:
            print(index)
            return self.images_list[index-1]
        return None

    def get_image_from_set(self, index: int, set_index: int = 1):
        """Return an image from its index in a specific set.
        :param index: Index of the image to return.
        :param set_index: Index of the set of the image. Default 1.
        """
        return self.images_list[set_index-1][index-1]

    def get_images_as_list(self):
        """Return all the stored images in a single list."""
        list = []
        for i in range(self.images_sets_number):
            set = self.get_images_set(i+1)
            list += set
        return list


if __name__ == '__main__':
    image1 = np.zeros((100,220))
    image2 = np.zeros((100,220))
    image3 = np.zeros((100,220))
    image4 = np.zeros((100,220))

    store = Images(3)
    store.add_set_images([image1, image2, image3])
    store.add_set_images([image2, image4, image3])

    set1 = store.get_images_set(1)
    set2 = store.get_images_set(2)


class ImagesChoice(QWidget):
    """Images Choice."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        ## Title of the widget
        self.label_images_choice_title = QLabel(translate("label_images_choice_title"))
        self.label_images_choice_title.setStyleSheet(styleH1)
        self.label_images_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ## Other graphical elements of the widget
        self.label_set_of_images = QLabel()
        self.label_set_of_images.setStyleSheet(styleH2)
        self.label_set_of_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_images = QLabel(translate("label_status_images"))
        self.label_status_images.setStyleSheet(styleH2)
        self.label_status_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_masks = QLabel(translate("label_status_masks"))
        self.label_status_masks.setStyleSheet(styleH2)
        self.label_status_masks.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widget set of images
        self.sets_of_images_number = 0
        self.sets_of_images_widget = QWidget()
        self.layout_set = QHBoxLayout()
        self.sets_of_images_widget.setLayout(self.layout_set)
        self.sets_button_list = []
        self.selected_set = 0

        # Widget images selection
        self.images_select_widget = QWidget()
        self.layout_images = QHBoxLayout()
        self.images_select_widget.setLayout(self.layout_images)
        self.images_button_select = []
        for i in range(number_of_images):
            button = QPushButton(str(i+1))
            button.setFixedWidth(40)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.display_image)
            self.images_button_select.append(button)
        '''
        button = QPushButton('ALL')
        button.setFixedWidth(40)
        button.clicked.connect(self.display_image)
        button.setStyleSheet(unactived_button)
        self.images_button_select.append(button)
        '''
        # Widget masks selection
        self.masks_select_widget = QWidget()
        self.layout_masks = QHBoxLayout()
        self.masks_select_widget.setLayout(self.layout_masks)
        self.masks_button_select = []

        # Add graphical elements in the layout
        self.layout.addWidget(self.label_images_choice_title)
        self.layout.addWidget(self.label_set_of_images)
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_images)
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_masks)
        self.layout.addWidget(self.masks_select_widget)


    def set_images_status(self, value: bool, index: int = 1):
        """Update images status.
        :param value: True if images are opened.
        :param index: Index of the image selected for display. Default 1.
        """
        if value:
            self.sets_of_images_number = self.parent.parent.images.get_number_of_sets()
            if self.sets_of_images_number > 1:
                self.label_set_of_images.setText(f'{self.sets_of_images_number} set(s) of images')
                for i in range(self.sets_of_images_number):
                    button = QPushButton(f'S{i + 1}')
                    button.setFixedWidth(40)
                    if i == 0:
                        button.setStyleSheet(actived_button)
                    else:
                        button.setStyleSheet(unactived_button)
                    button.clicked.connect(self.select_set)
                    self.sets_button_list.append(button)
                    self.layout_set.addWidget(self.sets_button_list[i])
            self.label_status_images.setText('Display image ?')
            for i in range(number_of_images):
                self.layout_images.addWidget(self.images_button_select[i])
            self.images_button_select[index-1].setStyleSheet(actived_button)
        else:
            self.label_status_images.setText('No Image')

    def set_masks_status(self, value: bool, number: int=0):
        """Update masks status.
        :param value: True if there is only one mask.
        :param number: Number of potential masks.
        """
        if value:
            self.label_status_masks.setText(f'{number} Mask(s) / Display ?')
            self.selected_set = 1
            for i in range(number):
                button = QPushButton(str(i + 1))
                button.setFixedWidth(40)
                button.setStyleSheet(unactived_button)
                button.clicked.connect(self.display_mask)
                self.masks_button_select.append(button)
                self.layout_masks.addWidget(self.masks_button_select[i])
        else:
            self.label_status_masks.setText('No Mask')

    def unactivate_buttons(self):
        """Set unactivated all the buttons."""
        for i in range(number_of_images):
            self.images_button_select[i].setStyleSheet(unactived_button)
        mask_number = self.parent.parent.masks.get_masks_number()
        for i in range(mask_number):
            self.masks_button_select[i].setStyleSheet(unactived_button)

    def select_set(self, event):
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        for i in range(self.sets_of_images_number):
            if sender == self.sets_button_list[i]:
                self.selected_set = i+1

    def display_image(self, event):
        """Action performed when an image is selected to be displayed."""
        try:
            self.unactivate_buttons()
            sender = self.sender()
            sender.setStyleSheet(actived_button)
            for i in range(number_of_images):
                if sender == self.images_button_select[i]:
                    image = self.parent.parent.images.get_image_from_set(i+1, self.selected_set)
                    self.parent.top_left_widget.set_image_from_array(image)
                    '''
                    if i != 5:
                    
                    else:
                        set_of_images = self.parent.parent.images.get_images_set(self.selected_set)
                        image = generate_images_grid(set_of_images)
                        self.parent.top_left_widget.set_image_from_array(image)
                    '''
        except Exception as e:
            print(f'display : {e}')

    def display_mask(self, event):
        """Action performed when an image is selected to be displayed."""
        self.unactivate_buttons()
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        try:
            mask_number = self.parent.parent.masks.get_masks_number()
            for i in range(mask_number):
                if sender == self.masks_button_select[i]:
                    image = self.parent.parent.images.get_image_from_set(1, self.selected_set)
                    mask, _ = self.parent.parent.masks.get_mask(i+1)
                    self.parent.top_left_widget.set_image_from_array(mask*image)
        except Exception as e:
            print(f'display_masks : {e}')

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

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
            else:
                self.layout.removeItem(item)


class ImagesDisplayWidget(QWidget):
    """
    Widget to display an image.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.width = 0
        self.height = 0
        # GUI Structure
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Objects
        self.image = None
        # GUI Elements
        self.image_display = QLabel('No Image to display')
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setScaledContents(False)
        self.layout.addWidget(self.image_display)

    def update_size(self, width, height, aoi: bool = False):
        """
        Update the size of this widget.
        """
        self.width = width
        self.height = height
        if self.image is not None:
            image_to_display = self.image
            if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
                image_to_display = resize_image_ratio(self.image, self.height-50, self.width-20)
            qimage = array_to_qimage(image_to_display)
            pmap = QPixmap.fromImage(qimage)
            self.image_display.setPixmap(pmap)

    def set_image_from_array(self, pixels: np.ndarray, aoi: bool = False, text: str = '') -> None:
        """
        Display a new image from an array (Numpy)
        :param pixels: Array of pixels to display.
        :param aoi: If True, print 'AOI' on the image.
        :param text: Text to display in the top of the image.
        """
        self.image = np.array(pixels, dtype='uint8')
        image_to_display = self.image.copy()
        image_to_display = np.squeeze(image_to_display)
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height-50, self.width-50)
        qimage = array_to_qimage(image_to_display)

        if aoi:
            painter = QPainter(qimage)
            painter.setPen(QColor(255, 255, 255))  # Couleur blanche pour le texte
            painter.setFont(QFont("Arial", 15))  # Police et taille
            painter.drawText(20, 20, 'AOI')
            painter.end()
        if text != '':
            painter = QPainter(qimage)
            painter.setPen(QColor(255, 255, 255))  # Couleur blanche pour le texte
            painter.setFont(QFont("Arial", 15))  # Police et taille
            painter.drawText(20, 20, text)
            painter.end()
        pmap = QPixmap.fromImage(qimage)
        self.image_display.setPixmap(pmap)

    def reset_image(self):
        """Display No image to display."""
        self.image_display.deleteLater()
        self.image_display = QLabel('No Image to display')
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setScaledContents(False)
        self.layout.addWidget(self.image_display)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = ImagesChoice(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())