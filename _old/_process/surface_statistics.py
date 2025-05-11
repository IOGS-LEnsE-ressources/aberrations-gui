import numpy as np

def statistique_surface(surface):
    # Calcul de PV (Peak-to-Valley)
    PV = np.nanmax(surface) - np.nanmin(surface)
    RMS = np.nanstd(surface)
    return PV, RMS