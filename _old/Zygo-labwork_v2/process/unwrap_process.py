# -*- coding: utf-8 -*-
"""*unwrap_process.py* file.

This file contains functions to unwrap the phase.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (LEnsE) <julien.villemejane@institutoptique.fr>

"""


'''
unwrapped_phase = unwrap_phase(wrapped_phase)/(2*np.pi)

# Display of the surface
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surface = ax.plot_surface(X[400:1200, 750:1900], Y[400:1200, 750:1900], unwrapped_phase[400:1200, 750:1900], cmap='magma')
ax.set_title('Unwrapped surface')
cbar = fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'Default magnitude ($\lambda$)')
#plt.show()

## Statistics
PV, RMS = surface_statistics(unwrapped_phase[400:1200, 750:1900])
print(f"PV: {PV:.2f} λ | RMS: {RMS:.2f} λ")


## Zernike coefficients
print('Calculating Zernike coefficients...')
max_order = 3
coeffs = get_zernike_coefficient(unwrapped_phase, max_order=max_order)

plt.figure()
plt.plot(coeffs)
plt.title('Zernike Coefficients')

# Remove specified aberration
aberrations_considered = np.ones(max_order, dtype=int)
print(aberrations_considered)

corrected_phase, XX, YY = remove_aberration(unwrapped_phase[400:1200, 750:1900], aberrations_considered)

PV, RMS = surface_statistics(corrected_phase[400:1200, 750:1900])
print(f"PV: {PV:.2f} λ | RMS: {RMS:.2f} λ")

## Display initial and corrected phase
# Création de la figure et des sous-graphiques en 3D
fig = plt.figure(figsize=(14, 6))

# Initial phase with aberrations
min_value = np.round(np.min(unwrapped_phase[400:1200, 750:1900]), 0) - 1
max_value = np.round(np.max(unwrapped_phase[400:1200, 750:1900]), 0) + 1

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
surf1 = ax1.plot_surface(XX, YY, unwrapped_phase[400:1200, 750:1900], cmap='viridis')
ax1.set_zlim([min_value, max_value])
ax1.set_title('Initial phase with aberrations')
fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

# Corrected phase without specified aberrations
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
surf2 = ax2.plot_surface(XX, YY, corrected_phase, cmap='viridis')
ax2.set_zlim([min_value, max_value])
ax2.set_title('Corrected phase without specified aberrations')
fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

# Ajustement des paramètres de la figure
fig.tight_layout()

plt.show()

'''
