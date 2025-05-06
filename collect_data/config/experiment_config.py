from pathlib import Path

from qualang_tools.units import unit

u = unit()

s = u.s
ms = u.ms
us = u.us
ns = u.ns

Hz = u.Hz
kHz = u.kHz
MHz = u.MHz
GHz = u.GHz

#############
# Data path #
#############
EXPERIMENT_BASE_PATH = Path("/mathieu/data")
PROJECT_NAME = Path("impedance_matching_dpph")
# Number of averaged runs
n_avg = 2


#############
# PARAMETERS #
##############
class QMConfig:
    padding = 1 * us
    ####################
    # Pulse parameters #
    ####################
    # NV
    spin_if = 100e6
    spin_lo = 4.4798248e9

    spa_tigger_length = int(4e3)

    square_pulse_length = 400  # units of ns, divisible by 4
    gaussian_pulse_length = 400  # units of ns, divisible by 4
    init_pulse_length = 400  # units of ns, divisible by 4

    readout_length = 8000  # units of 1ns, divisible by 4
    saturation_pulse_length = 2000  # units of 1ns, divisible by 4
    pi_pulse_length = 500  # units of 1ns, divisible by 4
    pi_half_pulse_length = pi_pulse_length  # units of 1ns, divisible by 4

    time_of_flight = 180 * ns  # Minimum 24, Swabian laser has 270ns delay
    smearing = 0
    # safe_delay = u.to_clock_cycles(2 * us)  # Delay to safely avoid pulses during readout window

    power = 0
    saturation_power = power  # max 3dBm
    pi_power = power  # max 3dBm
    gaussian_power = power  # max 3dBm

    # Laser
    initialization_len = 100 * us
    power_stabilization_len = 500 * us


class MagConfig:
    field = 165  # mT
    ramp_rate = 0.5  # T/s
    theta = 0  # degrees
    phi = 0  # degrees


class MWConfig:
    mw_power = 10
    mw_freq = 4500 * MHz  # For single frequency experiments # 1544
    step = 0.1 * MHz
    freq_if = 100 * MHz
    if_offset = 35 * MHz


class FreeInductionDecay:
    mw_power = 10
    mw_freq = MWConfig.mw_freq
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/FID")


class PiPulseCalibration:
    mw_power = 10
    mw_freq = MWConfig.mw_freq
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/pi_pulse_calibration")


class HahnEcho:
    mw_power = 10
    mw_freq = MWConfig.mw_freq
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/Hahn_echo")


class DynamicalDecoupling:
    mw_power = 10
    mw_freq = MWConfig.mw_freq
    n_pulses = 3
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/dynamical_decoupling")
