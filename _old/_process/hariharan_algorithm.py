# -*- coding: utf-8 -*-
"""*hariharan_algorithm.py* file.

This file is attached to a 1st year of engineer training labwork in photonics.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian Mendes (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import numpy as np

def hariharan_algorithm(intensity_1: np.ndarray, intensity_2: np.ndarray, intensity_3: np.ndarray, intensity_4: np.ndarray, intensity_5: np.ndarray) -> np.ndarray:
    """
    Apply the Hariharan phase demodulation algorithm to a set of intensity measurements.

    Parameters
    ----------
    intensity_1 : np.ndarray
        First intensity measurement, I_1 = I_0 * (1 + C * cos(phi)).

    intensity_2 : np.ndarray
        Second intensity measurement, I_2 = I_0 * (1 + C * cos(phi + π/2)).

    intensity_3 : np.ndarray
        Third intensity measurement, I_3 = I_0 * (1 + C * cos(phi + π)).

    intensity_4 : np.ndarray
        Fourth intensity measurement, I_4 = I_0 * (1 + C * cos(phi + 3π/2)).

    intensity_5 : np.ndarray
        Fifth intensity measurement, I_5 = I_0 * (1 + C * cos(phi + 2π)).

    Returns
    -------
    np.ndarray
        The demodulated phase phi array.

    Notes
    -----
    This function calculates the demodulated phase using the Hariharan algorithm, which is a method for phase recovery in interferometry.

    The five intensity measurements are taken with phase shifts of π/2 between them, specifically:
    - I_1 = I_0(1 + C * cos(phi))
    - I_2 = I_0(1 + C * cos(phi + pi/2))
    - I_3 = I_0(1 + C * cos(phi + pi))
    - I_4 = I_0(1 + C * cos(phi + 3*pi/2))
    - I_5 = I_0(1 + C * cos(phi + 2*pi))

    The returned phase values are in radians.

    This algorithm was originally published in:
    P. Hariharan, B. F. Oreb, and T. Eiju, "Digital phase-shifting interferometry: a simple error-compensating phase calculation algorithm," Appl. Opt. 26, 2504-2506 (1987).
    Available at: https://opg.optica.org/ao/fulltext.cfm?uri=ao-26-13-2504&id=168363

    Examples
    --------
    >>> intensity_1 = np.array([[1, 2], [3, 4]])
    >>> intensity_2 = np.array([[1, 2], [4, 5]])
    >>> intensity_3 = np.array([[1, 3], [4, 6]])
    >>> intensity_4 = np.array([[4, 5], [6, 7]])
    >>> intensity_5 = np.array([[3, 6], [7, 6]])
    >>> hariharan_algorithm(intensity_1, intensity_2, intensity_3, intensity_4, intensity_5)
    array([[-1.24904577, -1.24904577],
           [-1.10714872,  1.10714872]])
    """
    num = 2 * (intensity_2 - intensity_4)
    denum = 2 * intensity_3 - intensity_5 - intensity_1
    return np.arctan2(num, denum)
