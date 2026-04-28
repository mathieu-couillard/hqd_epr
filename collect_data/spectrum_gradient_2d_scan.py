# General imports

from config.inst_addresses import InstrumentAddresses as instAddr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils import generate_path
from pathlib import Path
import time
from drivers import AMI430Vector, AgilentN5230C, YokogawaGS200

########
# Names
########
project = "dpph_impedance_matching"
exp_name = "gradient_spectrum_2d"
base_path = Path("D://Mathieu/Data/")

########
# Magnetic field
########
b_field0 = 164.5
ramp_rate_ami = 0.05
gradient_offset_coef = 4.6*1.5  # uT/mA

########
# Magnet Field Gradient Source Parameters
########
curr_start = 108e-3
curr_stop = 111e-3
curr_step = 0.1e-3

########
# VNA Parameters
########
cfreq = 4.5808095  # GHz
span = 0.05  # GHz
data_points = 3001#32001
elec_delay = 61.104365e-9  # sec
phase_offset = 0

exp_power = -10  # dbm
n_avg = 1
avg_state = False
bandwidth = 1e3
correction_factor = 4.47e-3


curr_list = np.arange(curr_start, curr_stop + 0.5 * curr_step, curr_step)
# print(np.flip(curr_list))


def source_ramp(source, target_level, rate=1e-3, step_size=1e-5):
    # units of amp and seconds
    level = float(source.level())
    while level != target_level:
        if target_level > level:
            direction = 1
        else:
            direction = -1
        level = float(source.level())
        level += direction * step_size
        source.level(level)
        if step_size / rate > 0.004:
            time.sleep(step_size / rate)
        if abs(target_level - level) < step_size:
            source.level(target_level)
            break


def config_vna(
    vna,
    exp_power,
    bandwidth,
    center_freq,
    span,
    elec_delay,
    phase_offset,
    data_points,
    n_avg=1,
    avg_state=False,
):
    vna.totalPower_dBm = exp_power
    vna.BW = bandwidth
    vna.centerFreqInGHz = center_freq
    vna.spanFreqInGHz = span
    vna.electricalDelay = elec_delay
    vna.phaseOffset = phase_offset
    vna.numOfPoints = data_points
    vna.aveIsOn = avg_state
    vna.numOfAve = n_avg


def config_mag_gradient_source(mag_grad_source):
    mag_grad_source.function(function="current")
    mag_grad_source.source_range(source_range="0.2")
    if not mag_grad_source.output():
        source_ramp(mag_grad_source, 0)
        mag_grad_source.output(True)
    mag_grad_source.operation_complete()


def get_data(vna):
    # vna.trigger()
    vna.waitFullSweep()
    freq = vna.getFreq()
    log_mag, phase = vna.getTrace()
    return freq, log_mag, phase


def save_spectrum(freq, log_mag, phase, current, path):
    filename = f"{round(current * 1000, 3)}mA".replace(".", "p")
    df = pd.DataFrame({"freq": freq, "log mag": log_mag, "phase": phase})
    df.to_csv((path / (filename + ".csv")), index=False)


def save_spectrogram(data2D_mag, data2D_phase, currents, freqs, path):
    Data2D_mag = pd.DataFrame(data2D_mag, columns=currents, index=freqs)
    Data2D_mag.to_csv(path / "data2d_log_mag.csv")
    Data2D_phase = pd.DataFrame(data2D_phase, columns=currents, index=freqs)
    Data2D_phase.to_csv(path / "data2d_phase.csv")


# def create_directory_structure(project, exp_name, glob):
#     path, data_path, fig_path = generate_path(
#         project=project, exp_name=exp_name, basepath=glob
#     )
#     return path, data_path, fig_path


def plot_spectrum(freq, log_mag, phase, curr, fig_path):
    filename = f"{round(curr * 1000, 3)}mA".replace(".", "p")
    fig, ax1 = plt.subplots()

    color = "tab:red"
    ax1.set_xlabel("Frequancy [GHz]")
    ax1.set_ylabel("log mag [dB]", color=color)
    ax1.plot(freq, log_mag, color=color)
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis

    color = "tab:blue"
    ax2.set_ylabel(
        "Phase [rad]", color=color
    )  # we already handled the x-label with ax1
    ax2.plot(freq, phase, color=color)
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig((fig_path / filename))
    # plt.show()
    plt.clf()
    plt.close(fig)


if __name__ == "__main__":
    mag_grad_source = YokogawaGS200(visa_backend="@py", address=instAddr.gs200_2)
    config_mag_gradient_source(mag_grad_source)
    vna = AgilentN5230C(address=instAddr.N5230C)
    config_vna(
        vna,
        exp_power,
        bandwidth,
        cfreq,
        span,
        elec_delay,
        phase_offset,
        data_points,
        n_avg,
        avg_state,
    )
    mags = AMI430Vector([instAddr.mag_x, instAddr.mag_y, instAddr.mag_z])
    path, data_path, fig_path = generate_path(project, exp_name, base_path)
    print(path)
    vna.operation_complete()
    freq = vna.getFreq()
    data2D_mag = np.zeros((len(freq), len(curr_list)))
    data2D_phase = np.zeros((len(freq), len(curr_list)))

    for i, curr in enumerate(curr_list):
        b_field = b_field0 + gradient_offset_coef * curr
        mags.ramp_spherical(field=b_field, ramp_rate=ramp_rate_ami)
        source_ramp(mag_grad_source, curr, rate=3e-2, step_size=1e-4)
        mag_grad_source.operation_complete()
        time.sleep(2)
        freq, log_mag, phase = get_data(vna)
        save_spectrum(freq, log_mag, phase, curr, data_path)
        plot_spectrum(freq, log_mag, phase, curr, fig_path)

        data2D_mag[:, i] = log_mag
        data2D_phase[:, i] = phase
    save_spectrogram(data2D_mag, data2D_phase, curr_list, freq, path)
    source_ramp(mag_grad_source, 0, rate=0.001, step_size=1e-3)
