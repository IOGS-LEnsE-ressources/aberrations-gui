Interferometric controls / Labwork
##################################

The source code of the application is in the :file:`applis/Zygo-labwork` directory of the GitHub repository of this project : `Camera GUI <https://github.com/IOGS-LEnsE-ressources/camera-gui>`_.

	
Goal of the labworks
********************



The topics of the lab sessions are available on the LEnsE website:

First year: `Interferometric Controls <https://lense.institutoptique.fr/tp-controles-interferometriques/>`_ (French
version only)
Second year: `Aberrations <https://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-PolyAberrations.EN.pdf>`_

First series of labworks : quality of standard optical components
=================================================================

These lab sessions aim to present some commonly used interferometry methods for characterizing the
quality of standard optical components (parallel-faced plates, flat mirrors, telescope mirrors,
optical systems, etc.). These techniques allow the quantification of the quality of finished
optical components or those in the process of manufacturing.

IMAGE OF "SIMPLE" ACQUISITION PART ?

Second series of labworks : aberrations
=======================================

The goal of the following lab sessions is to study and analyze the defects of an optical system, i.e.
the geometrical and chromatic aberrations.

IMAGE OF ANALYSIS PART ?

Needs for the interface
***********************

ZYGO is a Fizeau laser interferometer (using an amplitude division) equipped with a phase shift system.
It allows to measure wavefront errors down to approximately λ/10(PV).

The user interface of the **ZygoLab** application is designed to facilitate the acquisition and analysis of
interferograms obtained using a *Zygo interferometer* as part of the photonics lab work at the
Experimental Teaching Laboratory (LEnsE) of the Institut d'Optique Graduate School (IOGS).

Capture images from a camera
============================

- Set exposure time, fps and black level of the camera.
- Acquire image from a the camera.

Control a piezo actuator
========================

- Analog output (via Texas Instruments USB-6001 device or Nucleo if no API in Python for TI USB-6001) to control the piezo actuator.

See https://github.com/ni/nidaqmx-python


Make some calculations
======================

To complete...