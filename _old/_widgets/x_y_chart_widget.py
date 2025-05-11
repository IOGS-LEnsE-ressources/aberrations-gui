# -*- coding: utf-8 -*-
"""XYChartWidget for displaying data on a 2D chart.

---------------------------------------
(c) 2024 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/02
    Modification on 2024/06/11

Authors
-------
    Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
    Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import numpy as np
import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, mkPen

from lensepy.css import *

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# -----------------------------------------------------------------------------------------------

class XYChartWidget(QWidget):
    """
    Widget used to display data in a 2D chart - X and Y axis.
    Inherits from QWidget.

    Attributes
    ----------
    title : str
        Title of the chart.
    plot_chart_widget : PlotWidget
        PyQtGraph PlotWidget to display the chart.
    plot_chart : PlotWidget.plot
        Plot object of the PyQtGraph widget.
    plot_x_data : np.ndarray
        Data values for the X axis.
    plot_y_data : np.ndarray
        Data values for the Y axis.
    line_color : str
        Color of the line in the graph (CSS format, e.g., '#0A3250').
    line_width : float
        Width of the line in the graph (default 1).

    Methods
    -------
    set_data(x_axis, y_axis):
        Set the X and Y axis data to display on the chart.
    set_x_label(label, color=BLUE_IOGS):
        Set the label and color for the X axis.
    set_y_label(label, color=BLUE_IOGS):
        Set the label and color for the Y axis.
    set_axis_and_ticks_color(axis_color=BLUE_IOGS, ticks_color=BLUE_IOGS):
        Set the color of the axes, their ticks, and labels.
    refresh_chart():
        Refresh the data of the chart.
    update_infos(val=True):
        Update the information displayed below the chart.
    set_title(title):
        Set the title of the chart.
    set_information(infos):
        Set additional information below the chart.
    set_background(css_color):
        Set the background color of the widget.
    clear_graph():
        Clear the main chart of the widget.
    disable_chart():
        Remove all widgets from the layout.
    enable_chart():
        Add and display all widgets in the layout.
    set_line_color_width(color, width):
        Set the color and width of the line in the graph.
    """

    def __init__(self):
        """
        Initialize the XYChartWidget.
        """
        super().__init__()
        self.title = ''  # Title of the chart
        self.layout = QVBoxLayout()  # Main layout of the QWidget

        self.master_layout = QVBoxLayout()
        self.master_widget = QWidget()

        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        # Option label
        self.info_label = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)

        self.plot_chart_widget = PlotWidget()  # PyQtGraph widget
        self.plot_x_data = np.array([])  # Initialize X data
        self.plot_y_data = np.array([])  # Initialize Y data

        # Initialize plot with dummy data
        self.plot_chart = self.plot_chart_widget.plot([0])

        # Set default line color and width
        self.line_color = ORANGE_IOGS
        self.line_width = 1

        self.set_axis_and_ticks_color()  # Set initial axis and ticks color

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        self.enable_chart()  # Enable chart to add widgets to the layout

    def set_data(self, x_axis, y_axis):
        """
        Set the X and Y axis data to display on the chart.

        Parameters
        ----------
        x_axis : np.ndarray
            X-axis values to display.
        y_axis : np.ndarray
            Y-axis values to display.

        Returns
        -------
        None
            No return value.
        """
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis

    def set_x_label(self, label, unit='', color=BLUE_IOGS):
        """
        Set the label and color of the X axis.

        Parameters
        ----------
        label : str
            Label for the X axis.
        color : str, optional
            Color of the label in CSS format (default is BLUE_IOGS).

        Returns
        -------
        None
            No return value.
        """
        self.plot_chart_widget.setLabel('bottom', label, units=unit, color=color)

    def set_y_label(self, label, unit='', color=BLUE_IOGS):
        """
        Set the label and color of the Y axis.

        Parameters
        ----------
        label : str
            Label for the Y axis.
        color : str, optional
            Color of the label in CSS format (default is BLUE_IOGS).

        Returns
        -------
        None
            No return value.
        """
        self.plot_chart_widget.setLabel('left', label, units=unit, color=color)

    def set_axis_and_ticks_color(self, axis_color=BLUE_IOGS, ticks_color=BLUE_IOGS):
        """
        Set the color of the axes, their ticks, and labels.

        Parameters
        ----------
        axis_color : str, optional
            Color for the axes in CSS format (default is BLUE_IOGS).
        ticks_color : str, optional
            Color for the ticks in CSS format (default is BLUE_IOGS).

        Returns
        -------
        None
            No return value.
        """
        # Set the pen for the X and Y axes
        axis_pen = mkPen(color=axis_color, width=2)
        self.plot_chart_widget.getAxis('bottom').setPen(axis_pen)
        self.plot_chart_widget.getAxis('left').setPen(axis_pen)

        # Set the pen for the ticks
        ticks_pen = mkPen(color=ticks_color, width=1)
        self.plot_chart_widget.getAxis('bottom').setTickPen(ticks_pen)
        self.plot_chart_widget.getAxis('left').setTickPen(ticks_pen)

        # Set the color for the tick labels
        self.plot_chart_widget.getAxis('bottom').setTextPen(axis_pen)
        self.plot_chart_widget.getAxis('left').setTextPen(axis_pen)

    def refresh_chart(self):
        """
        Refresh the data displayed on the chart.

        Returns
        -------
        None
            No return value.
        """
        self.plot_chart_widget.removeItem(self.plot_chart)
        self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                      self.plot_y_data,
                                                      pen=mkPen(self.line_color, width=self.line_width))
        self.adjustSize()

    def update_infos(self, val=True):
        """
        Update the information displayed below the chart.

        Parameters
        ----------
        val : bool, optional
            If True, display mean and standard deviation; otherwise, indicate "acquisition in progress".
            Default is True.

        Returns
        -------
        None
            No return value.
        """
        if val:
            mean_d = round(np.mean(self.plot_y_data), 2)
            stdev_d = round(np.std(self.plot_y_data), 2)
            self.set_information(f'Mean = {mean_d} / Standard Dev = {stdev_d}')
        else:
            self.set_information('Data Acquisition In Progress')

    def set_title(self, title):
        """
        Set the title of the chart.

        Parameters
        ----------
        title : str
            Title for the chart.

        Returns
        -------
        None
            No return value.
        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos):
        """
        Set additional information below the chart.

        Parameters
        ----------
        infos : str
            Information to display.

        Returns
        -------
        None
            No return value.
        """
        self.info_label.setText(infos)

    def set_background(self, css_color):
        """
        Set the background color of the widget.

        Parameters
        ----------
        css_color : str
            Color in CSS format.

        Returns
        -------
        None
            No return value.
        """
        self.plot_chart_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        """
        Clear the main chart of the widget.

        Returns
        -------
        None
            No return value.
        """
        self.plot_chart_widget.clear()

    def disable_chart(self):
        """
        Remove all widgets from the layout.

        Returns
        -------
        None
            No return value.
        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self):
        """
        Add and display all widgets in the layout.

        Returns
        -------
        None
            No return value.
        """
        # self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        # self.layout.addWidget(self.info_label)

    def set_line_color_width(self, color, width):
        """
        Set the color and width of the line in the graph.

        Parameters
        ----------
        color : str
            Color of the line in CSS format (e.g., '#FF0000').
        width : float
            Width of the line.

        Returns
        -------
        None
            No return value.
        """
        self.line_color = color
        self.line_width = width

class MultiCurveChartWidget(XYChartWidget):
    def __init__(self):
        super().__init__()
        self.curves = []  # List to store the curves

    def add_curve(self, x_axis, y_axis, color, width, name):
        """
        Add a new curve to the graph.

        Parameters
        ----------
        x_axis : np.ndarray
            Data for the X axis.
        y_axis : np.ndarray
            Data for the Y axis.
        color : str
            Color of the curve in CSS format (e.g., '#FF0000').
        width : float
            Width of the curve.
        name : str
            Name of the curve for the legend.
        """
        curve = self.plot_chart_widget.plot(x_axis, y_axis, pen=mkPen(color, width=width), name=name)
        self.curves.append(curve)

    def refresh_chart(self):
        """
        Update the graph display with all the curves.
        """
        self.plot_chart_widget.clear()  # Clear existing graph
        for curve in self.curves:
            self.plot_chart_widget.addItem(curve)
        # self.plot_chart_widget.addLegend()  # Uncomment to add a legend

    def clear_graph(self):
        """
        Clear the main chart of the widget and reset the curves.
        """
        super().clear_graph()
        self.curves = []  # Reset the list of curves

# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XY Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = XYChartWidget()
        self.chart_widget.set_title('My Super Chart')
        self.chart_widget.set_information('This is a test')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(0, 100, 101)
        y = np.random.randint(0, 100, 101, dtype=np.int8)

        self.chart_widget.set_background('lightgray')

        self.chart_widget.set_data(x, y)
        self.chart_widget.set_x_label('X')
        self.chart_widget.set_y_label('Y')

        self.chart_widget.refresh_chart()

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)

# Launching as main for tests
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())

