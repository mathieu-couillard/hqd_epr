import numpy as np
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
EXPERIMENT_BASE_PATH = Path('/mathieu/data')
PROJECT_NAME = Path('impedance_matching_dpph')

#############
# PARAMETERS #
##############
class QMConfig:
    # Number of averaged runs
    n_avg = 20
    padding = 1 * us
    ####################
    # Pulse parameters #
    ####################
    # NV
    const_amp = 0.2  # in V
    const_len = 100 * ns  # in ns

    saturation_amp = 0.2  # in V. 0.2 starts to saturate the SRS 445A amplifier.
    saturation_len = 0.5 * ms  # Needs to be several T1

    pi_half_len = 64 * ns  # in units of ns #3.8MHz Rabi oscillations
    pi_half_amp = const_amp

    pi_len = 2 * pi_half_len  # in units of ns
    pi_amp = const_amp  # in units of volts

    readout_len = 5 * us

    time_of_flight = 236 * ns  # Minimum 24, Swabian laser has 270ns delay
    # safe_delay = u.to_clock_cycles(2 * us)  # Delay to safely avoid pulses during readout window

    # Laser
    initialization_len = 100 * us
    power_stabilization_len = 500 * us


class MagConfig:
    field = 165  # mT
    ramp_rate = 0.5 # T/s
    theta = 0  # degrees
    phi = 0  # degrees


class MWConfig:
    mw_power = 10
    mw_freq = 4500 * MHz # For single frequency experiments # 1544
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
