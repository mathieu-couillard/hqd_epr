import shutil
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyvisa as visa
from drivers import KeysightE8247C, AMI430Vector, KeysightN9010A
from qm import LoopbackInterface, SimulationConfig
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager

from qualang_tools.loops import from_array
from qualang_tools.results import fetching_tool, progress_counter
from qualang_tools.units import unit

from config import qm_config
from config import InstrumentAddresses as InstAddr
from config.experiment_config import FreeInductionDecay as FIDconf
from config.experiment_config import MagConfig, EXPERIMENT_BASE_PATH, n_avg
from config.experiment_config import __file__ as EXPPERIMENT_CONFIG_PATH

from utils import generate_path
from utils import save_data_1d_echo

# TODO: this should be in experiment config
PROJECT_NAME = "impedance_matching_dpph"
EXPERIMENT_NAME = "fid_4K_dpph"

CHUNCK_SIZE = 4 // 4
ARRAY_SIZE = qm_config.READOUT_LENGTH // (CHUNCK_SIZE * 4)


with program() as Pulse_Duration_calib:
    pass


rm = visa.ResourceManager()
qmm = QuantumMachinesManager(host=InstAddr.qm)
