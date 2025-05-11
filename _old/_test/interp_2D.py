from scipy.interpolate import RegularGridInterpolator
from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt
import time

# Fonction quadratique
def ff(x, y):
    return x**2 + y**2

# Définir les dimensions de l'échantillon
x_samples = 1000
y_samples = 800

# Créer un espace d'échantillonnage
x = np.linspace(0, 1, x_samples)
y = np.linspace(0, 1, y_samples)
#xg, yg = np.meshgrid(np.arange(x_samples), np.arange(y_samples), indexing='ij')
xg, yg = np.meshgrid(x, y, indexing='ij')

# Générer les données de l'échantillon
data = ff(xg, yg)

print(data.dtype)


print(f'Random Start')
# Introduire des valeurs manquantes (NaN)
np.random.seed(42)  # Pour reproductibilité
for _ in range(200):
    x_k = np.random.randint(0, x_samples)
    y_k = np.random.randint(0, y_samples)
    # data[x_k, y_k] = np.nan

# Créer un masque pour les valeurs non-NaN
mask = ~np.isnan(data)

# Obtenir les coordonnées des points non-NaN
coords = np.array(np.nonzero(mask)).T
values = data[mask]

# Coordonnées de la grille cible
#grid_x, grid_y = np.meshgrid(np.arange(x_samples), np.arange(y_samples), indexing='ij')

print(f'Interp Start')

start_time = time.time()
# Interpolation des données manquantes
interpolated_data = griddata(coords, values, (xg, yg), method='cubic')

stop_time = time.time()

print(f'Inter Time = {stop_time-start_time}')

# Interpolation des données manquantes
#interpolated_data = griddata(coords, values, (xg, yg), method='cubic')

# Créer une figure avec plusieurs subplots
fig = plt.figure(figsize=(18, 6))

# Affichage des données originales
ax1 = fig.add_subplot(221)
im1 = ax1.imshow(data, interpolation='none', cmap='viridis')
ax1.set_title('Données Originales')
fig.colorbar(im1, ax=ax1)

# Affichage du masque
ax2 = fig.add_subplot(222)
im2 = ax2.imshow(mask, interpolation='none', cmap='viridis')
ax2.set_title('Masque')
fig.colorbar(im2, ax=ax2)

# Affichage des données interpolées
ax3 = fig.add_subplot(223)
im3 = ax3.imshow(interpolated_data, interpolation='none', cmap='viridis')
ax3.set_title('Données Interpolées')
fig.colorbar(im3, ax=ax3)

# Affichage 3D des données et de l'interpolation
ax4 = fig.add_subplot(224, projection='3d')
ax4.scatter(xg.ravel(), yg.ravel(), data.ravel(), s=60, c='k', label='Données')
ax4.plot_wireframe(xg, yg, interpolated_data, rstride=3, cstride=3, alpha=0.4, color='m', label='Interpolation Cubique')
ax4.set_title('Données et Interpolation 3D')

# Afficher la figure
plt.tight_layout()
plt.show()




'''
interp = RegularGridInterpolator((x, y), data, method='cubic',
                                 bounds_error=False, fill_value=None)

print(f'Data = {data}')
#print(f'Interp Data = {interp(xg, yg)}')


import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
#ax.scatter(xg.ravel(), yg.ravel(), data.ravel(), s=60, c='k', label='data')

xx = np.linspace(-2, 4, 31)
yy = np.linspace(-4, 9, 31)
X, Y = np.meshgrid(xx, yy, indexing='ij')

# interpolator
ax.plot_wireframe(X, Y, interp((X, Y)), rstride=3, cstride=3, alpha=0.4, color='m', label='linear interp')
# ground truth
ax.plot_wireframe(X, Y, ff(X, Y), rstride=3, cstride=3, alpha=0.4, label='ground truth')
plt.legend()
plt.show()

'''
