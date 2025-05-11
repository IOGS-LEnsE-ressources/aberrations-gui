# -*- coding: utf-8 -*-
"""*masks.py* file.

This file contains graphical elements to display and manage masks in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : nov/2024
"""
import sys, os

import matplotlib.pyplot as plt
import numpy as np
import cv2
import scipy

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTableWidget,
    QCheckBox, QMessageBox,
    QMainWindow, QDialog, QApplication
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QKeyEvent, QMouseEvent
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.images.conversion import *
from lensepy.pyqt6 import *


class Masks:
    """Class containing masks data and parameters.
    """
    def __init__(self):
        """Default constructor.
        """
        self.masks_list = []
        self.masks_number = 0
        self.mask_type = []
        self.mask_selected = []
        self.mask_inverted = []
        self.global_inverted = False

    def __str__(self):
        """Print function."""
        out_str = 'Masks List\n'
        for i in range(self.masks_number):
            out_str += f'\tMask {i+1} : {self.mask_type[i]}\n'
        return out_str

    def get_mask(self, index: int) -> np.ndarray:
        """Return the selected mask.
        :param index: Index of the mask to return.
        """
        if index <= self.masks_number:
            if self.mask_inverted[index-1] is True:
                mask = np.logical_not(self.masks_list[index-1])
            else:
                mask = self.masks_list[index-1]
            return mask, self.mask_type[index-1]
        return None

    def get_type(self, index: int) -> str:
        """Return the type of the selected mask.
        :param index: Index of the mask to get the type.
        :return: Type of the mask.
        """
        if index <= self.masks_number:
            return self.mask_type[index-1]
        return None

    def get_mask_list(self) -> list[np.ndarray]:
        """Return all the masks in a list."""
        return self.masks_list

    def add_mask(self, mask: np.ndarray, type_m: str = ''):
        """Add a new mask to the list.
        :param mask: Mask to add to the list.
        :param type_m: Type of mask (Circular, Rectangular, Polygon).
        """
        self.masks_list.append(mask)
        self.mask_type.append(type_m)
        self.mask_selected.append(True)
        self.mask_inverted.append(False)
        self.masks_number += 1

    def reset_masks(self):
        """Reset all the masks."""
        self.masks_list.clear()
        self.mask_type.clear()
        self.mask_selected.clear()
        self.mask_inverted.clear()
        self.masks_number = 0

    def del_mask(self, index: int):
        """Remove the specified mask.
        :param index: Index of the mask to remove.
        """
        self.masks_list.pop(index-1)
        self.mask_type.pop(index-1)
        self.mask_selected.pop(index-1)
        self.mask_inverted.pop(index-1)
        self.masks_number -= 1

    def select_mask(self, index: int, value: bool = True):
        """Select or unselect a mask.
        :param index: Index of the mask to select.
        :param value: False to unselect. Default True to select.
        """
        self.mask_selected[index-1] = value

    def invert_mask(self, index: int, value: bool = True):
        """Invert or not a mask.
        :param index: Index of the mask to invert.
        :param value: False to uninvert. Default True to invert.
        """
        self.mask_inverted[index-1] = value

    def invert_global_mask(self, value: bool = True):
        """Invert the global mask.
        :param value: False to uninvert. Default True to invert.
        """
        self.global_inverted = value

    def get_global_mask(self):
        """Return the resulting mask."""
        try:
            if self.masks_number > 0:
                global_mask = np.zeros_like(self.masks_list[0]).astype(bool)
                for i, simple_mask in enumerate(self.masks_list):
                    if self.mask_selected[i]:
                        simple_mask = simple_mask > 0.5
                        if self.mask_inverted[i]:
                            simple_mask = np.logical_not(simple_mask)
                        global_mask = np.logical_or(global_mask, simple_mask)
                if self.global_inverted:
                    return np.logical_not(global_mask)
                else:
                    return global_mask
            else:
                return None
        except Exception as e:
            print(f'get_global_mask {e}')

    def get_masks_number(self):
        """Return the number of stored masks."""
        return self.masks_number

    def is_mask_selected(self, index: int):
        """Return the status of the selection of a mask.
         :param index: Index of the mask.
         :return: True if the mask is selected.
         """
        return self.mask_selected[index-1]

    def is_mask_inverted(self, index: int):
        """Return the status of the inversion of a mask.
         :param index: Index of the mask.
         :return: True if the mask is inverted.
         """
        return self.mask_inverted[index-1]


