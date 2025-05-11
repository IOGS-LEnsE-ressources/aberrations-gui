import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fftshift, fft2
import cv2

PI = np.pi
I = 1j

def calculate_centroid(image):
    """
    Calculate the centroid (barycenter) of a 2D image.

    Parameters
    ----------
    image : numpy.ndarray
        2D array representing the image, where pixel values represent intensities.

    Returns
    -------
    tuple
        Coordinates of the centroid (x_centroid, y_centroid).

    Notes
    -----
    The centroid is calculated using the formula:
    x_centroid = sum(x * I(x, y)) / sum(I(x, y))
    y_centroid = sum(y * I(x, y)) / sum(I(x, y))
    where I(x, y) is the intensity at pixel (x, y).

    Example
    -------
    >>> image = np.array([[0, 0, 0, 0, 0],
    ...                   [0, 0, 1, 0, 0],
    ...                   [0, 1, 1, 1, 0],
    ...                   [0, 0, 1, 0, 0],
    ...                   [0, 0, 0, 0, 0]])
    >>> calculate_centroid(image)
    (2.0, 2.0)
    """
    # Get the indices of the image array
    y_indices, x_indices = np.indices(image.shape)

    # Calculate the total intensity of the image
    total_intensity = np.sum(image)

    # Calculate the coordinates of the centroid
    x_centroid = np.sum(x_indices * image) / total_intensity
    y_centroid = np.sum(y_indices * image) / total_intensity

    return (x_centroid, y_centroid)

def resize_image(img, Ne):
    real_part = np.real(img)
    imaginary_part = np.imag(img)

    phi_reshaped_real_part = cv2.resize(real_part, (Ne, Ne), interpolation=cv2.INTER_LINEAR)
    try:
        phi_reshaped_imaginary_part = cv2.resize(imaginary_part, (Ne, Ne), interpolation=cv2.INTER_LINEAR)
        phi_reshaped = phi_reshaped_real_part + I* phi_reshaped_imaginary_part
    except:
        phi_reshaped = phi_reshaped_real_part
    return phi_reshaped

def thresholed_log(x, threshold_dB=-30):
    x[x<10**(threshold_dB/10)] = 10**(threshold_dB/10)
    return 10*np.log10(x)

def get_psf(wavefront, zoom, Ne):
    # Calculating necessary parameters
    N_phi = int(Ne // (2 ** zoom))

    phi_reshaped = resize_image(wavefront, N_phi)
    phi_reshaped[np.isnan(phi_reshaped)] = 0

    psf = np.abs(fftshift(fft2(phi_reshaped, (Ne, Ne))))**2
    perfect_psf = np.abs(fftshift(fft2(np.abs(phi_reshaped), (Ne, Ne))))**2

    return psf/perfect_psf.max()

def get_mtf(wavefront, zoom, Ne):
    psf = get_psf(wavefront, zoom, Ne)
    mtf = np.abs(fftshift(fft2(psf)))
    mtf /= mtf.max()

    return mtf
