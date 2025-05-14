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
n_avg = 100


#############
# PARAMETERS #
##############
class QMConfig:
    padding = 1 * us
    ####################
    # Pulse parameters #
    ####################
    # NV
    spin_if_freq = 100 * MHz
    spin_if_amp = 300e-3 # max 500 mV

    square_pulse_length = 400  # units of ns, divisible by 4
    gaussian_pulse_length = 400  # units of ns, divisible by 4
    init_pulse_length = 400  # units of ns, divisible by 4

    readout_length = 500  # units of 1ns, divisible by 4
    saturation_pulse_length = 500  # units of 1ns, divisible by 4
    pi_pulse_length = 200  # units of 1ns, divisible by 4
    pi_half_pulse_length = pi_pulse_length  # units of 1ns, divisible by 4


    safe_delay = u.to_clock_cycles(2000)  # Delay to safely avoid pulses during readout window
    # Laser
    initialization_len = 100 * us
    power_stabilization_len = 500 * us


class MagConfig:
    field = 164.558 # mT
    ramp_rate = 0.5  # T/s
    theta = 0  # degrees
    phi = 0  # degrees


class MWConfig:
    spin_freq = 4.5807043 * GHz
    # spin_freq = 4.581304 * GHz
    spin_lo_freq = spin_freq - QMConfig.spin_if_freq
    spin_lo_power = 10


class FreeInductionDecay:
    spin_lo_power = MWConfig.spin_lo_power
    spin_lo_freq = MWConfig.spin_lo_freq
    glob = Path("data/FID")


class PiPulseCalibration:
    spin_lo_power = MWConfig.spin_lo_power
    spin_lo_freq = MWConfig.spin_lo_power
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/pi_pulse_calibration")


class HahnEcho:
    spin_lo_power = MWConfig.spin_lo_power
    spin_lo_freq = MWConfig.spin_lo_power
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/Hahn_echo")


class DynamicalDecoupling:
    spin_lo_power = MWConfig.spin_lo_power
    spin_lo_freq = MWConfig.spin_lo_power
    n_pulses = 3
    tau_i = 20 * ns
    tau_f = 1 * us
    tau_step = 20 * ns
    glob = Path("data/dynamical_decoupling")

