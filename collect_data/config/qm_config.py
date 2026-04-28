from pathlib import Path

import numpy as np
from scipy.signal.windows import gaussian

from .experiment_config import QMConfig, MWConfig

from .inst_addresses import InstrumentAddresses

HOST_IP = InstrumentAddresses.qm

# simulation
# Simulation time # length should be in the unit of 4ns


##################
# IQ mixer balance
##################
def IQ_imbalance(g, phi):
    """
    Creates the correction matrix for the mixer imbalance caused by the gain
    and phase imbalances, more information can be seen at:
    https://docs.qualang.io/libs/examples/mixer-calibration/#non-ideal-mixer

    :param g: relative gain imbalance between the I & Q ports (unit-less). Set to 0 for no gain imbalance.
    :param phi: relative phase imbalance between the I & Q ports (radians). Set to 0 for no phase imbalance.
    """
    c = np.cos(phi)
    s = np.sin(phi)
    N = 1 / ((1 - g**2) * (2 * c**2 - 1))
    return [float(N * x) for x in [(1 - g) * c, (1 + g) * s, (1 - g) * s, (1 + g) * c]]

# Mixer correction
MIXER_GAIN = 0.01194123619794846
MIXER_PHASE = -0.06355408787727335
OUTPUT_OFFSET_I = -0.013625781509173596
OUTPUT_OFFSET_Q = -0.01938618634801776

INPUT_OFFOUT_I = 0.0 #6-0.01455#-0.21271891043526786
INPUT_OFFOUT_Q = 0.0 #6-0.01455#-0.2172443777901786

# MIXER_GAIN = 0
# MIXER_PHASE = 0.0
# OUTPUT_OFFSET_I = 0.0
# OUTPUT_OFFSET_Q = 0.0

INPUT_OFFOUT_I = 0 #6-0.01455#-0.21271891043526786
INPUT_OFFOUT_Q = 0 #6-0.01455#-0.2172443777901786

# details for switch delays
ANALOG_OUTPUT_DELAY = 200  # QM has 136 ns delay in the analogs line with digital

CRYO_SWITCH_BUFFER = 0
CRYO_SWITCH_DELAY = 0  # EV1HMC547ALP3
CRYO_SWITCH_TIME_OF_FLIGHT = 100

RT_SWITCH_BUFFER = 500
RT_SWITCH_DELAY = 750 # EVAL-ADRF5019

############################
# Experiment configuration #
############################

SPIN_IF = QMConfig.spin_if_freq
SPIN_LO = MWConfig.spin_lo_freq


SPA_TIGGER_LENGTH = int(4e3)

SQUARE_PULSE_LENGTH = QMConfig.square_pulse_length
GAUSSIAN_PULSE_LENGTH = QMConfig.gaussian_pulse_length
INIT_PULSE_LENGTH = QMConfig.init_pulse_length

half_gauss_amp = QMConfig.half_gauss_amp
half_gauss_sigma = QMConfig.half_gauss_sigma

READOUT_LENGTH = QMConfig.readout_length
SATURATION_PULSE_LENGTH = QMConfig.saturation_pulse_length
PI_PULSE_LENGTH = QMConfig.pi_pulse_length
PI_HALF_PULSE_LENGTH = QMConfig.pi_half_pulse_length


TIME_OF_FLIGHT = 724#584 # pulse
# TIME_OF_FLIGHT = 24#524 # echo
SMEARING = 0
# {'out1': 0.21271891043526786, 'out2': 0.2172443777901786}


# calculate the peak voltage
saturation_wf_amp = QMConfig.spin_if_pi_amp
pi_amp = QMConfig.spin_if_pi_amp
gaussian_amp = QMConfig.spin_if_pi_amp
pi_half_amp = QMConfig.spin_if_pi_half_amp

#################
# Gaussian waveforms
#################
gaussian_I_wf = gaussian_amp * gaussian(
    GAUSSIAN_PULSE_LENGTH, GAUSSIAN_PULSE_LENGTH / 5
)


