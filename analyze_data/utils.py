import numpy as np
import numpy.typing as npt
from scipy.special import erfcx, erfi
from scipy.constants import physical_constants

mu_B = physical_constants["Bohr magneton in Hz/T"][0]
g_e = abs(physical_constants["electron g factor"][0])
g_DPPH = 2.0037


def linear_to_db_power(data: np.ndarray) -> np.ndarray:
    """Convert normalized linear power data to dB power scale.

    Args:
      data (numpy.ndarray): numpy array of power to be converted from
      normalized linear to dB scale.

    Returns:
      Data of power in logarithmic scale
    """
    return 10 * np.log10(data)


def db_to_lin_power(data: np.ndarray) -> np.ndarray:
    """Convert dB power data to normalized linear power scale.

    Args:
        Data (numpy.ndarray): numpy array of power to be converted from
        dB to normalized linear scale.

    Returns:
        numpy.ndarray: Data of power in normalized linear scale.
    """
    return 10 ** (data / 10)


def db_to_lin_amp(data: np.ndarray) -> np.ndarray:
    """Convert dB power data to normalized linear power scale.

    Args:
        Data (numpy.ndarray): numpy array of power to be converted from
        dB to normalized linear scale.

    Returns:
        numpy.ndarray: Data of power in normalized linear scale.
    """
    return 10 ** (data / 20)


def k_lorentzian(omega, omega_spin, g_ens, gamma):  # eq. 2.116 Cecile's thesis
    """Calculate the K function for a Lorentzian function."""
    return g_ens**2 / (omega - omega_spin + 1j * (gamma) / 2)


# def k_square(omega, omega_spin, g_ens, gamma):  # eq. 2.116 Cecile's thesis
#     """Calculate the K function for a square function."""
#     if np.abs(omega-omega_spin)<gamma:
#         return g_ens**2/
#     else:
#         return 0


def reflection_coef(
    omega: npt.NDArray,
    b_field: float,
    omega_cav: float,
    b_offset: float,
    g_ens: float,
    inhomo_broad: float,
    kappa_int: float,
    kappa_ext: float,
) -> npt.NDArray:
    """Calculate the reflection coefficient amp of a cavity spin system."""

    omega_spins = 2 * np.pi * mu_B * g_DPPH * (b_field - b_offset) / 1e3
    k_func = k_lorentzian(omega, omega_spins, g_ens, inhomo_broad)
    return np.abs(
        1j * kappa_ext / (omega - omega_cav + 1j * (kappa_ext + kappa_int) / 2 - k_func) - 1
    )


def reflection_2d_resonator_spin(
    omega_b_fields: tuple[float, float],
    omega_res: float,
    b_offset: float,
    g_ens: float,
    inhomo_broad: float,
    # kappa_int: float,
    # kappa_ext: float,
) -> float:
    """Calculate the reflection coefficient of a resonators coupled to an
    spin system.

    Args:
        omega_b_fields(tuple[float, float]): Tuple of drive frequency and
        magnetic field (rad/s, mT).
        omega_res (float): Resonator's resonance frequency (rad/s).
        b_offset (float): Offset of the magnetic field, sum of systematic
        and zero field splitting(mT).
        kappa_int (float): Resonator's internal loss rate (rad/s).
        g_ens (float): Ensemble coupling strength (rad/s).
        inhomo_broadening (float): Inhomogeneous broadening (rad/s).
        kappa_ext (float): Resonator coupling rate to drive line (rad/s).

    Returns:
        float: Reflection coefficient
    """
    omega = omega_b_fields[0]
    b_field = omega_b_fields[1]

    # g_ens = 5.598728592162093e6 * 2 * np.pi
    kappa_ext = 4.423e6 * 2 * np.pi
    kappa_int = kappa_ext * 1e-3
    # omega_res = 4.580666094213045e9 * 2 * np.pi
    # inhomo_broad = 0.9676*27.127992967355e6 * 2 * np.pi

    omega_spins = 2 * np.pi * mu_B * g_DPPH * (b_field - b_offset) / 1e3
    k_func = k_lorentzian(omega, omega_spins, g_ens, inhomo_broad)
    # k_func = k_square()
    r = 1j * kappa_ext / (omega - omega_res + 0.5j * (kappa_ext + kappa_int) - k_func) - 1
    return np.abs(r)


