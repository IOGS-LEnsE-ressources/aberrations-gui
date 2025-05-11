# -*- coding: utf-8 -*-
"""
BarChartWidget: Widget for displaying bar charts using PyQtGraph.

---------------------------------------
(c) 2024 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2024/06/25
    Modification on 2024/06/25

Authors
-------
    Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
    Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

Description
-----------
This module defines the BarChartWidget class, which encapsulates functionality
to display bar charts using PyQtGraph. It includes methods to set data, set bar color,
update the bar chart display, and modify chart title and axis labels. Colors for axes,
bars, and background can be customized, including axis ticks and labels.

Usage
-----
To use this widget:
1. Import BarChartWidget from this module.
2. Create an instance of BarChartWidget, optionally passing colors as arguments.
3. Use set_data() to provide data for the bar chart.
4. Use set_title() to set the chart title.
5. Use set_axis_labels() to set labels for the X and Y axes.
6. Optionally, use set_bar_color() to change the color of the bars.
7. The widget automatically updates the display with the provided data and settings.

Example:
--------
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import sys
import numpy as np
import pyqtgraph as pg
from bar_chart_widget import BarChartWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Bar Chart Example")
    main_window.setGeometry(100, 100, 800, 600)

    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)

    layout = QVBoxLayout()
    central_widget.setLayout(layout)

    bar_chart_widget = BarChartWidget(axis_color='black', bar_color='blue', background_color='lightgray',
                                      axis_ticks_color='black', axis_labels_color='black')
    layout.addWidget(bar_chart_widget)

    x_data = np.array([1, 2, 3, 4, 5])
    y_data = np.array([10, 30, 20, 15, 35])
    bar_chart_widget.set_data(x_data, y_data)
    bar_chart_widget.set_title('My Bar Chart')
    bar_chart_widget.set_axis_labels('X Axis', 'Y Axis')

    main_window.show()
    sys.exit(app.exec())
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from lensepy.css import *  # Import CSS styles if needed

class BarChartWidget(QWidget):
    def __init__(self, axis_color='black', bar_color='orange', background_color='white',
                 axis_ticks_color='black', axis_labels_color='black'):
        super().__init__()
        self.axis_color = axis_color

        # Main layout of the widget
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Chart title
        self.title_label = QLabel('')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Plot widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Default bar color
        self.bar_color = pg.mkColor(bar_color)

        # Update plot widget style
        self.plot_widget.setBackground(background_color)
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(axis_color))
        self.plot_widget.getAxis('bottom').setTickPen(pg.mkPen(axis_ticks_color))
        self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(axis_labels_color))
        self.plot_widget.getAxis('left').setPen(pg.mkPen(axis_color))
        self.plot_widget.getAxis('left').setTickPen(pg.mkPen(axis_ticks_color))
        self.plot_widget.getAxis('left').setTextPen(pg.mkPen(axis_labels_color))

        # Default data (example)
        self.x_data = np.array([1, 2, 3, 4, 5])
        self.y_data = np.array([10, 30, 20, 15, 35])

        # Horizontal line at y=0
        self.zero_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen(axis_color, width=1))
        self.plot_widget.addItem(self.zero_line)

        # Update the plot at initialization
        self.update_plot()

    def set_data(self, x_data, y_data):
        """
        Set the data to display in the bar chart.
        """
        self.x_data = x_data
        self.y_data = y_data
        self.update_plot()

    def set_bar_color(self, color):
        """
        Set the color of the bars.
        """
        self.bar_color = pg.mkColor(color)
        self.update_plot()

    def set_title(self, title):
        """
        Set the title of the chart.
        """
        self.title_label.setText(title)

    def set_axis_labels(self, x_label, y_label):
        """
        Set labels for the X and Y axes.
        """
        self.plot_widget.setLabel('bottom', x_label)
        self.plot_widget.setLabel('left', y_label)

    def update_plot(self):
        """
        Update the bar chart with current data and settings.
        """
        self.plot_widget.clear()

        # Create a BarGraphItem object with current data and specified color
        bar_chart = pg.BarGraphItem(x=self.x_data, height=self.y_data, width=0.6, brush=self.bar_color)

        # Horizontal line at y=0
        self.zero_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen(self.axis_color, width=1))
        self.plot_widget.addItem(self.zero_line)

        # Add BarGraphItem object to the plot widget
        self.plot_widget.addItem(bar_chart)

        # Set axis labels if needed
        self.plot_widget.setLabel('left', 'Y Axis')
        self.plot_widget.setLabel('bottom', 'X Axis')

# Example of using BarChartWidget in a QMainWindow
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bar Chart Example")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create and add the bar chart widget to the main window
        self.bar_chart_widget = BarChartWidget(axis_color='black', bar_color='blue', background_color='lightgray',
                                              axis_ticks_color='black', axis_labels_color='black')
        self.layout.addWidget(self.bar_chart_widget)

        # Example data
        x_data = np.array([1, 2, 3, 4, 5])
        y_data = np.array([10, 30, 20, 15, 35])
        self.bar_chart_widget.set_data(x_data, y_data)

        # Example of setting chart title and axis labels
        self.bar_chart_widget.set_title('My Bar Chart')
        self.bar_chart_widget.set_axis_labels('X Axis', 'Y Axis')

# Entry point to run the PyQt application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MyWindow()
    main_window.show()
    sys.exit(app.exec())
