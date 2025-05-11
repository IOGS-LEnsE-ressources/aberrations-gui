# -*- coding: utf-8 -*-
"""
ContourWidget for displaying contour lines of a surface in 2D.

---------------------------------------
(c) 2024 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2024/06/13

Authors
-------
    Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import numpy as np
import sys
import matplotlib.pyplot as plt  # Import matplotlib for contour plotting

import pyqtgraph as pg  # Import pyqtgraph for PyQt integration

from lensepy.css import *  # Import CSS styles if needed

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"


class ContourWidget(QWidget):
    """
    Widget used to display contour lines of a surface chart.

    Attributes
    ----------
    title : str
        Title of the contour plot widget.
    plot_chart_widget : pg.PlotWidget
        pyQtGraph PlotWidget to display the contour plot.
    plot_x_data : np.ndarray
        X-axis values to display.
    plot_y_data : np.ndarray
        Y-axis values to display.
    plot_z_data : np.ndarray
        Z-axis values to display.
    contour_plot : matplotlib.contour.QuadContourSet or None
        Contour plot object.

    Methods
    -------
    set_data(x_axis: np.ndarray, y_axis: np.ndarray, z_axis: np.ndarray) -> None
        Set the X, Y, and Z axis data to display on the contour plot.
    refresh_chart() -> None
        Refresh the data and display the contour plot.
    set_title(title: str) -> None
        Set the title of the contour plot.
    set_information(infos: str) -> None
        Set information text displayed below the contour plot.
    set_background(css_color: str) -> None
        Set the background color of the widget.
    clear_graph() -> None
        Clear the contour plot.
    disable_chart() -> None
        Remove all widgets from the layout.
    enable_chart() -> None
        Add and display all widgets in the layout.
    """

    def __init__(self) -> None:
        """
        Initialize the 2D contour plot widget.
        """
        super().__init__()
        self.title: str = ''  # Initialize title as an empty string
        self.layout: QVBoxLayout = QVBoxLayout()  # Create a vertical layout for the widget

        self.master_layout: QVBoxLayout = QVBoxLayout()  # Create a master layout for the widget
        self.master_widget: QWidget = QWidget()  # Create a master widget to hold the layout

        # Title label setup
        self.title_label: QLabel = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        # Information label setup
        self.info_label: QLabel = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)

        # pyQtGraph PlotWidget setup
        self.plot_chart_widget: pg.PlotWidget = pg.PlotWidget()
        # self.plot_chart_widget.setMinimumWidth(400)
        # self.plot_chart_widget.setMinimumHeight(400)

        # Initialize Numpy arrays for X, Y, and Z data
        self.plot_x_data: np.ndarray = np.array([])
        self.plot_y_data: np.ndarray = np.array([])
        self.plot_z_data: np.ndarray = np.array([])

        # Initialize contour plot object to None
        self.contour_plot = None

        # Set up the layout hierarchy
        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_data(self, x_axis: np.ndarray, y_axis: np.ndarray, z_axis: np.ndarray) -> None:
        """
        Set the X, Y, and Z axis data to display on the contour plot.

        Parameters
        ----------
        x_axis : np.ndarray
            X-axis values to display.
        y_axis : np.ndarray
            Y-axis values to display.
        z_axis : np.ndarray
            Z-axis values to display.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method sets the data for the X, Y, and Z axes that will be used to generate the contour plot.
        """
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis
        self.plot_z_data = z_axis

    def refresh_chart(self) -> None:
        """
        Refresh the data and display the contour plot.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method refreshes the contour plot using the current X, Y, and Z data.
        """
        if self.contour_plot:
            self.plot_chart_widget.clear()

        x = self.plot_x_data
        y = self.plot_y_data
        z = self.plot_z_data

        # Create a contour plot using matplotlib
        fig, ax = plt.subplots()
        CS = ax.contour(x, y, z, levels=10)
        
        for collection in CS.collections:
            path = collection.get_paths()
            for p in path:
                vertices = p.vertices
                self.plot_chart_widget.plot(vertices[:, 0], vertices[:, 1], pen=BLUE_IOGS)

        plt.close(fig)

        self.plot_chart_widget.setXRange(x.min(), x.max())
        self.plot_chart_widget.setYRange(y.min(), y.max())
        self.plot_chart_widget.setAspectLocked(True)  # Lock the aspect ratio to ensure orthonormal graph
        self.adjustSize()

    def set_title(self, title: str) -> None:
        """
        Set the title of the contour plot.

        Parameters
        ----------
        title : str
            Title of the contour plot.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the title displayed at the top of the contour plot widget.
        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos: str) -> None:
        """
        Set information text displayed below the contour plot.

        Parameters
        ----------
        infos : str
            Information to display below the contour plot.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the information text displayed below the contour plot.
        """
        self.info_label.setText(infos)

    def set_background(self, css_color: str) -> None:
        """
        Set the background color of the widget.

        Parameters
        ----------
        css_color : str
            Color in CSS style.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the background color of the widget using CSS styles.
        """
        self.plot_chart_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self) -> None:
        """
        Clear the contour plot.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method clears the displayed contour plot.
        """
        self.plot_chart_widget.clear()

    def disable_chart(self) -> None:
        """
        Remove all widgets from the layout.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method removes all widgets from the layout, effectively disabling the contour plot.
        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self) -> None:
        """
        Add and display all widgets in the layout.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method ensures all necessary widgets are added and displayed in the layout.
        """
        # self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        # self.layout.addWidget(self.info_label)


# -----------------------------------------------------------------------------------------------
# Example usage of the ContourWidget class
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2D Contour Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = ContourWidget()
        self.chart_widget.set_title('Contour Plot')
        self.chart_widget.set_information('Contour plot of a 2D function')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(x**2+y**2))

        self.chart_widget.set_background('lightgray')

        self.chart_widget.set_data(x, y, z)
        self.chart_widget.refresh_chart()

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
