import numpy as np
import matplotlib.pyplot as plt

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

def circled_energy(psf, theorical_psf, f_number, psf_zoom):
    x_centroid, y_centroid = calculate_centroid(psf)

    y_dim, x_dim = psf.shape
    x = np.arange(x_dim)
    y = np.arange(y_dim)
    X, Y = np.meshgrid(x, y)

    _X = X - x_centroid * np.ones_like(X)
    _Y = Y - y_centroid * np.ones_like(Y)
    R = np.sqrt(_X**2 + _Y**2)

    circled_energy = np.array([np.sum(psf[R<ray]) for ray in range(x_dim//2)])/np.sum(psf)
    theorical_circled_energy = np.array([np.sum(theorical_psf[R<ray]) for ray in range(x_dim//2)])/np.sum(psf)

    LAMBDA = 632.8e-6 #mm
    image_radius = LAMBDA*f_number
    pupil_ratio = 2**psf_zoom

    r = (1e3) * (image_radius/pupil_ratio) * np.array(list(range(x_dim//2)))
    plt.figure()
    plt.plot(r, circled_energy, label='Réponse percussionnelle')
    plt.plot(r, theorical_circled_energy, label='Limite de diffraction')
    plt.xlabel('en µm')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    x = y = np.linspace(-1, 1, 100)
    X, Y = np.meshgrid(x, y)
    c = np.ones_like(X)
    c[X**2+Y**2>1/7] = 0

    psf = np.fft.fftshift(np.fft.fft2(c))
    plt.imshow(np.abs(psf))
    plt.show()

    circled_energy(np.abs(psf), np.abs(psf)+2*np.random.rand(), 10, 2)