class MasksTableWidget(QTableWidget):

    def __init__(self, parent=None):
        """Default constructor.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.masks_list = Masks()
        self.apply_checkbox_list = []
        self.inverse_checkbox_list = []
        self.delete_button_list = []
        self.show_button_list = []
        self.setColumnCount(5)  # 5 columns
        self.setHorizontalHeaderLabels(["Select", "Invert", "Type", "Delete", "Show"])
        self.verticalHeader().setVisible(False)
        ## Global parameters
        self.insertRow(self.rowCount())
        # Global unselect
        self.button_unselect = QPushButton(f'ALL')
        self.button_unselect.setStyleSheet(styleCheckbox)
        self.button_unselect.clicked.connect(self.global_changed)
        button_widget = qobject_to_widget(self.button_unselect)
        self.setCellWidget(0, 0, button_widget)
        # Global invert
        self.checkbox_invert = QCheckBox()
        self.checkbox_invert.stateChanged.connect(self.global_changed)
        check_widget = qobject_to_widget(self.checkbox_invert)
        self.setCellWidget(0, 1, check_widget)
        # Global label
        label = QLabel('GLOBAL')
        label.setStyleSheet(styleH3)
        label_widget = qobject_to_widget(label)
        self.setCellWidget(0,2, label_widget)
        # Global delete
        self.button_delete_all = QPushButton(translate('delete_all'))
        self.button_delete_all.setStyleSheet('background:red; color:white;')
        self.button_delete_all.clicked.connect(self.global_changed)
        delete_all = qobject_to_widget(self.button_delete_all)
        self.setCellWidget(0, 3, delete_all)
        # Global show
        self.button_show_selection = QPushButton(translate('show_selection'))
        self.button_show_selection.setStyleSheet(styleCheckbox)
        self.button_show_selection.clicked.connect(self.global_changed)
        show_selection = qobject_to_widget(self.button_show_selection)
        self.setCellWidget(0, 4, show_selection)

    def erase_all(self):
        """Delete all the rows and reconstruct the first line (header)."""
        self.apply_checkbox_list = []
        self.inverse_checkbox_list = []
        self.delete_button_list = []
        self.show_button_list = []

        self.clearContents()
        self.setRowCount(0)
        
        ## Global line - header
        self.insertRow(self.rowCount())
        button_widget = qobject_to_widget(self.button_unselect)
        self.setCellWidget(0, 0, button_widget)
        check_widget = qobject_to_widget(self.checkbox_invert)
        self.setCellWidget(0, 1, check_widget)
        label = QLabel('GLOBAL')
        label.setStyleSheet(styleH3)
        label_widget = qobject_to_widget(label)
        self.setCellWidget(0,2, label_widget)
        delete_all = qobject_to_widget(self.button_delete_all)
        self.setCellWidget(0, 3, delete_all)
        show_selection = qobject_to_widget(self.button_show_selection)
        self.setCellWidget(0, 4, show_selection)
        

    def set_masks(self, masks: Masks):
        """Add a set of masks (type Masks).
        :param masks: Set of masks.
        """
        # Erase previous data
        self.erase_all()
        # Create a new set of masks
        self.masks_list = masks
        number_of_rows = self.masks_list.get_masks_number()
        for row in range(number_of_rows):
            self.insertRow(self.rowCount())
        self.create_elements()
        self.update_display()


    def print_list(self):
        """Print the list of masks."""
        print(self.masks_list)

    def create_elements(self):
        """Create the Masks options display."""
        number_of_rows = self.masks_list.get_masks_number()
        # For each mask : select / invert / type / del / show
        for row in range(number_of_rows):
            # Create checkbox for mask selection (first column)
            checkbox_item = QCheckBox()
            checkbox_item.setChecked(self.masks_list.is_mask_selected(row+1))
            checkbox_item.stateChanged.connect(self.checkbox_apply_mask_changed)
            check_widget = qobject_to_widget(checkbox_item)
            self.apply_checkbox_list.append(checkbox_item)
            self.setCellWidget(row+1, 0, check_widget)
            # Create checkbox for mask inversion (second column)
            checkbox_item = QCheckBox()
            checkbox_item.setChecked(self.masks_list.is_mask_inverted(row+1))
            checkbox_item.stateChanged.connect(self.checkbox_inverse_mask_changed)
            check_widget = qobject_to_widget(checkbox_item)
            self.inverse_checkbox_list.append(checkbox_item)
            self.setCellWidget(row+1, 1, check_widget)
            # Create label for mask type (third column)
            label = QLabel(f'{self.masks_list.get_type(row+1)}')
            label_widget = qobject_to_widget(label)
            self.setCellWidget(row+1, 2, label_widget)
            # Create button for mask deletion (fourth column)
            button = QPushButton(f'{translate("del_mask")} {row+1}')
            button.setStyleSheet(styleCheckbox)
            button.clicked.connect(self.button_erase_mask_clicked)
            button_widget = qobject_to_widget(button)
            self.delete_button_list.append(button)
            self.setCellWidget(row+1, 3, button_widget)
            # Create button for mask showing (fifth column)
            button = QPushButton(f'{translate("show_mask")} {row+1}')
            button.setStyleSheet(styleCheckbox)
            button.clicked.connect(self.button_show_mask_clicked)
            button_widget = qobject_to_widget(button)
            self.show_button_list.append(button)
            self.setCellWidget(row+1, 4, button_widget)

        # Resize columns to fit content
        self.resizeColumnsToContents()

    def update_display(self):
        """Update Masks options widget display."""
        # All / Global : unselect / invert / __ / del / show
        self.checkbox_invert.setChecked(self.masks_list.global_inverted)

        number_of_rows = self.masks_list.get_masks_number()
        # For each mask : select / invert / type / del / show
        for row in range(number_of_rows):
            # Update checkbox for mask selection (first column)
            self.apply_checkbox_list[row].setChecked(self.masks_list.is_mask_selected(row+1))
            # Update checkbox for mask inversion (second column)
            self.inverse_checkbox_list[row].setChecked(self.masks_list.is_mask_inverted(row+1))
            # Create label for mask type (third column)
            label = QLabel(f'{self.masks_list.get_type(row+1)}')
            label_widget = qobject_to_widget(label)
            self.setCellWidget(row+1, 2, label_widget)

        # Resize columns to fit content
        self.resizeColumnsToContents()

    def global_changed(self):
        """Action performed when a global button changed."""
        sender = self.sender()
        if sender == self.button_unselect:
            value = not self.masks_list.is_mask_selected(1)
            for i in range(self.masks_list.get_masks_number()):
                self.masks_list.select_mask(i+1, value)
            self.update_display()
            self.parent.parent.masks_changed = True

        elif sender == self.checkbox_invert:
            value = self.checkbox_invert.isChecked()
            self.parent.parent.parent.masks.invert_global_mask(value)
            self.parent.parent.masks_changed = True
            

        elif sender == self.button_delete_all:
            reply = QMessageBox.question(self, 'Delete all masks',
                                         'Do you really want to delete all the masks ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.parent.parent.parent.masks.reset_masks()
                self.update_display()
                self.parent.parent.action_masks_visualization()
            self.parent.parent.masks_changed = True

        elif sender == self.button_show_selection:
            self.parent.parent.action_masks_visualization()
            self.parent.parent.masks_changed = True

    def checkbox_apply_mask_changed(self):
        """Action performed when an invert checkbox changed."""
        checkbox = self.sender()
        index = -1
        for i in range(len(self.apply_checkbox_list)):
            if checkbox == self.apply_checkbox_list[i]:
                index = i
                self.masks_list.select_mask(index+1, checkbox.isChecked())
                self.parent.parent.action_masks_visualization()

    def checkbox_inverse_mask_changed(self):
        """Action performed when an invert checkbox changed."""
        checkbox = self.sender()
        for i in range(len(self.inverse_checkbox_list)):
            if checkbox == self.inverse_checkbox_list[i]:
                index = i
                self.masks_list.invert_mask(index+1, checkbox.isChecked())
                self.update_display()
                self.parent.parent.action_masks_visualization()

    def button_show_mask_clicked(self):
        """Action performed when a show button is clicked.."""
        button = self.sender()
        index = -1
        for i in range(len(self.show_button_list)):
            print(f'show mask = {i}')
            if button == self.show_button_list[i]:
                index = i
                print(f'Display {index+1}')
                # Show the ith mask on the image
                self.parent.parent.action_masks_visualization(str(index+1))

    def button_erase_mask_clicked(self):
        """Action performed when a mask deletion is required."""
        reply = QMessageBox.question(self, translate('delete_mask_box'),
                                     translate('delete_mask_box_message'),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            button = self.sender()
            index = -1
            for i in range(len(self.delete_button_list)):
                if button == self.delete_button_list[i]:
                    index = i
                    self.parent.parent.parent.masks.del_mask(index+1)
                    self.update_display()
                    if self.masks_list.get_masks_number() == 0:
                        self.parent.parent.parent.mask_created = False
                        self.parent.parent.update_menu()
                    self.parent.parent.action_masks_visualization()


class MasksOptionsWidget(QWidget):
    """
    Masks Options widget of the application.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        self.label_masks_option_title = QLabel(translate("label_masks_option_title"))
        self.label_masks_option_title.setStyleSheet(styleH1)
        self.label_masks_option_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Table for displaying masks
        self.table_widget = MasksTableWidget(self)
        self.table_widget.set_masks(self.parent.parent.masks)

        # Add graphical elements in the layout
        self.layout.addWidget(self.label_masks_option_title)
        self.layout.addStretch()
        self.layout.addWidget(self.table_widget)
        self.layout.addStretch()

    def update_display(self):
        """Update the masks list."""
        self.table_widget.update_display()

    def set_masks(self, masks: Masks):
        """Set a sets of masks from a Masks object."""
        self.table_widget.set_masks(masks)


