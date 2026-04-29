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
EXPERIMENT_BASE_PATH = Path("/Mathieu/Data")
PROJECT_NAME = Path("impedance_matching_dpph")
# Number of averaged runs
n_avg = int(1e3)

#############
# PARAMETERS #
##############
class QMConfig:
    padding = 1 * us
    ####################
    # Pulse parameters #
    ####################
    # NV
    spin_if_freq = 250 * MHz
    spin_if_pi_amp = 500e-3 #0.075e-3 # max 500 mV
    spin_if_pi_half_amp = spin_if_pi_amp/2 #

    square_pulse_length = 40  # units of ns, divisible by 4
    gaussian_pulse_length = 900  # units of ns, divisible by 4
    init_pulse_length = 40  # units of ns, divisible by 4

    saturation_pulse_length = 500  # units of 1ns, divisible by 4
    pi_pulse_length = 132//4*4 #800//4*4 #(10_000)//4*4  # units of 1ns, divisible by 4 # 348ns for 200mA, B=135.4
    pi_half_pulse_length = pi_pulse_length  # units of 1ns, divisible by 4
    
    half_gauss_amp = 500e-3
    half_gauss_sigma = 40*2

    safe_delay = u.to_clock_cycles(1500)  # Delay to safely avoid pulses during readout window
    # Laser
    initialization_len = 100 * us
    power_stabilization_len = 500 * us

    readout_length =  1_000 # units of 1ns, divisible by 4
    # readout_length =  8000 # units of 1ns, divisible by 4


class MagConfig:
    _field = 164.35-10 # mT
    ramp_rate = 1.5  # mT/s
    theta = 0  # degrees
    phi = 0  # degrees
    gradient_offset_coef = 4.6  # mT/A
    gradient_current = 0e-3 # A
    set_field = _field + gradient_offset_coef*gradient_current


class MWConfig:
    spin_freq = 4.5809095 * GHz-100*MHz #(4.58074+0.003) * GHz #4.58128 * GHz 
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

