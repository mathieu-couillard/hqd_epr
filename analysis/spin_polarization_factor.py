import numpy as np

temp_system = 5.3
temp_exchange = 17.6
N = 1.5226e18*1.1
freq = 4.58e9


def boltzmann_ratio_temp(T, T_coupling):
    """
    Calculate the fractional population of the triplet state.

    This function determines the equilibrium population of a triplet state
    relative to a singlet ground state for a given system temperature,
    assuming a degeneracy of 3 for the triplet and 1 for the singlet.

    Args:
        T (float): The system temperature (K).
        T_coupling (float): The energy gap between states expressed in units
            of temperature (K), where ΔE = k_B * T_coupling.

    Returns:
        float: The fraction of the total population in the triplet state
            (ranging from 0 to 1).
    """
    # If the triplet is higher, the exponent must be negative
    delta_E = abs(T_coupling)
    # The Boltzmann factor with degeneracy (3 for triplet, 1 for singlet)
    ratio = 3 * np.exp(-delta_E / T)
    # excited Population
    pct_triplet = ratio / (ratio + 1)

    return pct_triplet


def calculate_spin_polarization_hz(T, freq_hz):
    """
    Calculates spin polarization using frequency in Hertz.

    Parameters:
    T       : float : System temperature in Kelvin (K)
    freq_hz : float : Transition frequency in Hertz (Hz)

    Returns:
    polarization : float : The polarization factor (0 to 1)
    """
    # Physical Constants
    h = 6.62607015e-34  # Planck constant (J*s)
    kB = 1.380649e-23  # Boltzmann constant (J/K)

    if T <= 0:
        return 1.0

    # Energy gap in Kelvin: T_trans = (h * nu) / kB
    # Then arg = T_trans / (2 * T)
    arg = (h * freq_hz) / (2 * kB * T)

    # Polarization P = tanh(h*nu / 2*kB*T)
    polarization = np.tanh(arg)

    return polarization


p_triplet = boltzmann_ratio_temp(temp_system, temp_exchange)
p_temp = calculate_spin_polarization_hz(temp_system, freq)
print(f"-------------------------------")
print(f"At {temp_system}K with a coupling of {temp_exchange}K:")
print(f"Total spins: {N:.3g}.")
print(f"Triplet Population: {N * p_triplet:.3g}")
print(f"-------------------------------")
print(f"At {freq / 1e9:.1f} GHz and {temp_system} K:")
print(f"Polarization Factor: {p_temp * p_triplet:.3g}")
print(f"Polarized spins: {N * p_temp * p_triplet:.3g}")
