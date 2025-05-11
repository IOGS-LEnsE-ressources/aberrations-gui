# -*- coding: utf-8 -*-
"""*modes.py* file from *modes* folder.

This file contains elements to manage modes.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""

BOT_HEIGHT, TOP_HEIGHT = 45, 50
LEFT_WIDTH, RIGHT_WIDTH = 45, 45
TOP_LEFT_ROW, TOP_LEFT_COL = 1, 1
TOP_RIGHT_ROW, TOP_RIGHT_COL = 1, 2
BOT_LEFT_ROW, BOT_LEFT_COL = 2, 1
BOT_RIGHT_ROW, BOT_RIGHT_COL = 2, 2
SUBMENU_ROW, SUBMENU_COL = 0, 0
OPTIONS_ROW, OPTIONS_COL = 0, 1
SUBOPTIONS_ROW, SUBOPTIONS_COL = 0, 2

class Mode:
    """
    Class Mode to manage modes of the application.
    """

    def __init__(self, zygo_app):
        """"""
        self.zygo_app = zygo_app
        self.mode = None

    def update_interface(self):
        """Update widgets in the interface."""
        self._clear_layouts()
        # self.zygo_app.central_widget

    def _clear_layouts(self):
        """"""
        # Clear layouts
        self._clear_sublayout(OPTIONS_COL)
        self._clear_sublayout(SUBOPTIONS_COL)
        self._clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self._clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self._clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def _clear_layout(self, row: int, column: int) -> None:
        """
        Remove widgets from a specific position in the layout.
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

    def _clear_sublayout(self, column: int) -> None:
        """
        Remove widgets from a specific position in the layout of the bottom left area.
        :param column: Column index of the layout.
        """
        item = self.bot_left_layout.itemAtPosition(0, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

    def _set_top_left_widget(self, widget):
        """
        Modify the top left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.top_left_widget = widget
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)

    def set_top_right_widget(self, widget):
        """
        Modify the top right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)

    def set_bot_left_widget(self, widget):
        """
        Modify the bottom left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_LEFT_ROW, BOT_LEFT_COL)
        self.bot_left_widget = widget
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

    def set_bot_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.bot_right_widget = widget
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def set_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL, 2, 1)

    def set_sub_menu_widget(self, widget):
        """
        Modify the sub menu widget.
        :param widget: Widget of the sub menu.
        """
        self.clear_sublayout(SUBMENU_COL)
        self.submenu_widget = widget
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)

    def set_options_widget(self, widget):
        """
        Modify the options widget.
        :param widget: Widget of the options.
        """
        self.clear_sublayout(OPTIONS_COL)
        self.options_widget = widget
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)

    def set_suboptions_widget(self, widget):
        """
        Modify the options widget.
        :param widget: Widget of the options.
        """
        self.clear_sublayout(SUBOPTIONS_COL)
        self.suboptions_widget = widget
        self.bot_left_layout.addWidget(self.suboptions_widget, SUBOPTIONS_ROW, SUBOPTIONS_COL)