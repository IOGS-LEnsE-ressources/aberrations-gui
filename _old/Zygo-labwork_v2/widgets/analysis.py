# -*- coding: utf-8 -*-
"""*analysis.py* file.

This file contains graphical elements to display analysis parameters.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : nov/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QBrush
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import *
from lensepy.images.conversion import *
from lensepy.pyqt6 import *
from matplotlib import pyplot as plt


def is_number(s: str) -> bool:
    """Return if a str is a floating number.
    :param str: String to test.
    :return: True if str is a floating number.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

## TO MOVE TO LENSEPY.PYQT6
class LineEditWidget(QWidget):
    """Class to display a line edit block"""

    edit_finished = pyqtSignal(str)

    def __init__(self, title: str, txt: str = '', number: bool = False) -> None:
        """Default constructor.
        :param title: Title of the block.
        :param txt: Default text to display.
        :param number: True if this block is to enter numbers.
        """
        super().__init__(parent=None)

        self.layout = QHBoxLayout()
        self.number = number
        self.previous_val = ''

        self.label = QLabel(title)
        self.label.setStyleSheet(styleH2)

        self.lineedit = QLineEdit(txt)
        self.lineedit.editingFinished.connect(self.action_editing_finished)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def set_text(self, text: str):
        self.lineedit.setText(text)

    def get_text(self):
        return self.lineedit.text()

    def clear(self):
        self.lineedit.clear()

    def set_placeholder_text(self, text: str):
        self.lineedit.setPlaceholderText(text)

    def action_editing_finished(self):
        # Test if number
        if self.number:
            val = self.lineedit.text()
            if is_number(val):
                self.previous_val = val
                self.edit_finished.emit('finish')
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Warning - Not a number")
                dlg.setText("You didn't enter a number.")
                dlg.setStandardButtons(
                    QMessageBox.StandardButton.Ok
                )
                dlg.setIcon(QMessageBox.Icon.Warning)
                button = dlg.exec()
                self.lineedit.setText(self.previous_val)

        else:
            self.edit_finished.emit('finish')

class SimpleAnalysisOptionsWidget(QWidget):
    """Acquisition Options."""

    wedge_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Title
        self.label_simple_analysis_title = QLabel(translate("label_simple_analysis_title"))
        self.label_simple_analysis_title.setStyleSheet(styleH1)
        self.label_simple_analysis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Wedge Factor
        self.wedge_edit = LineEditWidget(title=translate('wedge_factor_label'), number=True)
        self.wedge_edit.edit_finished.connect(self.action_update_wedge)

        # Update Wedge
        self.update_wedge = QPushButton(translate('button_update_wedge'))
        self.update_wedge.clicked.connect(self.action_update_wedge)
        self.update_wedge.setStyleSheet(unactived_button)
        self.update_wedge.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        wedge_up_widget = qobject_to_widget(self.update_wedge)

        # Statistics
        self.table_stats = StatisticsTableWidget(self)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_simple_analysis_title)
        self.layout.addStretch()
        self.layout.addWidget(self.wedge_edit)
        self.layout.addWidget(wedge_up_widget)
        self.layout.addStretch()
        self.layout.addWidget(self.table_stats)
        self.layout.addStretch()

    def set_wedge_factor(self, value: float):
        """Set the wedge factor value.
        :param value: Value to update.
        """
        self.wedge_edit.set_text(str(value))

    def get_wedge_factor(self) -> float:
        return float(self.wedge_edit.get_text())


    def set_values(self, pv: list[float], rms: list[float]):
        """Add new values.

        """
        self.table_stats.set_values(pv, rms)

    def action_update_wedge(self):
        """Action performed when the Wedge factor is updated."""
        self.wedge_changed.emit('wedge')



class SimpleAnalysisSubOptionsWidget(QWidget):
    """Simple Analysis SubOptions."""

    aberrations_selected = pyqtSignal(list)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Title
        self.label_acquisition_title = QLabel(translate("label_sub_acquisition_title"))
        self.label_acquisition_title.setStyleSheet(styleH1)
        self.label_acquisition_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.check_tilt = QCheckBox(translate("check_tilt"))
        self.check_tilt.setEnabled(False)
        self.check_tilt.stateChanged.connect(self.action_state_changed)

        self.corrected_stats = StatisticsTableWidget(self)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_acquisition_title)
        self.layout.addWidget(self.check_tilt)
        self.layout.addWidget(self.corrected_stats)
        self.layout.addStretch()

    def set_tilt_enabled(self, val:bool = True):
        """Update tilt checkbox.
        :param val: True or False.
        """
        self.check_tilt.setEnabled(val)

    def uncheck_tilt(self):
        """Uncheck the tilt options."""
        self.check_tilt.setChecked(False)

    def action_state_changed(self):
        list_ab = []
        if self.check_tilt.isChecked():
            list_ab.append('tilt')
        self.aberrations_selected.emit(list_ab)

    def set_values(self, pv: list[float], rms: list[float]):
        """Add new values.

        """
        self.corrected_stats.set_values(pv, rms)


class StatisticsTableWidget(QTableWidget):

    def __init__(self, parent=None):
        """Default constructor.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.images_list = []
        self.voltage_list = []
        self.show_button_list = []
        self.setColumnCount(3)  # 3 columns
        self.setHorizontalHeaderLabels(["Set", "PV", "RMS"])
        self.setColumnWidth(0, 15)
        self.setStyleSheet("""
            QHeaderView::section {
                background-color: lightblue;
                color: black;
                font-weight: bold;
            }
        """)
        self.verticalHeader().setVisible(False)

    def _set_line(self, row, cell1, cell2, cell3, bg:str='white'):
        item = QTableWidgetItem(cell1)
        item.setBackground(QBrush(QColor(bg)))
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)  # change the alignment
        self.setItem(row, 0, item)
        item = QTableWidgetItem(cell2)
        item.setBackground(QBrush(QColor(bg)))
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)  # change the alignment
        self.setItem(row, 1, item)
        item = QTableWidgetItem(cell3)
        item.setBackground(QBrush(QColor(bg)))
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)  # change the alignment
        self.setItem(row, 2, item)

    def set_values(self, pv: list[float], rms: list[float]):
        """Add new values.

        """
        try:
            if len(pv) == len(rms):
                if len(pv) > 1:
                    self.setRowCount(len(pv)+2)
                    # Process global PV and RMS
                    std_pv = np.std(pv)
                    mean_pv = np.mean(pv)
                    std_rms = np.std(rms)
                    mean_rms = np.mean(rms)
                    # Display global PV and RMS
                    self._set_line(0, 'Mean', str(mean_pv),
                                   str(mean_rms), bg='lightblue')
                    self._set_line(0, 'STDev', str(std_pv),
                                   str(std_rms), bg='lightblue')
                    for row in range(len(pv)):
                        self._set_line(row+2, str(row+1), str(pv[row]), str(rms[row]))
                else:
                    self.setRowCount(len(pv))
                    self._set_line(0, str(1), str(pv[0]), str(rms[0]))

        except Exception as e:
            print(f'Stat Table {e}')

    def erase_all(self):
        """Delete all the rows and reconstruct the first line (header)."""
        self.clearContents()


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = SimpleAnalysisOptionsWidget(self)
            list_pv = [1.2, 5.2]
            list_rms = [5.8, 3.5]
            self.central_widget.set_values(list_pv, list_rms)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())