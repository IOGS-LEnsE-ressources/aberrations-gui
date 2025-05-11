# -*- coding: utf-8 -*-
"""
File: zernike_coefficients.py

This file is associated with a first-year and second year engineering lab in photonics.
First-year subject: http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf
Second-year subject: https://lense.institutoptique.fr/s8-aberrations/

Development details for this interface:
https://iogs-lense-ressources.github.io/camera-gui/contents/applis/appli_Zygo_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import matplotlib.pyplot as plt
import numpy as np
import math

if __name__ == '__main__':
    from polar_cartesian_transformations import *


aberrations_type = {
    "piston": [0],
    "tilt": [1, 2],
    "defocus": [3],
    "astig3" : [4, 5],
    "coma3" : [6, 7],
    "sphere3" : [8],
    "trefoil5" : [9, 10],
    "astig5" : [11, 12],
    "coma5" : [13, 14],
    "sphere5" : [15],
    "quadra7" : [16, 17],
    "trefoil7" : [18, 19],
    "astig7" : [20, 21],
    "coma7" : [22, 23],
    "sphere7" : [24],
    "penta9" : [25, 26],
    "quadra9" : [27, 28],
    "trefoil9" : [29, 30],
    "astig9" : [31, 32],
    "coma9" : [33, 34],
    "sphere9" : [35],
    "sphere11" : [36]
}

aberrations_list = [
    "tilt",
    "defocus",
    "astig3" ,
    "coma3",
    "sphere3",
    "trefoil5",
    "astig5",
    "coma5",
    "sphere5",
    "quadra7",
    "trefoil7",
    "astig7",
    "coma7",
    "sphere7",
    "penta9",
    "quadra9",
    "trefoil9",
    "astig9",
    "coma9",
    "sphere9",
    "sphere11" 
]


class Zernike:
    """
    Notes
    -----
    For more information on Zernike polynomials and their coefficients, refer to:
    https://iopscience.iop.org/article/10.1088/2040-8986/ac9e08/pdf
    """

    def __init__(self, max_order:int = 36):
        self.max_order = max_order
        self.surface = None

        self.corrected_phase = None
        self.coeff_calculated = False  # Zernike coefficients are calculated
        self.coeff_list = [None] * (self.max_order + 1)
        self.polynomials = [None] * (self.max_order + 1)
        self.X = None
        self.Y = None
        self.pow1 = None
        self.pow2 = None

    def set_surface(self, surface):
        self.surface = surface
        print(type(self.surface))
        print(f'surface shape = {self.surface.shape}')
        print(f'surface Infos = {np.nanmean(self.surface)} / {np.nanmin(self.surface)} / {np.nanmax(self.surface)}')
        # Dimensions of the surface
        a, b = self.surface.shape

        # Creating coordinate grids
        x = np.linspace(-1, 1, b)
        y = np.linspace(-1, 1, a)
        self.X, self.Y = np.meshgrid(x, y)
        self.pow1 = (self.X**2 - self.Y**2)
        self.pow2 = (self.X**2 + self.Y**2)

        self.corrected_phase = np.zeros_like(self.surface)

    def process_cartesian_polynomials(self, noll_index: int) -> np.ndarray:
        if noll_index == 0:     # Piston
            return np.ones_like(self.X)
        elif noll_index == 1:   # x-Tilt
            return 2*self.X
        elif noll_index == 2:   # y-Tilt
            return 2*self.Y
        elif noll_index == 3:   # defocus
            return np.sqrt(3)*(2*self.pow2 - 1)
        ## ORDER 3
        elif noll_index == 4:   # defocus / 45d primary astig
            return 2*np.sqrt(6)*(self.X * self.Y)
        elif noll_index == 5:   # defocus / 0d primary astig
            return np.sqrt(6)*self.pow1
        elif noll_index == 6:   # Primary coma
            return np.sqrt(8)*self.Y*(3*self.pow2-2)
        elif noll_index == 7:   # Primary coma
            return np.sqrt(8)*self.X*(3*self.pow2-2)
        elif noll_index == 8:   # Primary coma
            return np.sqrt(8)*self.Y*(3*self.X**2 - self.Y**2)
        ## ORDER 5
        elif noll_index == 9:   # Primary coma
            return np.sqrt(8)*self.X*(self.X**2 - 3*self.Y**2)
        elif noll_index == 10:   # Primary Spherical Aber.
            return np.sqrt(5)*(6*self.pow2**2 - 6*self.pow2 + 1)
        elif noll_index == 11:   # Primary Spherical Aber.
            return np.sqrt(10)*self.pow1*(4*self.pow2 - 3)
        elif noll_index == 12:   # Primary Spherical Aber.
            return 2*np.sqrt(10)*self.X*self.Y*(4*self.pow2 - 3)
        elif noll_index == 13:   # Primary Spherical Aber.
            return np.sqrt(10)*(self.pow2**2 - 8*self.X**2*self.Y**2)
        elif noll_index == 14:   # Primary Spherical Aber.
            return 4*np.sqrt(10)*self.X*self.Y*self.pow1
        elif noll_index == 15:   # Secondary coma
            return np.sqrt(12)*self.X*(10*(self.pow2)**2 - 12*(self.pow2) + 3)
        ## ORDER 7
        elif noll_index == 16:   # Secondary coma
            return np.sqrt(12)*self.Y*(10*(self.pow2)**2 - 12*(self.pow2) + 3)
        elif noll_index == 17:   # Secondary coma
            return np.sqrt(12)*self.X*(self.X**2 - 3*self.Y**2)*(5*self.pow2 - 4)
        elif noll_index == 18:   # Secondary coma
            return np.sqrt(12)*self.Y*(3 * self.X**2 - self.Y**2)*(5*self.pow2 - 4)
        elif noll_index == 19:   # Secondary coma
            return np.sqrt(12)*self.X*(16*self.X**4 - 20*self.X**2*self.pow2 + 5*self.pow2**2)
        elif noll_index == 20:   # Secondary coma
            return np.sqrt(12)*self.Y*(16*self.Y**4 - 20*self.Y**2*self.pow2 + 5*self.pow2**2)
        elif noll_index == 21:   # Secondary Spherical Aber.
            return np.sqrt(7)*(20*self.pow2**3 - 30*self.pow2**2 + 12*self.pow2 - 1)
        elif noll_index == 22:   # Secondary Spherical Aber.
            return 2*np.sqrt(14)*self.X*self.Y*(15*self.pow2**2 - 20*self.pow2 + 6)
        elif noll_index == 23:   # Secondary Spherical Aber.
            return np.sqrt(14)*self.pow1*(15*self.pow2**2 - 20*self.pow2 + 6)
        elif noll_index == 24:   # Secondary Spherical Aber.
            return 4*np.sqrt(14)*self.X*self.Y*self.pow1*(6*self.pow2 - 5)
        ## ORDER 9
        elif noll_index == 25:   # Secondary Spherical Aber.
            return np.sqrt(14)*(self.pow2**2 - 8*self.X**2*self.Y*2)*(6*self.pow2 - 5)
        elif noll_index == 26:   # Secondary Spherical Aber.
            return np.sqrt(14)*self.X*self.Y*(32*self.X**4 - 32*self.X**2*self.pow2 + 6*self.pow2**2)
        elif noll_index == 27:   # Secondary Spherical Aber.
            return np.sqrt(14)*(32*self.X**6 - 48*self.X**4*self.pow2 + 18*self.X**2*self.pow2**2 - self.pow2**3)

        elif noll_index == 28:   # Secondary Spherical Aber.
            return 4*self.Y*(35*self.pow2**3-60*self.pow2**2+30*self.pow2-4)
        elif noll_index == 29:   # Secondary Spherical Aber.
            return 4*self.X*(35*self.pow2**3-60*self.pow2**2+30*self.pow2-4)
        elif noll_index == 30:   # Tertiary y-Coma
            return 4*self.Y*(3*self.X**2-self.Y**2)*(21*self.pow2**2-30*self.pow2+10)
        elif noll_index == 31:   # Tertiary x-Coma
            return 4*self.X*(self.X**2-3*self.Y**2)*(21*self.pow2**2-30*self.pow2+10)
        elif noll_index == 32:   # Secondary Spherical Aber.
            return 4*(4*self.X**2*self.Y*self.pow1+self.Y*self.pow2**2-8*self.X**2*self.Y**3)*(7*self.pow2-6)
        elif noll_index == 33:   # Secondary Spherical Aber.
            return 4*(self.X*self.pow2**2-8*self.X**3*self.Y**2-4*self.X*self.Y**2*self.pow1)*(7*self.pow2-6)
        elif noll_index == 34:   # Secondary Spherical Aber.
            return 8*self.X**2*self.Y*(3*self.pow2**2-16*self.X**2*self.Y**2)+4*self.Y*self.pow1*(self.pow2**2-16*self.X**2*self.Y**2)
        elif noll_index == 35:   # Secondary Spherical Aber.
            return 4*self.X*self.pow1*(self.pow2**2-16*self.X**2*self.Y**2)-8*self.X*self.Y**2*(3*self.pow2**2-16*self.X**2*self.Y**2)

        ## ORDER 11
        elif noll_index == 36: # Tertiary spherical
            return 3*(70*self.pow2**4-140*self.pow2**3 +90*self.pow2**2-20*self.pow2+1)

    def process_zernike_coefficient(self, order: int) -> np.ndarray:
        if order <= self.max_order:
            if self.coeff_list[order] is None:
                Z_nm = self.process_cartesian_polynomials(order)
                # Mask NaN values
                valid_mask = ~np.isnan(self.surface)
                surface_filtered = self.surface[valid_mask]
                Z_nm_filtered = Z_nm[valid_mask]

                self.coeff_list[order] = np.sum(surface_filtered * Z_nm_filtered) / np.sum(Z_nm_filtered ** 2)
                print(f'Z{order} = {self.coeff_list[order]}')
                print(f'\t Mean = {np.nanmean(Z_nm)} / {np.nanmean(Z_nm_filtered)}')
        else:
            return None

    def process_surface_correction(self, aberrations: list[str]):
        self.corrected_phase = np.zeros_like(self.surface)
        for k, type_ab in enumerate(aberrations):
            coeffs = aberrations_type[type_ab]
            for c in coeffs:
                if self.coeff_list[c] is None:
                    self.process_zernike_coefficient(c)
                self.corrected_phase += self.coeff_list[c] * self.process_cartesian_polynomials(c)
        # Correction de la surface
        new_surface = self.surface - self.corrected_phase
        return self.corrected_phase, new_surface
    
    def  phase_correction(self, corrected_coeffs: list[float]):
        self.corrected_phase = np.zeros_like(self.surface)
        for i,c in enumerate(corrected_coeffs):
            self.corrected_phase += c * self.process_cartesian_polynomials(i)
        # Correction de la surface
        new_surface = self.surface - self.corrected_phase

        return self.corrected_phase, new_surface
    

def display_3_figures(init, zern, corr):
    """Displaying results."""
    vmin = np.nanmin([init.min(), corr.min()])
    vmax = np.nanmax([init.max(), corr.max()])

    init = np.ma.array(init, mask=np.isnan(init))
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    im1 = axs[0].imshow(init, extent=(-1, 1, -1, 1), vmin=vmin, vmax=vmax, cmap='jet')
    axs[0].set_title("Initial Surface")
    fig.colorbar(im1, ax=axs[0])

    im2 = axs[1].imshow(zer, extent=(-1, 1, -1, 1), vmin=vmin, vmax=vmax, cmap='jet')
    axs[1].set_title("Correction")
    fig.colorbar(im2, ax=axs[1])

    corr = np.ma.array(corr, mask=np.isnan(corr))
    im3 = axs[2].imshow(corr, extent=(-1, 1, -1, 1), vmin=vmin, vmax=vmax, cmap='jet')
    axs[2].set_title("Corrected surface")
    fig.colorbar(im3, ax=axs[2])

    print(f'INIT = max = {np.max(init)} / min = {np.min(init)} / Mean = {np.mean(init)}')
    print(f'CORR = max = {np.max(corr)} / min = {np.min(corr)} / Mean = {np.mean(corr)}')

    plt.show()


def zernike_radial(n, m, r):
    """ Calcule la composante radiale des polynômes de Zernike. """
    R = np.zeros_like(r)
    for k in range((n - abs(m)) // 2 + 1):
        c = (-1)**k * math.factorial(n - k) / (
            math.factorial(k) *
            math.factorial((n + abs(m)) // 2 - k) *
            math.factorial((n - abs(m)) // 2 - k)
        )
        R += c * r**(n - 2*k)
    return R


def zernike2(n, m, rho, theta):
    """ Calcule un polynôme de Zernike. """
    if m >= 0:
        return zernike_radial(n, m, rho) * np.cos(m * theta)
    else:
        return zernike_radial(n, -m, rho) * np.sin(-m * theta)


def elliptic_mask(image, cx=0, cy=0, a=0.5, b=0.5):
    """Create elliptic mask on an image.
    :param image: initial image to mask
    :param cx: X-axis center
    :param cy: Y-axis center
    :param a: X-axis dimension
    :param b: Y-axis dimension
    """
    height, width = image.shape
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    return ((X - cx) ** 2) / a ** 2 + ((Y - cy) ** 2) / b ** 2 < 1


if __name__ == "__main__":
    '''
    # Grid definition
    N, M = 256, 128  # Taille de la grille
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, M)
    X, Y = np.meshgrid(x, y)
    # Circular mask
    R = np.sqrt(X ** 2 + Y ** 2)
    theta = np.arctan2(Y, X)
    mask = R < 1


    # Surface creation
    tilt_x = -0.27
    tilt_y = 0.35
    surface = tilt_x * X + tilt_y * Y #+ np.exp(-3 * R ** 2) + 0.48 * (2 * R ** 2 - 1)


    mask = elliptic_mask(surface, 0.2, 0, a=0.4)

    # Coma horizontale (Z3^1) et verticale (Z3^-1)
    coma_horizontal = zernike(3, 1, R, theta)  # Z3^1
    coma_vertical = zernike(3, -1, R, theta)  # Z3^-1
    surface += coma_vertical #+coma_vertical

    surface[~mask] = np.nan
    '''
    ## Other test
    import os
    import scipy
    def read_mat_file(file_path: str) -> dict:
        """
        Load data and masks from a .mat file.
        The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
        Additional masks can be included in a dictionary key called "Masks".

        :param file_path: Path and name of the file to load.
        :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
        """
        if os.path.exists(file_path):
            data = scipy.io.loadmat(file_path)
            return data
        else:
            print('read_mat_file / No File')

    def split_3d_array(array_3d, size: int = 5):
        # Ensure the array has the expected shape
        if array_3d.shape[2] % size != 0:
            raise ValueError(f"The loaded array does not have the expected third dimension size of {size}.")
        # Extract the 2D arrays
        arrays = [array_3d[:, :, i].astype(np.float32) for i in range(array_3d.shape[2])]
        return arrays

    ### START !!
    data = read_mat_file("../_data/test3.mat")
    images_mat = data['Images']
    images = split_3d_array(images_mat)

    mask = data['Masks'].squeeze()
    mask = mask.astype(bool)
    print(mask.dtype)

    plt.figure()
    plt.imshow(images[0]*mask)
    plt.show()

    from lensepy.images.conversion import find_mask_limits, crop_images
    from scipy.ndimage import gaussian_filter
    from process.hariharan_algorithm import *
    from skimage.restoration import unwrap_phase
    #>> Wrapped phase
    if mask is not None:
        # Crop images around the mask
        top_left, bottom_right = find_mask_limits(mask)
        height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
        pos_x, pos_y = top_left[1], top_left[0]
        cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
        images_c = crop_images(images, (height, width), (pos_x, pos_y))
        # Filtering images to avoid noise
        images_f = list(map(lambda x: gaussian_filter(x, 10), images_c))

        # Process Phase
        wrapped_phase = hariharan_algorithm(images_f, cropped_mask_phase)
        wrapped_phase = np.ma.masked_where(np.logical_not(cropped_mask_phase), wrapped_phase)
        # End of process

    plt.figure()
    plt.imshow(cropped_mask_phase)
    plt.show()

    print(f'Cropped Mask type = {type(cropped_mask_phase)} / {cropped_mask_phase.dtype}')

    plt.figure()
    plt.imshow(wrapped_phase)
    plt.show()

    #>> Unwrapped phase
    unwrapped_phase = unwrap_phase(wrapped_phase) / (2 * np.pi)

    #unwrapped_phase = np.ma.masked_where(np.logical_not(cropped_mask_phase), unwrapped_phase)
    unwrapped_phase_to_correct = unwrapped_phase.copy()
    unwrapped_phase_to_correct[~cropped_mask_phase] = np.nan
    unwrapped_phase_done = True

    plt.figure()
    plt.imshow(unwrapped_phase)
    plt.show()

    def statistics_surface(surface):
        # Process (Peak-to-Valley)
        PV = np.round(np.nanmax(surface) - np.nanmin(surface), 3)
        RMS = np.round(np.nanstd(surface), 3)
        return PV, RMS

    print(f'Unwrapped = {statistics_surface(unwrapped_phase_to_correct)}')

    zer = Zernike(28)
    zer.set_surface(unwrapped_phase_to_correct)

    for k in range(28):
        zer.process_zernike_coefficient(k)

    #> Correction
    ab_list = ['tilt']  # ,'defocus'] #,'coma1','sphere1','coma2','sphere2']

    correction, new_image = zer.process_surface_correction(ab_list)

    # display_3_figures(unwrapped, correction, new_image)

    print(f'Correction = {statistics_surface(new_image)}')

    '''


    # Crop images around the mask
    from lensepy.images.conversion import find_mask_limits, crop_images
    from scipy.ndimage import gaussian_filter
    top_left, bottom_right = find_mask_limits(mask)
    height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
    pos_x, pos_y = top_left[1], top_left[0]
    cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
    images_c = crop_images(images, (height, width), (pos_x, pos_y))
    # Filtering images to avoid noise
    images_f = list(map(lambda x: gaussian_filter(x, 10), images_c))

    # Calculate hariharan and unwrap phase in surface
    from process.hariharan_algorithm import *
    wrapped = hariharan_algorithm(images_f, cropped_mask_phase)
    wrapped = np.ma.masked_where(np.logical_not(cropped_mask_phase), wrapped)

    def statistics_surface(surface):
        # Process (Peak-to-Valley)
        PV = np.round(np.nanmax(surface) - np.nanmin(surface), 3)
        RMS = np.round(np.nanstd(surface), 3)
        return PV, RMS

    plt.figure()
    plt.imshow(wrapped)
    plt.colorbar()

    print(f'Wrapped = {statistics_surface(wrapped)}')

    from skimage.restoration import unwrap_phase
    unwrapped_t = unwrap_phase(wrapped) / (2*np.pi)
    unwrapped = np.ma.masked_where(np.logical_not(cropped_mask_phase), unwrapped_t).copy()

    unwrapped[~cropped_mask_phase] = np.nan

    print(f'Unwrapped = {statistics_surface(unwrapped)}')

    plt.figure()
    plt.imshow(unwrapped)
    plt.colorbar()

    plt.show()

    zer = Zernike(28)
    zer.set_surface(unwrapped)
    for i in range(28):
        zer.process_zernike_coefficient(i)
    ab_list = ['tilt']  #,'defocus'] #,'coma1','sphere1','coma2','sphere2']

    correction, new_image = zer.process_surface_correction(ab_list)

    #display_3_figures(unwrapped, correction, new_image)


    print(f'Correction = {statistics_surface(new_image)}')
    '''

