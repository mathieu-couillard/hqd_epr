from config import qm_config
from qm.qua import *


def get_iq_full_demod(
    operation: str = "readout",
    element: str = "digitizer",
    element_output: str = "out1",
    I=None,
    Q=None,
    I_st=None,
    Q_st=None,
):
    j = declare(int)
    I1 = declare(fixed)
    I2 = declare(fixed)
    Q1 = declare(fixed)
    Q2 = declare(fixed)

    if I is None:
        I = declare(fixed)
    if Q is None:
        Q = declare(fixed)
    if I_st is None:
        I_st = declare_stream()
    if Q_st is None:
        Q_st = declare_stream()

    measure(
        operation,
        element,
        demod.full("cos", I1, "out1"),
        demod.full("sin", Q1, "out1"),
        demod.full("cos", Q2, "out2"),
        demod.full("sin", I2, "out2"),
    )

    assign(I, I1 + I2)
    assign(Q, Q1 - Q2)
    save(I, I_st)
    save(Q, Q_st)

    return I, Q, I_st, Q_st


def get_iq_slice_demod(
    time_array_size: int,
    chunck_size: int = 20,  # divisible by 4ns and 1/IF (10ns for 100MHz)
    operation: str = "readout",
    element: str = "digitizer",
    element_output: str = "out1",
    I=None,
    Q=None,
    I_st=None,
    Q_st=None,
):
    j = declare(int)
    I1 = declare(fixed, size=time_array_size)
    I2 = declare(fixed, size=time_array_size)
    Q1 = declare(fixed, size=time_array_size)
    Q2 = declare(fixed, size=time_array_size)

    if I is None:
        I = declare(fixed, size=time_array_size)
    if Q is None:
        Q = declare(fixed, size=time_array_size)
    if I_st is None:
        I_st = declare_stream()
    if Q_st is None:
        Q_st = declare_stream()

    measure(
        operation,
        element,
        demod.sliced("cos", I1, chunck_size, "out1"),
        demod.sliced("sin", Q1, chunck_size, "out1"),
        demod.sliced("cos", Q2, chunck_size, "out2"),
        demod.sliced("sin", I2, chunck_size, "out2"),
    )

    with for_(j, 0, j < time_array_size, j + 1):
        assign(I[j], I1[j] + I2[j])
        assign(Q[j], Q1[j] - Q2[j])
        save(I[j], I_st)
        save(Q[j], Q_st)

    return I, Q, I_st, Q_st


def get_iq_full_dual_demod(
    operation: str = "readout",
    element: str = "digitizer",
    element_output: str = "out1",
    I=None,
    Q=None,
    I_st=None,
    Q_st=None,
):
    # TODO: this function needs to be tested.
    # The integration weights may be in the wrong order.
    if I is None:
        I = declare(fixed)
    if Q is None:
        Q = declare(fixed)
    if I_st is None:
        I_st = declare_stream()
    if Q_st is None:
        Q_st = declare_stream()

    measure(
        operation,
        element,
        None,
        dual_demod.full("cos", "sin", I),
        dual_demod.full("minus_sin", "cos", Q),
    )
    save(I, I_st)
    save(Q, Q_st)

    return I, Q, I_st, Q_st
