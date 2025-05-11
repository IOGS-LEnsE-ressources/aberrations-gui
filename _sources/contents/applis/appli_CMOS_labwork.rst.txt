Study of a CMOS sensor / Labwork
################################

The source code of the application is in the :file:`applis/CMOS-labwork` directory of the GitHub repository of this project : `Camera GUI <https://github.com/IOGS-LEnsE-ressources/camera-gui>`_.

.. note::

	The :file:`basler/camera_basler_widget.py` and :file:`ids/camera_ids_widget.py` files were modified to include the :code:`supoptools` module.
	
	The importation of this module is done by:
	
	.. code-block:: python
	
		sys.path.append('../supoptools')
		from images.conversion import *
		from pyqt6.widget_slider import WidgetSlider
	
	! To change when SupOpTools will become a package !
	
Goal of the labwork
*******************
	
The goal of the labwork is to measure the characteristics of an industrial camera (IDS or Basler), equipped with CMOS sensors. We are specifically interested in the **sensor linearity**, the **read-out noise**, the **dark signal** and the **photon noise**. The measured values will be compared to the data given by the manufacturer.
	
Needs for the interface
***********************

Read-out noise and black level
==============================

The **read-out noise** is an **electronic noise** that appears during the conversion of the photoelectrons into voltage. This voltage is then digitized over a specified number of bits (8 in 'Mono8' color mode, 10 in 'Mono10', 12 in 'Mono12'...). To measure this noise, the sensor should receive no signal at all, with an integration time set as small as possible (to suppress the dark signal).

Then we need to take a raw image and to display its histogram, including the mean value and the standard deviation.

This test could be done with different Black level value (or Bias).

.. note::

	The interface has to integrate the ability to adjust the black level, to change the color mode, adjust the integration time and display the histogram of a raw image (with the mean value of pixels and the standard deviation).

Study of the dark signal
========================

Dark images refer to images taken without any illumination.

The idea is to take a set of raw images for different integration time and to display their histogram, including the mean value and the standard deviation.

.. note::

	The interface has to integrate the ability to adjust the integration time and display the histogram of a raw image (with the mean value of pixels and the standard deviation), in "real-time".

Sensor linearity / Photon noise
===============================

Spatial and temporal analisys

The CMOS sensor is now placed in front of an integrating sphere in order to be
uniformly illuminated. The images obtained in this case are often called Flat.
⇝ Set the integration time to 1 ms.
⇝ Power the integration sphere in order to obtain a gray level mean of 150.
6.1 Spatial analysis - Linearity
In order to measure the linearity of the sensor, one can measure the mean value
of the signal as a function of the integration time (do not forget to subtract the
read-out noise).
⇝ Read off the mean value and the standard deviation of the signal for an
integration time ranging from 0 to 2 ms (by step of 250 µs).
Q6 What can you say about the last point ? How can you find the Full Well
value on your graph ?
⇝ Plot the mean value of the signal as a function of the integration time.
46 B 3. CMOS SENSOR
Q7 Is the response of the sensor linear?
6.2 Temporal analysis - Photon noise
The photon noise can be estimated by measuring the signal temporal fluctuation of a pixel for different incident photon fluxes on the sensor.
⇝ Set the integration time to 200 µs.
⇝ Power the integration sphere in order to obtain a gray level mean of 128.
⇝ Observe the fluctuation of the signal of a pixel for this signal level.
Q8 Is the signal random ? What is the shape of the histogram ?
Remark : In order to obtain good statistical results, the observation must
be done for a large number of points (between 500 to 1000).
⇝ Repeat this operation for differents gray levels (64, 128, 192...) and plot
the mean level as a function of the variance of the signal.
Q9 Can the measured noise be considered to be photon noise? Why?
If the noise is indeed photon noise (i.e. Poisson noise), the fluctuation of
the number of photo-electrons per pixel is given by its standard deviation or its
variance:

It is thus possible to find the conversion factor (gain) in electrons per bit-level

Q10 Estimate the value of the conversion factor and compare your result with
the value obtained in P2.
Q11 Propose an explanation to justify the difference between the temporal
fluctuations of a pixel’s signal and the noise that you get by studying the histogram of the 200 × 200-pixel area.

Sensor spectral response
========================

Figure 3.5: Schematic diagram of the measurement bench using
a monochromator
The monochromator allows one to choose the wavelength of the light sent on
the sensor. The input and output slits are 2-mm wide which gives a spectral
width of the order of 30 nm. After the monochromator, a collimator allows
to illuminate the studied sensor under normally incident light. We use a PIN
10-D photodiode with a photosensitive area of 1cm2
to measure the illumination received by the sensor. The sensitivity of this photodiode is given in Figure
3.6.
⇝ Power the monochromator light with a voltage around 20 V.
⇝ Using the photodiode, measure the irradiance (in W/cm2
) for the following wavelength: 500, 600, 700, 800, 900 nm.
⇝ Replace the photodiode with the CMOS sensor. Set an appropriate integration time. Measure the signal intensity in the center of the image for these
wavelengths.
48 B 3. CMOS SENSOR
⇝ Deduce from your measurements the spectral response of the sensor in
gray level as a function of the received energy per cm2

Q12 Plot the curve and compare it with the datasheet.
Q13 What is the quantum yield for these wavelengths? Plot the quantum
yield as a function of the wavelength.
	