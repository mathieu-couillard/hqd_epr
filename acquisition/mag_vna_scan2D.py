# General imports

from config.inst_addresses import InstrumentAddresses as instAddr
from utils import generate_path
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime
import pandas as pd
import shutil
from pathlib import Path
from tqdm import tqdm

# instrument imports

from config.experiment_config import EXPERIMENT_BASE_PATH
from drivers import AgilentN5230C
from drivers import AMI430Vector

# from drivers import gs200


current = 0.0

# VNA parameter
cfreq = 4.5809095  # GHz
span = 0.1  # GHz
data_points = 321
elec_delay = 59.183716e-9  # sec
phase_offset = 200


exp_power = -10  # dbm
n_avg = 1
avg_state = "off"  # off
bandwidth = 1e3  # Hz

# Power supply parameter
# sw_voltage = 3.3 # volt

# magnet parameter
Bmag_center = 164.6
Bmag_span = 2
Bmag_step = 0.02

Bmag_start = Bmag_center - Bmag_span / 2
Bmag_end = Bmag_center + Bmag_span / 2
Bmag_list = np.arange(Bmag_start, Bmag_end + 0.5 * Bmag_step, Bmag_step)
Bmag_list = np.insert(Bmag_list, 0, (Bmag_start - 5))
ramp_rate = 0.05
cooldown_time = 5
print(Bmag_list)

# magnetic field direction
theta = 0
phi = 0


def plot_data(freqs, amps, phases, title, fig_folder):
    figs, ax2 = plt.subplots()
    ax2.plot(freqs, amps, label="S11-Amplitude")
    ax2.set_xlabel("Frequency [Hz]")
    ax2.set_ylabel("Amplitude [dBm]")
    ax3 = ax2.twinx()
    ax3.plot(freqs, phases, color="red", label="S11-Phase")
    ax3.set_ylabel("Phase [degree]")
    ax2.set_title(title)
    plt.savefig(r"{}/{}.png".format(fig_folder, title))
    plt.clf()
    plt.close(figs)


def create_directory_structure(project, exp_name, experiment_base_name):
    path, data_path, fig_path = generate_path(
        project=project, exp_name=exp_name, basepath=experiment_base_name
    )
    # config_path = qm_config.__file__
    # shutil.copy(__file__, f"{str(path / Path(__file__).name)}")
    # shutil.copy(config_path, f"{str(path / Path(config_path).name)}")
    # shutil.copy(
    #     EXPPERIMENT_CONFIG_PATH, f"{str(path / Path(EXPPERIMENT_CONFIG_PATH).name)}"
    # )
    return path, data_path, fig_path


# def initialize_experiment(project, exp_name):
#     exp = experiment(project=project, exp_name=exp_name)
#     exp_path = exp.get_path()
#     data_folder = exp.create_folder(base_path=exp_path, _folder = 'Data')
#     fig_folder = exp.create_folder(base_path=exp_path, _folder = 'fig')
#     shutil.copy(__file__,r'{}/mag_vna_scan2D.py'.format(exp_path))
#     return  exp_path, data_folder, fig_folder


def main(current: float):
    current = round(current * 1e3, 3)
    current_str = str(current).split(".")
    if len(current_str) < 2:
        current_str.append("0")
    project_name = "Impedance_Matching_DPPH"
    print(current_str)
    experiment_name = "rutile_cavity_freq_and_Bfield_DPPH_gradient{}p{}mA".format(
        current_str[0], current_str[1]
    )

    path, data_path, fig_path = create_directory_structure(
        project=project_name,
        exp_name=experiment_name,
        experiment_base_name=EXPERIMENT_BASE_PATH,
    )

    vna = AgilentN5230C(instAddr.N5230C)
    magnet = AMI430Vector([instAddr.mag_x, instAddr.mag_y, instAddr.mag_z])

    vna.totalPower_dBm = exp_power
    vna.BW = bandwidth
    vna.aveIsOn = False
    vna.centerFreqInGHz = cfreq
    vna.spanFreqInGHz = span
    vna.electricalDelay = elec_delay
    vna.phaseOffset = phase_offset
    vna.numOfPoints = data_points
    vna.numOfAve = n_avg

    # data structure set-up and running plot
    frequencies = vna.getFreq()
    data2D_mag = np.zeros((len(frequencies), len(Bmag_list)))
    data2D_phase = np.zeros((len(frequencies), len(Bmag_list)))
    fig, ax = plt.subplots()
    image = ax.imshow(
        data2D_mag,
        aspect="auto",
        extent=[(Bmag_start - Bmag_step), Bmag_end, frequencies[0], frequencies[-1]],
        origin="lower",
    )
    ax.set_xlabel("Magnetic Field [mT]")
    ax.set_ylabel("Frequency [Hz]")
    ax.set_title(f"Magnetic Field Sweep with field gradient: {current} mA")
    plt.ion()

    # Magnet_preparation and experiment start
    magnet.ramp_spherical(
        field=Bmag_start - 1, thetaDeg=theta, phiDeg=phi, ramp_rate=0.5
    )
    time.sleep(cooldown_time)
    ami_Blist = []

    # Experiment Triggers
    for i, mag in enumerate(tqdm(Bmag_list)):
        magnet.ramp_spherical(
            field=(mag + 4.6e-3 * current),
            thetaDeg=theta,
            phiDeg=phi,
            ramp_rate=ramp_rate,
        )
        magxyz = list(magnet.magnetic_field())
        ami_Blist.append([mag, magxyz[0], magxyz[1], magxyz[2]])
        time.sleep(cooldown_time)
        # source.output(True)
        # source.operation_complete()
        vna.waitFullSweep()
        if i == 0:
            vna.waitFullSweep()

        power_dB, phase = vna.getTrace()
        print(len(frequencies))
        print(len(power_dB))
        print(len(phase))
        data = pd.DataFrame(
            {"frequency": frequencies, "power dB": power_dB, "phase": phase}
        )
        data.to_csv(
            f"{data_path}/{cfreq}GHz_{exp_power}dBm_{mag:07.3f}mT".replace(".", "p")
            + ".csv",
            index=False,
        )
        data2D_mag[:, i] = data["power dB"]
        data2D_phase[:, i] = data["phase"]

        plot_data(
            data["frequency"],
            data["power dB"],
            data["phase"],
            f"S11_{cfreq}GHz_{exp_power}dBm_{mag:07.3f}mT".replace(".", "p"),
            fig_path,
        )
        image.set_array(data2D_mag)
        image.autoscale()
        plt.pause(2)

    # magnet.ramp_zero()
    plt.ioff()
    # magnet.ramp_zero()
    Data2D_mag = pd.DataFrame(data2D_mag, columns=Bmag_list, index=frequencies)
    Data2D_mag.to_csv(
        r"{}/Data2D_mag_{}GHz_{}dBm".format(path, cfreq, exp_power).replace(".", "p")
        + ".csv"
    )
    Data2D_phase = pd.DataFrame(data2D_phase, columns=Bmag_list, index=frequencies)
    Data2D_phase.to_csv(
        r"{}/Data2D_phase_{}GHz_{}dBm".format(path, cfreq, exp_power).replace(".", "p")
        + ".csv"
    )
    plt.savefig(r"{}/VNA_2D_scan_with_magnet.png".format(path))
    plt.close()
    # plt.show()
    with open(r"{}/Bfield_list.txt".format(path), "w") as f:
        f.write(str(ami_Blist))


if __name__ == "__main__":
    main(current=current)
