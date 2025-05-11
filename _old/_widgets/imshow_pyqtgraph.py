import numpy as np
import sys
import pyqtgraph as pg
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from lensepy.css import *

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

class ImageWidget(QWidget):
    """
    Widget used to display a 2D image with a specified colormap.
    """
    window_closed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.title = ''
        self.layout = QVBoxLayout()
        self.master_widget = QWidget()

        # Title label setup
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # pyQtGraph GraphicsLayoutWidget setup
        self.plot_widget = pg.GraphicsLayoutWidget()

        # ImageItem setup
        self.image_item = pg.ImageItem()
        self.view_box = self.plot_widget.addViewBox()
        self.view_box.addItem(self.image_item)
        self.view_box.setAspectLocked(True)

        # Set up the layout hierarchy
        self.master_widget.setLayout(self.layout)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_widget)
        self.setLayout(self.layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_image_data(self, image_data: np.ndarray, colormap_name: str = 'viridis'):
        """
        Set the image data to display with a specified colormap.

        Parameters
        ----------
        image_data : np.ndarray
            2D array of image data.
        colormap_name : str, optional
            Name of the colormap to use (default is 'viridis').

        Notes
        -----
        This method applies the specified colormap to the image data.
        """
        # Rotate the image data 90 degrees clockwise
        image_data_rotated = np.rot90(image_data, k=-1)

        # Apply colormap to the rotated image data
        colormap = plt.get_cmap(colormap_name)
        colored_image = colormap(image_data_rotated)

        # Ensure the image has RGBA channels for transparency
        if colored_image.shape[2] == 3:
            colored_image = np.concatenate([colored_image, np.ones((colored_image.shape[0], colored_image.shape[1], 1))], axis=2)

        # Set the image data to the ImageItem
        self.image_item.setImage(colored_image)

        # Adjust the view range to fit the image
        self.view_box.autoRange()

    def set_title(self, title: str):
        """
        Set the title of the image display widget.
        """
        self.title = title
        self.title_label.setText(self.title)

    def clear_graph(self):
        """
        Clear the image display widget.
        """
        self.image_item.clear()

    def disable_chart(self):
        """
        Erase all widgets from the layout.
        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    

    def enable_chart(self):
        """
        Enable and display all widgets in the layout.
        """
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_widget)

    def closeEvent(self, event):
        self.window_closed.emit(True)

class TwoImageWidget(QWidget):
    """
    Widget used to display 2D images with a specified colormap.
    """
    window_closed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.title = ''
        self.layout = QVBoxLayout()
        self.master_layout = QVBoxLayout()
        self.master_widget = QWidget()

        # Title label setup
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)  # Apply styleH1

        # Information label setup
        self.info_label = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)  # Apply styleH3

        # pyQtGraph GraphicsLayoutWidget setup
        self.plot_widget = pg.GraphicsLayoutWidget()

        # ImageItem setup
        self.image_item = pg.ImageItem()
        self.view_box = self.plot_widget.addViewBox()
        self.view_box.addItem(self.image_item)
        self.view_box.setAspectLocked(True)

        # Set up the layout hierarchy
        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_image_data(self, image_data1: np.ndarray, image_data2: np.ndarray = None, colormap_name1: str = 'magma', colormap_name2: str = 'viridis', alpha: float = 0.5):
        """
        Set the image data to display with a specified colormap and alpha transparency.

        Parameters
        ----------
        image_data1 : np.ndarray
            2D array of image data for the first image.
        image_data2 : np.ndarray
            2D array of image data for the second image.
        colormap_name1 : str, optional
            Name of the colormap to use for the first image (default is 'magma').
        colormap_name2 : str, optional
            Name of the colormap to use for the second image (default is 'viridis').
        alpha : float, optional
            Transparency level of the second image (default is 0.5, semi-transparent).

        Notes
        -----
        This method overlays two images with different colormaps on top of each other.
        """
        # Rotate the image data 90 degrees clockwise
        image_data1_rotated = np.rot90(image_data1, k=-1)
        if image_data2 is not None:
            image_data2_rotated = np.rot90(image_data2, k=-1)

        # Apply colormap to the rotated image data
        colormap1 = plt.get_cmap(colormap_name1)
        colored_image1 = colormap1(image_data1_rotated)
        if image_data2 is not None:
            colormap2 = plt.get_cmap(colormap_name2)
            colored_image2 = colormap2(image_data2_rotated)

        # Ensure the images have RGBA channels for transparency
        if colored_image1.shape[2] == 3:
            colored_image1 = np.concatenate([colored_image1, np.ones((colored_image1.shape[0], colored_image1.shape[1], 1))], axis=2)
        if image_data2 is not None:
            if colored_image2.shape[2] == 3:
                colored_image2 = np.concatenate([colored_image2, np.ones((colored_image2.shape[0], colored_image2.shape[1], 1))], axis=2)

        if image_data2 is not None:
            # Set transparency levels for the second image
            colored_image2[..., 3] *= alpha

        # Combine the images with transparency
        combined_image = colored_image1.copy()
        if image_data2 is not None:
            combined_image[..., :3] = (1 - alpha) * colored_image1[..., :3] + alpha * colored_image2[..., :3]
            combined_image[..., 3] = np.maximum(colored_image1[..., 3], colored_image2[..., 3])

        # Set the combined image data to the ImageItem
        self.image_item.setImage(combined_image)

        # Adjust the view range to fit the image
        self.view_box.autoRange()

    def set_title(self, title: str):
        """
        Set the title of the image display widget.
        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos: str):
        """
        Set information text displayed below the image.
        """
        self.info_label.setText(infos)

    def set_background(self, css_color: str):
        """
        Set the background color of the widget.
        """
        self.plot_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        """
        Clear the image display widget.
        """
        self.image_item.clear()

    def disable_chart(self):
        """
        Erase all widgets from the layout.
        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self):
        """
        Enable and display all widgets in the layout.
        """
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.info_label)

    def closeEvent(self, event) -> None:
        self.window_closed.emit(True)


# Example usage of the ImageWidget class
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2D Image Display with Colormap")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.image_widget = TwoImageWidget()
        self.image_widget.set_title('Image Display with Colormap')
        self.image_widget.set_information('Displaying a 2D image with colormap "Magma" and "Viridis"')
        self.layout.addWidget(self.image_widget)

        # Example image data
        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        z1 = 100*np.sin(np.sqrt(x ** 2 + y ** 2))
        z2 = 100*np.cos(np.sqrt(x ** 2 + y ** 2))

        z1 = z1.astype(np.uint8)
        z2 = z2.astype(np.uint8)

        # Set background color
        self.image_widget.set_background('lightgray')

        # Display first image with 'magma' colormap and second image with 'viridis' colormap
        self.image_widget.set_image_data(z1, z2, colormap_name1='gray', colormap_name2='magma', alpha=0.5)

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests
"""if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())"""

def main():
    app = QApplication(sys.argv)

    # Create an instance of ImageWidget
    widget = ImageWidget()

    # Generate some sample data (2D array)
    x = np.linspace(-10, 10, 1024)
    y = np.linspace(-10, 10, 1024)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)

    # Set image data and colormap
    widget.set_image_data(Z, colormap_name='magma')

    # Set title
    widget.set_title('Pseudocolor Plot')

    # Show the widget
    widget.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()