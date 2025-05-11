# -*- coding: utf-8 -*-
"""*camera.py* file from *modes* folder.

This file contains elements to manage camera mode.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""

from modes.modes import *


class CameraMode(Mode):
    """
    Class Mode to manage Camera mode of the application.
    """

    def __init__(self, zygo_app):
        """Default constructor of the class.
        """
        super().__init__(zygo_app=zygo_app)
