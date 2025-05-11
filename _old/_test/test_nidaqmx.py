import nidaqmx
import numpy as np
import time
import sys

local_system = nidaqmx.system.System.local()
driver_version = local_system.driver_version
device_number = len(local_system.devices)
volt_min = 0
volt_max = 5

print(
    "DAQmx {0}.{1}.{2}".format(
        driver_version.major_version,
        driver_version.minor_version,
        driver_version.update_version,
    )
)

if device_number > 0:
    for i, device in enumerate(local_system.devices):
        print(f'({i+1}) Device Name: {device.name}, Product Type: {device.product_type}')
else:
    print('No NI Device connected')
    sys.exit(-1)

def set_daq_output(voltage) -> bool:
    with nidaqmx.Task() as task:
        # Add an analog output channel
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=volt_min, max_val=volt_max)
        task.start()
        if volt_min <= voltage <= volt_max:
            task.write(voltage)
            task.stop()
            return True
        else:
            return False

def daq_ramp(val_min, val_max, duration=1, step_nb=100):
    # Paramètres de la rampe de tension
    start_voltage = val_min  # Tension de départ en volts
    end_voltage = val_max # Tension finale en volts
    num_steps = step_nb  # Nombre de pas dans la rampe
    duration = duration  # Durée totale de la rampe en secondes

    # Calcul des paramètres de la rampe
    step_duration = duration / num_steps
    ramp = np.linspace(start_voltage, end_voltage, num_steps)

    # Créer une tâche pour générer la rampe de tension
    with nidaqmx.Task() as task:
        # Ajouter un canal de sortie analogique
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=start_voltage, max_val=end_voltage)

        # Démarrer la tâche
        task.start()

        # Générer la rampe de tension en écrivant chaque valeur successivement
        for voltage in ramp:
            task.write(voltage)
            time.sleep(step_duration)

        # Arrêter la tâche
        task.stop()

# daq_ramp(0, 5, 3)

'''
# Test 2
if set_daq_output(3):
    print('OK')
else:
    print('NOT OK')
'''

while(True):
    tension = float(input())
    set_daq_output(tension)