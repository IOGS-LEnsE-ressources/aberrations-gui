# Aberrations labworks GUI

## How to use this repository

You can Download or Clone this repository.

Then, you have to go to the **appli** directory and start the application by the following instruction:

'''
python cmos_machine_vision.py
'''

## Requirements

This application is coded in **Python** (3.10 or more) and it is based on **PyQt6**.

To be used with the Zygo interferometer system, you need to install specific drivers and Python API for a *Basler* 
USB camera. Piezo module is controlled by a NI-DAQ module (USB) that requires also NI drivers.

Other libraries or packages are required. You can access to the list in the *requirements.txt* file, from the **appli** directory.