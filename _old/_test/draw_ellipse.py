import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import QPoint

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Ellipse Drawing Example')
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawEllipse(painter)

    def drawEllipse(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(0, 0, 0), 2)  # Couleur noire avec une largeur de ligne de 2
        painter.setPen(pen)

        x_center = self.width() // 2
        y_center = self.height() // 2
        radius = 100

        painter.drawEllipse(QPoint(x_center, y_center), radius, radius)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())