def half_gaussian(amplitude, sigma, total_length=None, direction='increasing', step_size=4):
    """
    Generates either an increasing or decreasing half of a Gaussian curve.

    The curve's x-values always start at 0. The total length of the curve can
    be specified. If not provided, it defaults to `4 * sigma`. The peak of the 
    curve is defined by the direction:
    - 'increasing': The peak is at the end of the curve (at x = total_length).
    - 'decreasing': The peak is at the start of the curve (at x = 0).

    Args:
        amplitude (float): The maximum height of the Gaussian.
        sigma (float): The standard deviation of the Gaussian. A smaller
                       sigma results in a steeper slope.
        total_length (float, optional): The total length of the x-axis for the curve.
                                        If None, it defaults to `4 * sigma`.
        direction (str, optional): Specifies the curve's direction. Use
                                  'increasing' or 'decreasing'. Defaults
                                  to 'increasing'.
        step_size (float, optional): The interval between x-values. Defaults to 0.1.

    Returns:
        tuple: A tuple containing two numpy arrays:
               - The array of x-values for the half Gaussian, starting at 0.
               - The array of y-values representing the half Gaussian.
    """
    if direction not in ['increasing', 'decreasing']:
        print("Error: `direction` must be either 'increasing' or 'decreasing'.")
        return np.array([]), np.array([])

    # If total_length is not provided, set it to the default value.
    if total_length is None:
        total_length = 4 * sigma

    x = np.arange(0, total_length, step_size)
    
    if direction == 'increasing':
        # For an increasing half, the peak is at the end of the specified length.
        # The center of the full Gaussian is `total_length`.
        center = total_length
        y = amplitude * np.exp(-0.5 * ((x - center) / sigma)**2)
    else:  # direction == 'decreasing'
        # For a decreasing half, the peak is at the start (x=0).
        # The center of the full Gaussian is 0.
        center = 0
        y = amplitude * np.exp(-0.5 * ((x - center) / sigma)**2)

    return  y

