import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def generate_interference_pattern(size, step, angle, shift_x=0, amp=75, amp_noise=0):
    """
    Génère une matrice représentant des franges d'interférences avec décalage.

    Parameters:
    - size: tuple de deux entiers (hauteur, largeur) pour la taille de la matrice
    - step: espacement entre les franges
    - angle: angle des franges en degrés
    - shift_x: décalage des franges selon l'axe x

    Returns:
    - pattern: matrice 2D de taille 'size' avec les franges d'interférences
    """
    height, width = size
    angle_rad = np.radians(angle)

    # Grid for coordinates
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    # Shift
    x_shifted = x + shift_x
    noise = np.random.normal(0, amp_noise, x.shape)
    x_shifted += noise
    # Add noise

    # Process coordinates
    x_rot = x_shifted * np.cos(angle_rad) + y * np.sin(angle_rad)

    # interfering drawing
    pattern = amp * (np.sin(2 * np.pi * x_rot / step)+1) + 30
    pattern = pattern.astype(np.uint8)

    return pattern


def calibration(patterns, number_measures, display=False):
    x_min = 50
    x_max = 450
    y_min = 50
    y_max = 250
    average_for_all_voltages = []
    # Générer la rampe de tension en écrivant chaque valeur successivement
    start_voltage = 0
    end_voltage = 5
    ramp = np.linspace(start_voltage, end_voltage, len(patterns[0]))

    print(f'Nb Mesures = {number_measures}')
    for i in range(number_measures):
        image_for_all_voltages = []
        patternss = patterns[i]
        print(f'Shape of pattern {i} = {patternss[0].shape}')

        for j, voltage in enumerate(ramp):
            print(f"{i + 1}e mesure | V={voltage:.2f}/{end_voltage:.2f}")
            raw_array = patternss[j][y_min:y_max, x_min:x_max] / number_measures
            image_for_all_voltages.append(raw_array)
        average_for_all_voltages.append(image_for_all_voltages)

    average_for_all_voltages = np.mean(np.array(average_for_all_voltages), axis=0)
    print(f'Shape Average for all = {average_for_all_voltages.shape}')
    average_for_all_voltages = np.squeeze(np.array(average_for_all_voltages))

    if display:
        plt.figure()
        plt.imshow(average_for_all_voltages[2])
        plt.show()
    '''
    diff_images = []
    for i in range (len(ramp)-1):
        diff_images.append(average_for_all_voltages[i]-average_for_all_voltages[i+1])
        if display:
            plt.figure()
            plt.imshow(diff_images[i])
            plt.show()
    '''

    phi = np.array(list(map(lambda img: 1 - img / average_for_all_voltages[0], average_for_all_voltages)))

    animated_interference(phi, -1, 1)

    if display:
        for i in range(0,len(ramp)):
            print(phi[i].dtype)
            print(f'{i} ==> {np.max(phi[i])}')
            if display:
                plt.figure()
                plt.imshow(phi[i])
                plt.show()

    '''
    phi_norm = []

    for i in range(1, len(ramp)):
        print(f'{i} ==> {phi[i].shape}')
        phi_norm.append(phi[i] / np.max(phi[i]))
    phi_norm = np.array(phi_norm)

    print(f'Max Phi Norm = {np.max(phi_norm)}')
    '''

    avg_phi = []
    for i in range(1, len(phi)):
        avg_phi.append(np.mean(phi[i]))
    # avg_phi = np.mean(np.mean(phi, axis=1), axis=1) - np.pi / 2
    print(f'Max Avg Phi = {np.max(avg_phi)}')
    print(f'Min Avg Phi = {np.min(avg_phi)}')

    amp_phi = (np.max(avg_phi)-np.min(avg_phi))/2
    avg_phi_norm = (avg_phi/amp_phi) - np.mean(avg_phi/amp_phi)

    print(f'Max Avg_phi = {np.max(avg_phi_norm)} / {np.min(avg_phi_norm)}')

    phase = np.arcsin(avg_phi_norm)

    plt.figure()
    plt.plot(ramp[:-1], avg_phi_norm)
    plt.plot(ramp[:-1], phase)
    plt.show()


    '''
    phase = np.rad2deg(np.arcsin(np.nanmean(np.nanmean(phi[1:10] / np.nanmax(phi[1:10], axis=0), axis=2), axis=1)) - np.pi / 2)
    # phase = np.mean(np.mean(phi, axis=2), axis=1)
    print(phase.shape)
    
    phase -= phase[0]

    diff_phase = np.abs(np.diff(phase, prepend=0))

    # phase[0] = 0
    for i in range(1, len(phase)):
        phase[i] = phase[i - 1] + diff_phase[i]

    phase = 2 * phase

    plt.figure()
    plt.plot(ramp, phase)
    plt.show()

    eps = 1  # °
    V_1 = np.nanmean(ramp[np.where(np.abs(phase - 0) < eps)])
    V_2 = np.nanmean(ramp[np.where(np.abs(phase - 90) < eps)])
    V_3 = np.nanmean(ramp[np.where(np.abs(phase - 180) < eps)])
    V_4 = np.nanmean(ramp[np.where(np.abs(phase - 270) < eps)])
    V_5 = np.nanmean(ramp[np.where(np.abs(phase - 360) < eps)])

    print(f"V(phi=0°)={V_1}")
    print(f"V(phi=90°)={V_2}")
    print(f"V(phi=180°)={V_3}")
    print(f"V(phi=270°)={V_4}")
    print(f"V(phi=180°)={V_5}")
    '''

def animated_interference(patterns, min_val=-1, max_val=1):
    nb = len(patterns)
    # Créer la figure et les axes
    fig, ax = plt.subplots()
    img = ax.imshow(patterns[0], cmap='gray', vmin=min_val, vmax=max_val)

    def update(frame):
        img.set_data(patterns[frame])
        return img,

    # Créer l'animation
    ani = FuncAnimation(fig, update, frames=nb, blit=True, interval=100)

    # Afficher l'animation
    plt.show()

if __name__ == '__main__':
    import sys
    x = np.linspace(0,3*np.pi, 100)
    y = np.sin(x + 1)

    plt.figure()
    plt.plot(x, y)

    yy = np.arcsin(y)

    plt.figure()
    plt.plot(x, yy)
    plt.show()

    #sys.exit(0)


    # Parameters
    size = (300, 500)  # taille de la matrice
    step = 50  # pas (espacement entre les franges)
    angle = 30  # angle en degrés
    number_measures = 5

    ## Generate a list of array with
    k = 1.7 #
    x_value = np.linspace(0, k*step, 101)

    patterns2 = []
    for k in range(number_measures):
        patterns = []
        for x in x_value:
            pattern = generate_interference_pattern(size, step, angle, shift_x=x, amp_noise=10)
            patterns.append(pattern)
        patterns2.append(patterns)

    animated_interference(patterns2[0], min_val=0, max_val=255)
    calibration(patterns2, number_measures, display=False)





    '''
    ## Animation
    # Créer la figure et les axes
    fig, ax = plt.subplots()
    img = ax.imshow(patterns[0], cmap='gray', vmin=0, vmax=255)

    def update(frame):
        img.set_data(patterns[frame])
        return img,

    # Créer l'animation
    ani = FuncAnimation(fig, update, frames=len(x_value), blit=True, interval=50)

    # Afficher l'animation
    plt.show()
    '''
