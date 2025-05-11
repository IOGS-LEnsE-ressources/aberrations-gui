# -*- coding: utf-8 -*-
"""*initialization_parameters.py* file.

*initialization_parameters* file that contains :class::ZygoLabApp

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

def read_default_parameters(file):
    """
    Reads default parameters from a configuration file and returns them as a dictionary.

    Parameters
    ----------
    file : str
        Path to the configuration file.

    Returns
    -------
    dict
        Dictionary containing default parameters read from the file.

    Notes
    -----
    - Lines starting with '#' are treated as comments and skipped.
    - Each parameter should be defined on a separate line in the format 'key; value'.
    """
    default_parameters = {}
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('#'):  # Skip lines starting with '#'
                continue
            key, value = line.strip().split('; ')  # Split key and value based on '; '
            default_parameters[key.strip()] = value.strip()  # Remove extra whitespace and store in dictionary
    return default_parameters

def modify_parameter_value(file, parameter, new_value):
    """
    Modifies a specific parameter's value in the configuration file.

    Parameters
    ----------
    file : str
        Path to the configuration file.
    parameter : str
        Parameter key to modify.
    new_value : str
        New value to assign to the parameter.

    Returns
    -------
    None

    Notes
    -----
    - If the specified parameter is not found in the file, a message is printed indicating its absence.
    - The function overwrites the original file with the modified parameter value.
    """
    parameter_found = False
    with open(file, 'r') as f:
        lines = f.readlines()  # Read all lines in the file

    with open(file, 'w') as f:
        for line in lines:
            if line.startswith('#'):  # Preserve commented lines
                f.write(line)
                continue

            key, value = line.strip().split('; ')  # Split key and value based on '; '
            if key == parameter:  # If the key matches the parameter to modify
                f.write(f"{key}; {new_value}\n")  # Write the modified key-value pair
                parameter_found = True
            else:
                f.write(line)  # Otherwise, write the line unchanged

    if not parameter_found:
        print(f"The parameter '{parameter}' was not found in the file.")