def reflection_resonator_amp(
    omega: float, omega_res: float, kappa_int: float, kappa_ext: float
) -> float:
    """Calculate the reflection coefficient of a resonator.

    Args:
        omega (float): Drive frequency.
        omega_res (float): Resonator's resonance frequency.
        kappa_int (float): Resonator's internal loss rate.
        kappa_ext (float): Resonator coupling rate to drive line.

    Returns:
        float: Reflection coefficient
    """
    r = 1j * kappa_ext / (omega - omega_res + 0.5j * (kappa_int + kappa_ext)) - 1
    return np.sqrt(r.real**2 + r.imag**2)


def reflection_resonator_phase(
    omega: float,
    omega_res: float,
    kappa_int: float,
    kappa_ext: float,
    offset: float = 0,
    delay: float = 0,
) -> float:
    """Calculate the reflection coefficient of a resonator.

    Args:
        omega (float): Drive frequency.
        omega_res (float): Resonator's resonance frequency.
        kappa_int (float): Resonator's internal loss rate.
        kappa_ext (float): Resonator coupling rate to drive line.
        offset (float): Global phase offset.
        delay (float): Delay in the transmission line.

    Returns:
        float: Reflection coefficient
    """
    r = np.e ** (1j * omega * delay) * (
        np.e ** (1j * offset)
        * 1j
        * kappa_ext
        / (omega - omega_res + 0.5j * (kappa_int + kappa_ext))
        - 1
    )
    return np.arctan2(r.imag, r.real)


def correct_iq_data(
    i_data: list | np.ndarray | float,
    q_data: list | np.ndarray | float,
    gain_imbalance: float,
    phase_error_deg: float,
) -> tuple:
    """
    Corrects I and Q data for gain imbalance and phase error, returning the
    corrected data in the same type as the input (list, np.ndarray, or float).

    This function applies the standard two-step correction:
    1. A skew correction to the I-channel based on the phase error.
    2. A gain normalization to the Q-channel.

    Args:
        i_data (list | np.ndarray | float): A list, NumPy array, or single float of in-phase (I) data points.
        q_data (list | np.ndarray | float): A list, NumPy array, or single float of quadrature (Q) data points.
        gain_imbalance (float): The ratio of the Q-channel gain to the I-channel gain.
                                 A value of 1.0 means perfect gain balance.
        phase_error_deg (float): The phase error in degrees, representing the deviation
                                 from the ideal 90-degree separation. A value of 0.0 means
                                 perfect quadrature.

    Returns:
        tuple[list, list] | tuple[np.ndarray, np.ndarray] | tuple[float, float]:
        A tuple containing the corrected I and Q data, with the type matching the input.
    """
    # Check the type of the input to determine the return type
    input_type = type(i_data)

    # Convert input data to NumPy arrays for consistent and efficient calculation
    i_array = np.array(i_data)
    q_array = np.array(q_data)

    # Convert phase error from degrees to radians and calculate the skew factor
    phase_error_rad = np.radians(phase_error_deg)
    skew_factor = np.tan(phase_error_rad)

    # Apply the two-step correction formulas:
    # 1. First, correct for the gain imbalance on the Q-channel.
    q_corrected_gain = q_array / gain_imbalance

    # 2. Then, correct for the phase skew by removing the Q-channel's
    #    contribution from the I-channel.
    i_corrected_skewed = i_array - (q_array * skew_factor)

    # In some models, the skew factor is applied to the gain-corrected Q.
    # We will use this more robust approach:
    i_corrected = i_array - (q_corrected_gain * skew_factor)
    q_corrected = q_corrected_gain

    # Convert the corrected data back to the original input type
    if input_type is list:
        return i_corrected.tolist(), q_corrected.tolist()
    elif input_type is np.ndarray:
        return i_corrected, q_corrected
    elif input_type is float:
        return float(i_corrected), float(q_corrected)
    else:
        # Fallback for unexpected types
        return i_corrected.tolist(), q_corrected.tolist()
