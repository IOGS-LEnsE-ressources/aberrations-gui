# -*- coding: utf-8 -*-
"""*dataset.py* file.

./models/dataset.py contains DataSetModel class to manage sets of images and masks
from Zygo application.

Images are intensity measurements of interferences. All images have the same size.
A set of 5 images is necessary to be demodulated by the Hariharan phase
demodulation algorithm

Data are stored in MAT file, containing "Images" (set of 5 arrays in 2 dimensions),
"Masks" objects (array(s) in 2 dimensions - same size as images) and
"Masks_Type" list.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import numpy as np
from enum import Enum
from models.images import ImagesModel
from models.masks import MasksModel
from models.acquisition import AcquisitionModel
from utils.dataset_utils import DataSetState


class DataSetModel:
    """Class containing images data and parameters.
    Images are stored in sets of N images.
    """
    def __init__(self, set_size: int=5):
        """Default constructor.
        :param set_size: Size of a set of images.
        """
        self.set_size = set_size
        self.images_sets = ImagesModel(set_size)
        self.masks_sets = MasksModel()
        self.acquisition_mode = AcquisitionModel(set_size)
        self.data_set_state = DataSetState.NODATA

    def add_set_images(self, images: list) -> bool:
        """
        Add a new set of images.
        :param images: List of images to add.
        :return: True if the set of images is added.
        """
        state = self.images_sets.add_set_images(images)
        if state:
            self.data_set_state = DataSetState.IMAGES
        return state

    def get_images_sets(self, index: int=1) -> list[np.ndarray]:
        """
        Return the list of images of a specific set of images.
        :param index: Index of the set to get images list.
        :return: List of images of a specific set of images.
        """
        return self.images_sets.get_images_set(index)

    def load_images_set_from_file(self, filename: str = '') -> bool:
        """
        Load sets of images from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        state = self.images_sets.load_images_set_from_file(filename)
        if state:
            self.data_set_state = DataSetState.IMAGES
        return state

    def get_masks_list(self) -> list[np.ndarray]:
        """
        Return the list of the masks.
        :return: List of 2D-array.
        """
        return self.masks_sets.get_mask_list()

    def add_mask(self, mask: np.ndarray, type_m: str = ''):
        """Add a new mask to the list.
        :param mask: Mask to add to the list.
        :param type_m: Type of mask (Circular, Rectangular, Polygon).
        """
        self.masks_sets.add_mask(mask, type_m)
        self.data_set_state = DataSetState.MASKS

    def load_mask_from_file(self, filename: str = '') -> bool:
        """
        Load a set of mask from a MAT file.
        :param filename: Path of the MAT file.
        :return: True if file is loaded.
        """
        state = self.masks_sets.load_mask_from_file(filename)
        if state:
            self.data_set_state = DataSetState.MASKS
        return state


    def get_global_mask(self) -> np.ndarray:
        """
        Return the global resulting mask.
        :return: 2D-array.
        """
        return self.masks_sets.get_global_mask()

    def get_global_cropped_mask(self) -> np.ndarray:
        """
        Return the global resulting mask.
        :return: 2D-array.
        """
        return self.masks_sets.get_global_cropped_mask()

    def is_data_ready(self):
        """
        Check if a set of images and almost one mask are processed.
        :return: True if almost a set of images and a mask are ready.
        """
        if self.images_sets.get_number_of_sets() >= 1 and self.masks_sets.get_masks_number() >= 1:
            return True
        else:
            return False


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    number_of_images = 5
    data_set = DataSetModel(number_of_images)

    images_set = ImagesModel(number_of_images)
    if images_set.load_images_set_from_file('../_data/test3.mat'):
        print('Images OK')
        data_set.add_set_images(images_set.get_images_set(1))

    print(f'Number of sets = {data_set.images_sets.get_number_of_sets()}')
    if data_set.images_sets.get_number_of_sets() >= 1:
        image_1_1 = data_set.get_images_sets(1)
        if isinstance(image_1_1, list):
            plt.figure()
            plt.imshow(image_1_1[0], cmap='gray')
            plt.show()


