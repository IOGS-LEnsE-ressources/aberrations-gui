import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import time

x_nb = 2000
y_nb = 2000

x = np.linspace(-1,1,x_nb)
y = np.linspace(-1,1,y_nb)
X, Y = np.meshgrid(x,y)

def f(x, y):
    s = np.hypot(x, y)
    phi = np.arctan2(y, x)
    tau = s + s*(1-s)/5 * np.sin(6*phi)
    return 5*(1-tau) + tau

T = f(X, Y)
# Choose npts random point from the discrete domain of our model function
npts = int(0.05*x_nb*y_nb)
print(f'N = {npts}')
x_nan, y_nan = np.random.randint(0, x_nb, size=npts), np.random.randint(0, y_nb, size=npts)

T[x_nan, y_nan] = 0

px = x[x_nan]
py = y[y_nan]

fig, ax = plt.subplots(nrows=2, ncols=2)
# Plot the model function and the randomly selected sample points
ax[0,0].imshow(T, interpolation='none', cmap='viridis')
ax[0,0].scatter(px, py, c='k', alpha=0.2, marker='.')
ax[0,0].set_title('Sample points on f(X,Y)')


# Interpolate using three different methods and plot
for i, method in enumerate(('nearest', 'linear', 'cubic')):
    start_time = time.time()
    Ti = griddata((px, py), f(px,py), (X, Y), method=method)
    stop_time = time.time()
    print(f'Inter Time {method} = {stop_time - start_time}')
    r, c = (i+1) // 2, (i+1) % 2
    ax[r,c].imshow(Ti, interpolation='none', cmap='viridis')
    #ax[r,c].contourf(X, Y, Ti)
    ax[r,c].set_title("method = '{}'".format(method))


plt.tight_layout()
plt.show()