###################
# Config Dictionary
###################
config = {
    # "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",  # why was this removed???
            "analog_outputs": {
                1: {
                    "offset": OUTPUT_OFFSET_I,
                    "delay": ANALOG_OUTPUT_DELAY,
                },
                2: {
                    "offset": OUTPUT_OFFSET_Q,
                    "delay": ANALOG_OUTPUT_DELAY,
                },
            },
            "digital_outputs": {
                1: {},  # laser initialization
                2: {},  # HEMT cryo switch
                3: {},  # SPA
                6: {},  # RT MW switch
                5: {},  # digitizer trigger
            },
            "analog_inputs": {
                1: {
                    "offset": INPUT_OFFOUT_I,
                    "gain_db": 0,
                },  # signal from the down converted signal
                2: {
                    "offset": INPUT_OFFOUT_Q,
                    "gain_db": 0,
                },  # , 'gain_db': 0 signal from the up converted signal
            },
        }
    },
    "elements": {
        "spin": {
            "mixInputs": {
                "I": ("con1", 1),
                "Q": ("con1", 2),
                "lo_frequency": SPIN_LO,
                "mixer": "mixer_spin1",
            },
            "intermediate_frequency": SPIN_IF,
            "operations": {
                "saturation": "saturation_pulse",
                "pi": "pi_pulse",
                "pi_half": "pi_half_pulse",
                "gaussian_180": "gaussian_pulse",
                "half_gaussian_asend": "half_gaussian_increase",
                "half_gaussian_desend": "half_gaussian_decrease",
                "x90": "x90-pulse",
                "x180": "x180-pulse",
                "-x90": "-x90-pulse",
                "y90": "y90-pulse",
                "y180": "y180-pulse",
                "-y90": "-y90-pulse",
            },
            "digitalInputs": {
                "RT_SW": {  # EVAL-ADRF5019
                    "port": ("con1", 6),
                    "delay": RT_SWITCH_DELAY,
                    "buffer": RT_SWITCH_BUFFER,
                }
            },
        },
        "laser": {
            "digitalInputs": {
                "marker": {"port": ("con1", 1), "delay": 0, "buffer": 0.0},
            },
            "operations": {
                "initialize": "initialization_pulse",
                "readout_odmr": "readout_odmr_pulse",
            },
        },
        "digitizer": {
            "mixInputs": {
                "I": ("con1", 1),
                "Q": ("con1", 2),
                "lo_frequency": SPIN_LO,
                "mixer": "mixer_spin2",
            },
            "intermediate_frequency": SPIN_IF,
            "operations": {"readout": "readout_pulse"},
            "digitalInputs": {
                "marker": {
                    "port": ("con1", 5),
                    "delay": TIME_OF_FLIGHT,  # time of flight of the signal throught device
                    "buffer": 0,  # 20ns
                }
            },
            "time_of_flight": TIME_OF_FLIGHT,  # at the end of this time, digitizer starts demodulation and integration. should be such that record the data before actual echo.
            "smearing": SMEARING,  # this is for the raw ADAC data, extra data record +- the readout pulse starting at the end of time of flight.
            "outputs": {"out1": ("con1", 1), "out2": ("con1", 2)},
        },
        # For HEMT. Placed here to open switch independently of readout
        "CryoSw": {
            "digitalInputs": {
                "marker": {
                    "port": ("con1", 2),
                    "delay": CRYO_SWITCH_DELAY,
                    "buffer": CRYO_SWITCH_BUFFER,
                },
            },
            "operations": {
                "cryosw": "cryosw_on",
            },
        },
        # For reset
        # This triggers the SPA. Useful for automating the IQ calibration
        "SPA": {
            "digitalInputs": {
                "marker": {"port": ("con1", 3), "delay": 0, "buffer": 0.0},
            },
            "operations": {"spa": "spa_on"},
        },
    },
    "pulses": {
        "sq": {
            "operation": "control",
            "length": SQUARE_PULSE_LENGTH,
            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "saturation_pulse": {
            "operation": "control",
            "length": SATURATION_PULSE_LENGTH,
            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "pi_half_pulse": {
            "operation": "control",
            "length": PI_HALF_PULSE_LENGTH,
            "waveforms": {"I": "pi_half_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "pi_pulse": {
            "operation": "control",
            "length": PI_PULSE_LENGTH,
            "waveforms": {"I": "pi_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "gaussian_pulse": {
            "operation": "control",
            "length": GAUSSIAN_PULSE_LENGTH,
            "waveforms": {"I": "gaussian_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
         },           
         "half_gaussian_increase": {
            "operation": "control",
            "length": half_gauss_sigma,
            "waveforms": {"I": "gaussian_half_asend", "Q": "zero_wf"},
            "digital_marker": "ON",
         },
        
        "half_gaussian_decrease": {
            "operation": "control",
            "length": half_gauss_sigma,
            "waveforms": {"I": "gaussian_half_desend", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "x90-pulse": {
            "operation": "control",
            "length": PI_HALF_PULSE_LENGTH,
            "waveforms": {"I": "pi_half_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "x180-pulse": {
            "operation": "control",
            "length": PI_PULSE_LENGTH,
            "waveforms": {"I": "pi_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "-x90-pulse": {
            "operation": "control",
            "length": PI_HALF_PULSE_LENGTH,
            "waveforms": {"I": "minus_pi_half_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
        },
        "y90-pulse": {
            "operation": "control",
            "length": PI_HALF_PULSE_LENGTH,
            "waveforms": {"I": "zero_wf", "Q": "pi_half_wf"},
            "digital_marker": "ON",
        },
        "y180-pulse": {
            "operation": "control",
            "length": PI_PULSE_LENGTH,
            "waveforms": {"I": "zero_wf", "Q": "pi_wf"},
            "digital_marker": "ON",
        },
        "-y90-pulse": {
            "operation": "control",
            "length": PI_HALF_PULSE_LENGTH,
            "waveforms": {"I": "zero_wf", "Q": "minus_pi_half_wf"},
            "digital_marker": "ON",
        },
        "readout_pulse": {
            "operation": "measurement",
            "length": READOUT_LENGTH,
            "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_weights",
                "sin": "sin_weights",
                "minus_sin": "minus_sin_weights",
            },
        },
        "initialization_pulse": {
            "operation": "control",
            "length": INIT_PULSE_LENGTH,
            "digital_marker": "LASER_ON",
        },
        "readout_odmr_pulse": {
            "operation": "control",
            "length": READOUT_LENGTH,
            "digital_marker": "LASER_ON",
        },
        "cryosw_on": {
            "operation": "control",
            "length": READOUT_LENGTH+800,
            "digital_marker": "ON",
        },
        "spa_on": {
            "operation": "control",
            "length": SPA_TIGGER_LENGTH,
            "digital_marker": "spa_trigger",
        },
    },
    "waveforms": {
        "const_wf": {"type": "constant", "sample": saturation_wf_amp},
        "gaussian_wf": {"type": "arbitrary", "samples": gaussian_I_wf},
        "gaussian_half_asend": {"type": "arbitrary", "samples": half_gaussian(half_gauss_amp, half_gauss_sigma, direction="increasing")},
        "gaussian_half_desend": {"type": "arbitrary", "samples": half_gaussian(half_gauss_amp, half_gauss_sigma, direction="decreasing")},
        "pi_wf": {"type": "constant", "sample": pi_amp},
        "pi_half_wf": {"type": "constant", "sample": pi_half_amp},
        "minus_pi_half_wf": {"type": "constant", "sample": -pi_half_amp},
        "zero_wf": {"type": "constant", "sample": 0},
    },
    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]},
        "OFF": {"samples": [(0, 0)]},
        "spa_trigger": {"samples": [(1, 0)]},
        "LASER_ON": {"samples": [(1, 0)]},
    },
    "integration_weights": {
        "cos_weights": {
            "cosine": [(1.0, READOUT_LENGTH)],
            "sine": [(0.0, READOUT_LENGTH)],
        },
        "sin_weights": {
            "cosine": [(0.0, READOUT_LENGTH)],
            "sine": [(1.0, READOUT_LENGTH)],
        },
        "minus_sin_weights": {
            "cosine": [(0.0, READOUT_LENGTH)],
            "sine": [(-1.0, READOUT_LENGTH)],
        },
    },
    "mixers": {
        "mixer_spin1": [
            {
                "intermediate_frequency": SPIN_IF,
                "lo_frequency": SPIN_LO,
                "correction": [1.0, 0.0, 0.0, 1.0],#IQ_imbalance(MIXER_GAIN, MIXER_PHASE),
            }
        ],
        "mixer_spin2": [
            {
                "intermediate_frequency": SPIN_IF,
                "lo_frequency": SPIN_LO,
                "correction": [1.0, 0.0, 0.0, 1.0],
            }
        ],
    },
}
