# -*- coding: utf-8 -*-
"""*xyz_chart_widget.py* file.

This file contains graphical elements to display a XYZ chart in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : nov/2024
"""
from matplotlib.backends.qt_compat import QtWidgets
#from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QVector3D
import numpy as np
import sys
import matplotlib.pyplot as plt

from lensepy.css import *  # Import CSS styles if needed
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
matplotlib.use('QtAgg')
from matplotlib.figure import Figure
from matplotlib import cm, colors

class Surface3DWidget2(QtWidgets.QWidget):
    def __init__(self, parent=None, grid_color='black', subdivisions=10) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.grid_color = grid_color
        self.subdivisions = subdivisions

        self.title: str = ''  # Initialize title as an empty string
        self.layout: QVBoxLayout = QVBoxLayout()  # Create a vertical layout for the widget

        self.master_layout: QVBoxLayout = QVBoxLayout()  # Create a master layout for the widget
        self.master_widget: QWidget = QWidget()  # Create a master widget to hold the layout

        # Title label setup
        self.title_label: QLabel = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        # pyqtgraph OpenGL GLViewWidget setup
        self.plot_chart_widget: gl.GLViewWidget = gl.GLViewWidget()
        self.plot_chart_widget.setMinimumWidth(300)
        self.plot_chart_widget.setMinimumHeight(300)

        # Initialize Numpy arrays for X, Y, and Z data
        self.plot_x_data: np.ndarray = np.array([])
        self.plot_y_data: np.ndarray = np.array([])
        self.plot_z_data: np.ndarray = np.array([])

        # Initialize surface plot object to None
        self.surface_plot: gl.GLMeshItem or None = None

        # List to store grid items
        self.grid_items = []

        # Set up the layout hierarchy
        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def add_grids(self, grid_color='black', subdivisions=10):
        self.remove_grids()  # Remove existing grids before adding new ones

        # Create the background grids
        x_min, x_max = np.nanmin(self.plot_x_data), np.nanmax(self.plot_x_data)
        y_min, y_max = np.nanmin(self.plot_y_data), np.nanmax(self.plot_y_data)
        z_min, z_max = np.nanmin(self.plot_z_data), np.nanmax(self.plot_z_data)

        grid_x_size = x_max - x_min
        grid_y_size = y_max - y_min
        grid_z_size = z_max - z_min

        # Calculate the spacing for the subdivisions
        x_spacing = grid_x_size / subdivisions
        y_spacing = grid_y_size / subdivisions
        z_spacing = grid_z_size / subdivisions

        # Create and position the XZ grid at y_min
        gx = gl.GLGridItem(size=QVector3D(grid_z_size, grid_y_size, 0))
        gx.rotate(90, 0, 1, 0)
        gx.translate(x_min, (y_min + y_max) / 2, (z_min + z_max) / 2)
        gx.setColor(pg.mkColor(grid_color))
        gx.setSpacing(z_spacing, x_spacing)
        self.plot_chart_widget.addItem(gx)
        self.grid_items.append(gx)

        # Create and position the YZ grid at x_min
        gy = gl.GLGridItem(size=QVector3D(grid_x_size, grid_z_size, 0))
        gy.rotate(90, 1, 0, 0)
        gy.translate((x_min + x_max) / 2, y_min, (z_min + z_max) / 2)
        gy.setColor(pg.mkColor(grid_color))
        gy.setSpacing(y_spacing, z_spacing)
        self.plot_chart_widget.addItem(gy)
        self.grid_items.append(gy)

        # Create and position the XY grid at z_min
        gz = gl.GLGridItem(size=QVector3D(grid_x_size, grid_y_size, 0))
        gz.translate((x_min + x_max) / 2, (y_min + y_max) / 2, z_min)
        gz.setColor(pg.mkColor(grid_color))
        gz.setSpacing(x_spacing, y_spacing)
        self.plot_chart_widget.addItem(gz)
        self.grid_items.append(gz)

    def remove_grids(self):
        for grid_item in self.grid_items:
            self.plot_chart_widget.removeItem(grid_item)
        self.grid_items = []

    def set_data(self, x_axis: np.ndarray, y_axis: np.ndarray, z_axis: np.ndarray) -> None:
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis
        self.plot_z_data = z_axis

        # Add grids after setting data to ensure they match the data range
        self.add_grids(self.grid_color, self.subdivisions)

    def set_axis_and_ticks_color(self, axis_color: str = BLUE_IOGS, ticks_color: str = BLUE_IOGS) -> None:
        pass

    def apply_colormap(self, z_values: np.ndarray) -> np.ndarray:
        norm = (z_values - np.nanmin(z_values)) / (np.nanmax(z_values) - np.nanmin(z_values))
        colormap = plt.get_cmap('rainbow')
        colors = colormap(norm)
        return colors

    def adjust_camera_position(self) -> None:
        x_min, x_max = np.nanmin(self.plot_x_data), np.nanmax(self.plot_x_data)
        y_min, y_max = np.nanmin(self.plot_y_data), np.nanmax(self.plot_y_data)
        z_min, z_max = np.nanmin(self.plot_z_data), np.nanmax(self.plot_z_data)

        # Calculate center of the plot
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        center_z = (z_min + z_max) / 4 * 3

        # Calculate distance for camera position
        distance = 1.5 * max(x_max - x_min, y_max - y_min, z_max - z_min) * 2

        # Set camera position
        self.plot_chart_widget.setCameraPosition(
            pos=QVector3D(center_x, center_y, center_z),
            distance=distance,
            azimuth=0,  # Adjust azimuth as needed
            elevation=15  # Adjust elevation as needed
        )

    def refresh_chart(self) -> None:
        if self.surface_plot:
            self.plot_chart_widget.removeItem(self.surface_plot)

        x = self.plot_x_data
        y = self.plot_y_data
        z = self.plot_z_data

        vertices = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
        faces = []
        face_colors = []
        rows, cols = x.shape

        z_colors = self.apply_colormap(z)  # Get the colors for the z values

        for i in range(rows - 1):
            for j in range(cols - 1):
                faces.append([i * cols + j, i * cols + j + 1, (i + 1) * cols + j])
                faces.append([(i + 1) * cols + j, i * cols + j + 1, (i + 1) * cols + j + 1])

                face_colors.append(z_colors[i, j, :])
                face_colors.append(z_colors[i, j, :])

        faces = np.array(faces)
        face_colors = np.array(face_colors)

        self.surface_plot = gl.GLMeshItem(
            vertexes=vertices, faces=faces, faceColors=face_colors, smooth=False, drawEdges=False)
        self.plot_chart_widget.addItem(self.surface_plot)
        self.adjust_camera_position()  # Adjust camera position after adding item
        self.adjustSize()

    def set_title(self, title: str) -> None:
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos: str) -> None:
        pass
        #self.info_label.setText(infos)

    def set_background(self, css_color: str) -> None:
        self.plot_chart_widget.setBackgroundColor(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self) -> None:
        self.plot_chart_widget.clear()

    def disable_chart(self) -> None:
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self) -> None:
        #self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111, projection='3d')
        super().__init__(fig)
        # Activate mouse interaction with mouse
        self.mpl_connect('scroll_event', self._zoom)
        self.fig = fig

    def _zoom(self, event):
        """ Fonction de zoom avec correction du sens de la molette et maintien de la figure centrée """
        pass
        '''
        scale_factor = 0.9 if event.button == 'up' else 1.1
        xlim, ylim, zlim = self.axes.get_xlim3d(), self.axes.get_ylim3d(), self.axes.get_zlim3d()
        x_center, y_center, z_center = np.mean(xlim), np.mean(ylim), np.mean(zlim)
        new_xlim = [x_center + (x - x_center) * scale_factor for x in xlim]
        new_ylim = [y_center + (y - y_center) * scale_factor for y in ylim]
        new_zlim = [z_center + (z - z_center) * scale_factor for z in zlim]
        self.axes.set_xlim3d(new_xlim)
        self.axes.set_ylim3d(new_ylim)
        self.axes.set_zlim3d(new_zlim)
        self.draw()
        '''

