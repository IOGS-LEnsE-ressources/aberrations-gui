if __name__ == '__main__':
    from hariharan_algorithm import *
    from initialization_parameters import read_default_parameters
else:
    from process.hariharan_algorithm import *
    from process.initialization_parameters import read_default_parameters

import nidaqmx
import time
from scipy.ndimage import gaussian_filter

def get_phase(parent, sigma_gaussian_filter=3):
    images = []
    mask = parent.mask
    if __name__ == '__main__':
        str_voltages = read_default_parameters('./config.txt')['Piezo voltage']
    else:
        str_voltages = read_default_parameters('config.txt')['Piezo voltage']
    voltages = list(str_voltages.split(','))
    
    try:
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5)

            task.start()

            parent.camera_thread.stop()
            parent.camera.init_camera()
            parent.camera.alloc_memory()
            parent.camera.start_acquisition()

            #import matplotlib.pyplot as plt
            #plt.new_figure_manager

            for i in range(5):
                # plt.subplot(1,5,i+1)
                # print(f'Image {i}')
                
                task.write(voltages[i])
                time.sleep(0.1)
                raw_array = parent.camera_widget.camera.get_image().copy().squeeze()
                #plt.imshow(raw_array*mask, 'gray')
                images.append(raw_array*mask)
            #plt.show()
                

            parent.camera.stop_acquisition()
            parent.camera.free_memory()

            task.write(0)
            task.stop()
        
        images_filtrees = np.array(list(map(lambda x:gaussian_filter(x, sigma_gaussian_filter), images))).squeeze()

    except Exception as e:
        print(f'Exception Phase - {e}')

    parent.camera_thread.start()
    return hariharan_algorithm(*images_filtrees), images_filtrees

def check_alpha(images):
    num = images[5-1]-images[1-1]
    denum = 2*(images[4-1]-images[2-1])
    alpha = np.rad2deg(np.arccos(num/denum))
    average_alpha = np.nanmean(alpha)
    std_alpha = np.std(alpha)
    
    """
    import matplotlib.pyplot as plt
    plt.figure()
    plt.hist(alpha.ravel(),100)
    plt.axvline(average_alpha, color='red')
    plt.axvline(average_alpha-std_alpha, color='k')
    plt.axvline(average_alpha+std_alpha, color='k')
    plt.show()
    """

    print(f"alpha = {average_alpha} °")
    return average_alpha, std_alpha