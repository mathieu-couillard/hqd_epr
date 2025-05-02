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
    """Calculate the reflection coefficient of a cavity SU2 system."""

    omega_spins = 2 * np.pi * mu_B * g_DPPH * (b_field - b_offset) / 1e3
    k_func = k_lorentzian(omega, omega_spins, g_ens, inhomo_broad)
    return np.abs(
        1j * kappa_ext / (omega - omega_cav + 1j * (kappa_ext + kappa_int) / 2 - k_func)
        - 1
    )


def reflection_2d_resonator_spin(
    omega_b_fields: tuple[float, float],
    omega_res: float,
    b_offset: float,
    g_ens: float,
    inhomo_broad: float,
    kappa_int: float,
    kappa_ext: float,
) -> float:
    """Calculate the reflection coefficient of a resonators coupled to an
    SU2 system.

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

    omega_spins = 2 * np.pi * mu_B * g_DPPH * (b_field - b_offset) / 1e3
    k_func = k_lorentzian(omega, omega_spins, g_ens, inhomo_broad)
    return np.abs(
        1j * kappa_ext / (omega - omega_res + 0.5j * (kappa_ext + kappa_int) - k_func)
        - 1
    )


def reflection_resonator(
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
    return np.abs(
        1j * kappa_ext * (omega - omega_res + 0.5j * (kappa_int + kappa_ext)) - 1
    )
