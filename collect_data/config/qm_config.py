import numpy as np
from .inst_addresses import InstrumentAddresses
from scipy.signal.windows import gaussian
from pathlib import Path

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
MIXER_GAIN = -0.06202944228053098
MIXER_PHASE = 0.02538897782564157
DC_OFFSET_I = -0.021664633363113018
DC_OFFSET_Q = -0.020055943976947946

# details for switch delays
ANALOG_OUTPUT_DELAY = 200  # QM has 136 ns delay in the analogs line with digital

CRYO_SWITCH_DELAY = 10  # EV1HMC547ALP3
CRYO_SWITCH_BUFFER = 5

RT_SWITCH_DELAY = 160  # EVAL-ADRF5019
RT_SWITCH_BUFFER = 10


# experiment variable
SPIN_IF = 100e6
SPIN_LO = 4.4798248e9


SPA_TIGGER_LENGTH = int(4e3)

SQUARE_PULSE_LENGTH = 400  # units of ns, divisible by 4
GAUSSIAN_PULSE_LENGTH = 400  # units of ns, divisible by 4
INIT_PULSE_LENGTH = 400  # units of ns, divisible by 4

READOUT_LENGTH = 8000  # units of 1ns, divisible by 4
SATURATION_PULSE_LENGTH = 2000  # units of 1ns, divisible by 4
PI_PULSE_LENGTH = 500  # units of 1ns, divisible by 4
PI_HALF_PULSE_LENGTH = PI_PULSE_LENGTH  # units of 1ns, divisible by 4


##########
# Output variables
##########
# in the case of having a readout pulse time of flight should end before digitized readout starts
TIME_OF_FLIGHT = 180  # Units of ns, divisible by 4
SMEARING = 0  # 50 # Units of ns, divisible by 4
# {'out1': 0.21271891043526786, 'out2': 0.2172443777901786}
# number of Average
n_avg = 2

# Input power at the room temperature from QM
power = 0  # -5

saturation_power = power  # max 3dBm
pi_power = power  # max 3dBm
gaussian_power = power  # max 3dBm

# calculate the peak voltage
saturation_wf_amp = (
    np.sqrt(2) * np.sqrt((50 / 1000) * (10 ** (saturation_power / 10)))
) / 2.0
pi_amp = np.sqrt(2) * np.sqrt((50 / 1000) * (10 ** (pi_power / 10)))
gaussian_amp = np.sqrt(2) * np.sqrt((50 / 1000) * (10 ** (gaussian_power / 10)))
pi_half_amp = pi_amp / 2.0
print(saturation_wf_amp)
print(pi_amp)
print(pi_half_amp)

#################
# Gaussian waveforms
#################
pi_I_wf = pi_amp * gaussian(PI_PULSE_LENGTH, PI_PULSE_LENGTH / 5)
pi_half_I_wf = pi_half_amp * gaussian(PI_HALF_PULSE_LENGTH, PI_HALF_PULSE_LENGTH / 5)
minus_pi_half_I_wf = -pi_half_amp * gaussian(
    PI_HALF_PULSE_LENGTH, PI_HALF_PULSE_LENGTH / 5
)
gaussian_I_wf = gaussian_amp * gaussian(
    GAUSSIAN_PULSE_LENGTH, GAUSSIAN_PULSE_LENGTH / 5
)

###################
# Config Dictionary
###################
config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",  # why was this removed???
            "analog_outputs": {
                1: {
                    "offset": DC_OFFSET_I,
                    "delay": ANALOG_OUTPUT_DELAY,
                },
                2: {
                    "offset": DC_OFFSET_Q,
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
                    "offset": 0,
                    "gain_db": 0,
                },  # signal from the down converted signal
                2: {
                    "offset": 0,
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
                "mixer": "mixer_spin",
            },
            "intermediate_frequency": SPIN_IF,
            "operations": {
                "saturation": "saturation_pulse",
                "pi": "pi_pulse",
                "pi_half": "pi_half_pulse",
                "gaussian": "gaussian_pulse",
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
        "readout": {
            "mixInputs": {
                "I": ("con1", 1),
                "Q": ("con1", 2),
                "lo_frequency": SPIN_LO,
                "mixer": "mixer_spin",
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
                    "delay": CRYO_SWITCH_DELAY,  # WHY IS THIS NOT CRYO_SWITCH_DELAY?
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
            "length": READOUT_LENGTH + 500,
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
        "pi_wf": {"type": "arbitrary", "samples": pi_I_wf},
        "pi_half_wf": {"type": "arbitrary", "samples": pi_half_I_wf},
        "minus_pi_half_wf": {"type": "arbitrary", "samples": minus_pi_half_I_wf},
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
        "mixer_spin": [
            {
                "intermediate_frequency": SPIN_IF,
                "lo_frequency": SPIN_LO,
                "correction": IQ_imbalance(MIXER_GAIN, MIXER_PHASE),
            }
        ],
    },
}
