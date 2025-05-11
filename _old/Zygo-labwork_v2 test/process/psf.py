import numpy as np
#import pyfits
import matplotlib.pyplot as plt
from scipy.fftpack import fftshift, ifftshift, fft2, ifft2

from process.zernike_coefficients import *

def PSF(complx_pupil):
    PSF = ifftshift(fft2(fftshift(complx_pupil)))
    PSF = (np.abs(PSF))**2 #or PSF*PSF.conjugate()
    PSF = PSF/PSF.sum() #normalizing the PSF
    return PSF

def PSF2(complx_pupil):
    #inversion de fftshift et ifftshift
    PSF = fftshift(fft2(ifftshift(complx_pupil)))
    PSF = (np.abs(PSF))**2 #or PSF*PSF.conjugate()
    PSF = PSF/PSF.sum() #normalizing the PSF
    return PSF

def OTF(psf):
    otf = ifftshift(psf) #move the central frequency to the corner
    otf = fft2(otf)
    otf_max = float(otf[0,0]) #otf_max = otf[size/2,size/2] if max is shifted to center
    otf = otf/otf_max #normalize by the central frequency signal
    return otf

def MTF(otf):
    mtf = np.abs(otf)
    return mtf

def complex_pupil(A,Mask):
    abbe =  np.exp(1j*A)
    abbe_z = np.zeros((len(abbe),len(abbe)), dtype=np.complex128)
    abbe_z = Mask*abbe
    return abbe_z