class Surface3DWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.canvas = MplCanvas(self)

        # Ajout du widget dans le layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def set_data(self, Z: np.ndarray, mask: np.ndarray = None, bar_title : str = '',
                 size: int = 25, fast_mode: bool = True):
        """Set data to display in a 3D projection chart.
        :param Z: Data to display.
        :param mask: Mask to apply. Optional.
        :param bar_title: Title of the color bar. Optional.
        :param size: Size of the downscaling. Default 25.
        :param fast_mode: True to accelerate the process but downscaling the image.
        """
        x = np.arange(Z.shape[1])
        y = np.arange(Z.shape[0])
        X, Y = np.meshgrid(x, y)

        # Mask for transparency
        if mask is not None:
            ZZ = np.ma.masked_array(Z, mask=~mask)
            max_ZZ = ZZ.max()
            min_ZZ = ZZ.min()

            Z_shifted = Z - min_ZZ
            max_ZZ_shifted = max_ZZ - min_ZZ

            norm = colors.Normalize(vmin=0, vmax=max_ZZ_shifted)
            color_map = cm.magma(norm(Z_shifted))
            color_map[..., -1] = np.where(mask == 0, 0, 1)
            if fast_mode:
                surface = self.canvas.axes.plot_surface(X, Y, Z_shifted, facecolors=color_map, shade=False,
                                                        rstride=size, cstride=size)
            else:
                surface = self.canvas.axes.plot_surface(X, Y, Z_shifted, facecolors=color_map, shade=False,
                                                        rstride=10, cstride=10)
            self.canvas.axes.set_zlim(0, max_ZZ_shifted)
            mappable = cm.ScalarMappable(norm=norm, cmap='magma')
            mappable.set_array(Z)
            cbar = self.canvas.fig.colorbar(mappable, ax=self.canvas.axes, shrink=0.5, aspect=10)
        else:
            if fast_mode:
                surface = self.canvas.axes.plot_surface(X, Y, Z, cmap='magma', shade=False,
                                                        rstride=size, cstride=size)
            else:
                surface = self.canvas.axes.plot_surface(X, Y, Z, cmap='magma', shade=False,
                                                        rstride=10, cstride=10)
            cbar = self.canvas.fig.colorbar(surface, ax=self.canvas.axes) #, shrink=0.5, aspect=10)

        cbar.set_label(bar_title)
        self.canvas.draw()

    def set_data_wire(self, Z: np.ndarray, mask: np.ndarray = None):
        x = np.arange(Z.shape[1])
        y = np.arange(Z.shape[0])
        X, Y = np.meshgrid(x, y)
        surface = self.canvas.axes.plot_wireframe(X, Y, Z)
        self.canvas.draw()


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("3D Surface Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid: QtWidgets.QWidget = QtWidgets.QWidget()
        self.layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()

        self.chart_widget: Surface3DWidget = Surface3DWidget()
        self.layout.addWidget(self.chart_widget)

        x: np.ndarray = np.linspace(-1, 2, 2000)
        y: np.ndarray = np.linspace(-1, 1, 2000)
        x, y = np.meshgrid(x, y)
        z: np.ndarray = np.sin(np.sqrt(x**2 + y**2))

        z *= (x.max() - x.min()) * .75 / (z.max() - z.min())
        mask = np.ones_like(z).astype(np.uint8)
        mask[100:700, 200:500] = 0
        self.chart_widget.set_data(z, mask)

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