class CircularMaskSelection(QDialog):
    """
    A dialog for selecting a circular mask on an image.

    This dialog allows the user to define a circular region on an image. Points are selected
    by clicking on the image, and a circular mask is generated based on these points.

    Attributes
    ----------
    image : np.ndarray
        The image on which the mask will be drawn.
    points : list
        List of points selected by the user.
    mask : np.ndarray
        The binary mask created.

    Methods
    -------
    keyPressEvent(event)
        Handles key press events.
    get_points_circle(event)
        Captures points clicked by the user to define the circle.
    draw_point(x, y)
        Draws a point on the image at the specified coordinates.
    find_circle_center(x0, y0, x1, y1, x2, y2)
        Finds the center of a circle given three points.
    draw_circle()
        Draws a circle based on the points selected by the user.
    create_circular_mask(x_center, y_center, radius)
        Creates a circular mask.
    close_window()
        Closes the dialog window.

    See Also
    --------
    RectangularMaskSelection, PolygonalMaskSelection

    Notes
    -----
    This dialog is part of a photonics labwork interface developed at LEnsE - Institut d'Optique.

    Example
    -------
    image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    dialog = CircularMaskSelection(image)
    dialog.exec()
    """

    def __init__(self, pixel: np.ndarray,
                 help_text: str = 'Select 3 different points and then Click Enter') -> None:
        """
        Initializes the CircularMaskSelection dialog.

        Parameters
        ----------
        pixel : np.ndarray
            The image on which the mask will be drawn.
        help_text : str
            Text displayed to help the user.
        """
        super().__init__()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.width = screen_geometry.width() - 50
        self.height = screen_geometry.height() - 150
        self.setFixedSize(self.width, self.height)

        # Initialize layout and image attributes
        self.layout = QGridLayout()
        self.image = np.array(pixel.copy(), dtype='uint8')
        # Convert image to QImage and QPixmap for display and adjust to maximum size of the screen
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height-50, self.width)
        else:
            image_to_display = self.image

        self.qimage = array_to_qimage(image_to_display)
        self.pixmap = QPixmap.fromImage(self.qimage)

        self.ratio = self.image.shape[1] / image_to_display.shape[1]

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Create a QLabel to display help
        self.help = QLabel(help_text)

        # Create a QLabel to display the image
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(self.pixmap)

        # Add the label to the layout
        self.layout.addWidget(self.help)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, 95)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_circle

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Parameters
        ----------
        event : QKeyEvent
            The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.accept()

    def get_points_circle(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the circle.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event.
        """
        # Enable drawing points and limit to three points
        self.can_draw = True
        print(f'N = {len(self.points) }')
        if self.can_draw and len(self.points) < 3:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 3:
                self.draw_circle()
                self.can_draw = False

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.
        """
        # Draw a point on the point layer pixmap
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.blue, point_size)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()

        # Combine the point layer pixmap with the original image pixmap
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update the label pixmap to show the combined image
        self.label.setPixmap(combined_pixmap)

    def find_circle_center(self, x0: int, y0: int, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int]:
        """
        Finds the center of a circle given three points.

        Parameters
        ----------
        x0, y0 : int
            Coordinates of the first point.
        x1, y1 : int
            Coordinates of the second point.
        x2, y2 : int
            Coordinates of the third point.

        Returns
        -------
        tuple
            Coordinates of the circle center (x, y).
        """
        # Calculate midpoints and perpendicular bisectors
        mid_x_01 = (x0 + x1) / 2
        mid_y_01 = (y0 + y1) / 2
        mid_x_02 = (x0 + x2) / 2
        mid_y_02 = (y0 + y2) / 2

        if x0 == x1:
            slope_perp_01 = None
            intercept_perp_01 = mid_x_01
        else:
            slope_perp_01 = -1 / ((y1 - y0) / (x1 - x0))
            intercept_perp_01 = mid_y_01 - slope_perp_01 * mid_x_01

        if x0 == x2:
            slope_perp_02 = None
            intercept_perp_02 = mid_x_02
        else:
            slope_perp_02 = -1 / ((y2 - y0) / (x2 - x0))
            intercept_perp_02 = mid_y_02 - slope_perp_02 * mid_x_02

        # Calculate circle center coordinates
        if slope_perp_01 is None or slope_perp_02 is None:
            if slope_perp_01 is None:
                X = mid_x_01
                Y = slope_perp_02 * X + intercept_perp_02
            else:
                X = mid_x_02
                Y = slope_perp_01 * X + intercept_perp_01
        else:
            X = (intercept_perp_02 - intercept_perp_01) / \
                (slope_perp_01 - slope_perp_02)
            Y = slope_perp_01 * X + intercept_perp_01

        return X, Y

    def draw_circle(self) -> None:
        """
        Draws a circle based on the points selected by the user.
        """
        try:
            # Get the last three points selected by the user
            x0, y0 = self.points[-3]
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]

            # Find the center of the circle and radius
            x_center, y_center = self.find_circle_center(
                x0, y0, x1, y1, x2, y2)
            x_center = int(x_center)
            y_center = int(y_center)
            radius = int(np.sqrt((x_center-x0)**2+(y_center-y0)**2))

            # Draw the circle on the pixmap
            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(Qt.GlobalColor.blue,2)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(x_center, y_center), radius, radius)
            painter.end()

            # Combine the circle with the point layer pixmap
            combined_pixmap = self.pixmap.copy()
            painter = QPainter(combined_pixmap)
            painter.drawPixmap(0, 0, self.point_layer)
            painter.end()

            # Update the label pixmap to show the combined image
            self.label.setPixmap(combined_pixmap)

            # Update mask
            self.mask = self.create_circular_mask(x_center*self.ratio, y_center*self.ratio, radius*self.ratio)

        except Exception as e:
            print(f'Exception - circle_mask_draw {e}')

    def create_circular_mask(self, x_center: int, y_center: int, radius: int) -> np.ndarray:
        """
        Creates a circular mask.

        Parameters
        ----------
        x_center : int
            The x-coordinate of the circle center.
        y_center : int
            The y-coordinate of the circle center.
        radius : int
            The radius of the circle.

        Returns
        -------
        np.ndarray
            The binary mask with the circular region set to True.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Create grid of coordinates
        y, x = np.ogrid[:self.image.shape[0], :self.image.shape[1]]

        # Calculate distance from center
        dist_from_center = np.sqrt((x - x_center)**2 + (y - y_center)**2)

        # Set mask values inside the circle to 1
        mask[dist_from_center <= radius] = 1
        mask = mask > 0.5
        return mask


class RectangularMaskSelection(QDialog):
    """
    A dialog for selecting a rectangular mask on an image.

    Attributes
    ----------
    image : np.ndarray
        The image on which the mask will be drawn.
    points : list
        List of points selected by the user defining the rectangle.
    mask : np.ndarray
        The binary mask created.

    Methods
    -------
    keyPressEvent(event)
        Handles key press events.
    get_points_rectangle(event)
        Captures points clicked by the user to define the rectangle.
    draw_point(x, y)
        Draws a point on the image at the specified coordinates.
    draw_rectangle()
        Draws a rectangle based on the points selected by the user.
    create_rectangular_mask(x1, y1, x2, y2)
        Creates a rectangular mask.
    close_window()
        Closes the dialog window.

    See Also
    --------
    CircularMaskSelection, PolygonalMaskSelection

    Notes
    -----
    This dialog is part of a photonics labwork interface developed at LEnsE - Institut d'Optique.

    Examples
    --------
    image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    dialog = RectangularMaskSelection(image)
    dialog.exec()
    """

    def __init__(self, pixel: np.ndarray,
                 help_text: str = 'Select 2 different points and then Click Enter') -> None:
        """
        Initializes the RectangularMaskSelection dialog.

        Parameters
        ----------
        pixel : np.ndarray
            The image on which the mask will be drawn.
        help_text : str
            Text displayed to help the user.
        """
        super().__init__()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.width = screen_geometry.width() - 50
        self.height = screen_geometry.height() - 150
        self.setFixedSize(self.width, self.height)

        # Initialize layout and image attributes
        self.layout = QGridLayout()
        self.image = np.array(pixel.copy(), dtype='uint8')
        # Convert image to QImage and QPixmap for display and adjust to maximum size of the screen
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height - 50, self.width)

        self.qimage = array_to_qimage(image_to_display)
        self.pixmap = QPixmap.fromImage(self.qimage)

        self.ratio = self.image.shape[1] / image_to_display.shape[1]

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Create a QLabel to display help
        self.help = QLabel(help_text)

        # Create a QLabel to display the image
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        # Add the label to the layout
        self.layout.addWidget(self.help)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, 95)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_rectangle

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Parameters
        ----------
        event : QKeyEvent
            The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.accept()

    def get_points_rectangle(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the rectangle.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event.
        """
        # Enable drawing points and limit to two points
        self.can_draw = True
        if self.can_draw and len(self.points) < 2:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 2:
                self.draw_rectangle()
                self.can_draw = False

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.
        """
        # Draw a point on the point layer pixmap
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.blue, point_size)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()

        # Combine the point layer pixmap with the original image pixmap
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update the label pixmap to show the combined image
        self.label.setPixmap(combined_pixmap)

    def draw_rectangle(self) -> None:
        """
        Draws a rectangle based on the points selected by the user.
        """
        # Get the two points defining the rectangle
        x1, y1 = self.points[-2]
        x2, y2 = self.points[-1]

        # Draw the rectangle on the pixmap
        painter = QPainter(self.pixmap)
        pen = QPen(QColor(0, 0, 255), 2)
        painter.setPen(pen)
        painter.drawRect(x1, y1, (x2-x1), (y2-y1))
        painter.end()

        # Combine the rectangle with the point layer pixmap
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update the label pixmap to show the combined image
        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_rectangular_mask(x1, y1, x2, y2)

    def create_rectangular_mask(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """
        Creates a rectangular mask.

        Parameters
        ----------
        x1, y1 : int
            Coordinates of the top-left corner of the rectangle.
        x2, y2 : int
            Coordinates of the bottom-right corner of the rectangle.

        Returns
        -------
        np.ndarray
            The binary mask with the rectangular region set to True.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)
        # Invert y1,y2 or/and x1,x2 if not in ascending order
        if y2 < y1:
            y1, y2 = y2, y1
        if x2 < x1:
            x1, x2 = x2, x1
        # Set mask values inside the rectangle to 1
        mask[int(y1*self.ratio):int(y2*self.ratio), int(x1*self.ratio):int(x2*self.ratio)] = 1
        mask = mask > 0.5
        return mask


class PolygonalMaskSelection(QDialog):
    """
    A dialog for selecting a polygonal mask on an image.

    Attributes
    ----------
    image : np.ndarray
        The image on which the mask will be drawn.
    points : list
        List of points selected by the user defining the polygon.
    mask : np.ndarray
        The binary mask created.

    Methods
    -------
    keyPressEvent(event)
        Handles key press events.
    get_points_polygon(event)
        Captures points clicked by the user to define the polygon.
    draw_point(x, y)
        Draws a point on the image at the specified coordinates.
    draw_polygon()
        Draws a polygon based on the points selected by the user.
    create_polygonal_mask()
        Creates a polygonal mask based on the points selected.
    close_window()
        Closes the dialog window.

    See Also
    --------
    CircularMaskSelection, RectangularMaskSelection

    Notes
    -----
    This dialog is part of a photonics labwork interface developed at LEnsE - Institut d'Optique.

    Examples
    --------
    image = np.random.randint(0, 255, (600, 600), dtype=np.uint8)
    dialog = PolygonalMaskSelection(image)
    dialog.exec()
    """

    def __init__(self, pixel: np.ndarray,
                 help_text: str = 'Select N different points, the last one must be at the'
                                  ' same place as the first one and then Click Enter') -> None:
        """
        Initializes the PolygonalMaskSelection dialog.

        Parameters
        ----------
        pixel : np.ndarray
            The image on which the mask will be drawn.
        help_text : str
            Text displayed to help the user.
        """
        super().__init__()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.width = screen_geometry.width() - 50
        self.height = screen_geometry.height() - 150
        self.setFixedSize(self.width, self.height)

        # Initialize layout and image attributes
        self.layout = QGridLayout()
        self.image = np.array(pixel.copy(), dtype='uint8')
        # Convert image to QImage and QPixmap for display and adjust to maximum size of the screen
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height - 50, self.width)

        self.qimage = array_to_qimage(image_to_display)
        self.pixmap = QPixmap.fromImage(self.qimage)

        self.ratio = self.image.shape[1] / image_to_display.shape[1]

        # Create a pixmap layer for drawing points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        # Create a QLabel to display help
        self.help = QLabel(help_text)

        # Create a QLabel to display the image
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        # Add the label to the layout
        self.layout.addWidget(self.help)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, 95)

        # Initialize points list and mask array
        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        # Assign mousePressEvent to capture points
        self.label.mousePressEvent = self.get_points_polygon

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handles key press events.

        Parameters
        ----------
        event : QKeyEvent
            The key event.
        """
        # Close dialog on Enter or Return key press
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.accept()

    def get_points_polygon(self, event: QMouseEvent) -> None:
        """
        Captures points clicked by the user to define the polygon.

        Parameters
        ----------
        event : QMouseEvent
            The mouse event.
        """
        # Enable drawing points
        self.can_draw = True
        limit = 10 * self.ratio  # px

        # Get the position of the mouse click
        pos = event.pos()

        # Add the point to the list of polygon points
        self.points.append((pos.x(), pos.y()))

        # Draw the point on the image
        self.draw_point(pos.x(), pos.y())

        # Draw the polygon if the user has selected more than one point and the last point is close to the first point
        dist = (self.points[-1][0] - self.points[0][0])**2+(self.points[-1][1] - self.points[0][1])**2
        if len(self.points) > 1 and dist < limit**2:
            self.draw_polygon()
            self.can_draw = False

    def draw_point(self, x: int, y: int) -> None:
        """
        Draws a point on the image at the specified coordinates.

        Parameters
        ----------
        x : int
            The x-coordinate of the point.
        y : int
            The y-coordinate of the point.
        """
        # Draw a point on the point layer pixmap
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.blue, point_size)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()

        # Combine the point layer pixmap with the original image pixmap
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update the label pixmap to show the combined image
        self.label.setPixmap(combined_pixmap)

    def draw_polygon(self) -> None:
        """
        Draws a polygon based on the points selected by the user and updates the mask.

        Draws a polygon using the points stored in `self.points` and updates the displayed image
        (`self.label`) and the mask (`self.mask`) accordingly.

        Notes
        -----
        This method assumes `QPoint` and `QPixmap` are correctly imported from PyQt6.QtCore and PyQt6.QtGui,
        respectively. Ensure `self.points`, `self.pixmap`, `self.point_layer`, `self.label`, and `self.mask`
        are initialized correctly before calling this method.

        """
        # Convert points to QPoint objects
        points = [QPoint(self.points[i][0], self.points[i][1])
                  for i in range(len(self.points))]

        # Draw polygon on the main pixmap
        painter = QPainter(self.pixmap)
        pen = QPen(QColor(0, 0, 255), 2)
        painter.setPen(pen)
        painter.drawPolygon(points)
        painter.end()

        # Update combined pixmap to show polygon and points
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        # Update label with the combined pixmap
        self.label.setPixmap(combined_pixmap)

        # Update mask with the newly drawn polygon
        self.mask = self.create_polygonal_mask()

    def create_polygonal_mask(self) -> np.ndarray:
        """
        Creates a polygonal mask based on the points selected by the user.

        Returns
        -------
        np.ndarray
            The binary mask with the polygonal region set to True.
        """
        # Create an empty mask
        mask = np.zeros_like(self.image, dtype=np.uint8)

        # Create a list of vertices for the polygon
        vertices = []
        for point in self.points:
            # Swap x and y for numpy indexing
            vertices.append((int(point[0]*self.ratio), int(point[1]*self.ratio)))

        # Convert the list of vertices to numpy array format
        vertices = np.array([vertices], dtype=np.int32)

        # Fill the polygon region in the mask with 1
        cv2.fillPoly(mask, vertices, 1)
        mask = mask > 0.5
        return mask


# %% Example
if __name__ == '__main__':
    app = QApplication(sys.argv)
    image = np.random.randint(0, 255, (400, 600))
    try:
        main = CircularMaskSelection(image)
    except Exception as e:
        print(e)
    main.show()
    sys.exit(app.exec())



