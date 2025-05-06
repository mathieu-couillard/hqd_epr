import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal


########################
# Util. for Experiment #
########################
def digit_array_generator(min=4, max=2000):
    """Generate the digit array
    ex: result = 4,5,6,...,10,20,30,...,100,200,...,2000
    ------------------
    min : int
    max : int

    Returns
    ------------------
    np.array
    """
    digit = int(np.log10(min))
    x = min
    result = []
    while x <= max:
        result.append(x)
        x = x + 10 ** (digit)
        digit = int(np.log10(x))

    print("scan array: ", result)
    return result


#########################
# Util. for Saving Data #
#########################
### For VNA scan ###
def save_data_2d_vna(
    x_scan, freq_GHz, amp_2d, phase_2d, save_folder, xlabel, EXP_NAME, subfolder=""
):
    """
    Generate and save the figure from 2d array of I and Q data.
    This function is for echo measurement

    ------------------
    x_scan : 1d np array int / float /str
            Scaning parameter of x-axis; ex tau for T2 measurement.
    freq_GHz : 1d np array / float [GHz]
            Frequency sweep range of VNA in GHz.
    Amp_2d : 2d np array float
            Amplitude data correspond to x_scan and freq_GHz.
    Phase_2d : 2d np array float
            Phase data correspond to x_scan and freq_GHz.
    save_folder : str
            Experiment save folder. yyyymm/dd/xxxx-EXP_NAME.
    xlabel : str
            label name of x axis.
    EXP_NAME : str
            Figure title.

    Returns
    ------------------
    None

    Product (saved fig and csv)
    ------------------
    2D heatmap for Amp, Phase (Fig. and csv raw data).
    1D graph for each x_scan parameter (Fig. and csv raw data).
    """
    df_2d_amp = pd.DataFrame(amp_2d.T, index=freq_GHz, columns=x_scan)
    df_2d_amp.to_csv(
        os.path.join(save_folder, "raw_data", subfolder, "2d_Amp.csv"),
        header=True,
        index=True,
        index_label=xlabel + "/Frequency [GHz]",
    )
    df_2d_phase = pd.DataFrame(phase_2d.T, index=freq_GHz, columns=x_scan)
    df_2d_phase.to_csv(
        os.path.join(save_folder, "raw_data", subfolder, "2d_Phase.csv"),
        header=True,
        index=True,
        index_label=xlabel + "/Frequency [GHz]",
    )

    draw_pcolorMesh_echo(
        x_scan,
        freq_GHz,
        df_2d_amp.values,
        xlabel,
        "Amp [V]",
        EXP_NAME,
        save_folder,
        display=True,
        ylabel="Frequency [GHz]",
        subfolder=subfolder,
    )
    draw_pcolorMesh_echo(
        x_scan,
        freq_GHz,
        df_2d_phase.values,
        xlabel,
        "Pahse [Rad]",
        EXP_NAME,
        save_folder,
        display=True,
        ylabel="Frequency [GHz]",
        subfolder=subfolder,
    )

    for ii, x in enumerate(x_scan):
        save_data_1d_vna(
            freq_GHz,
            amp_2d[ii],
            phase_2d[ii],
            save_folder,
            xlabel + "={:.4f}".format(x),
        )


def save_data_1d_vna(freq_Ghz, amp_1d, phase_1d, save_folder, xlabel):
    df_1d = pd.DataFrame(
        np.array((phase_1d, amp_1d)).T,
        index=freq_Ghz,
        columns=["Phase[rad.]", "Amp[V]"],
    )
    df_1d.to_csv(
        save_folder + "//raw_data//1d_{}.csv".format(xlabel),
        header=True,
        index=True,
        index_label="Frequency [GHz]",
    )
    # xlabel is scan parameter ex xlabel = 'RFfreq5p923'
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(freq_Ghz, amp_1d)
    ax1.set_xlabel("Frequency [Hz]")
    ax1.set_ylabel("Amp [dB]")

    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(freq_Ghz, phase_1d)
    ax2.set_xlabel("Frequency [Hz]")
    ax2.set_ylabel("Phase")
    ax2.set_ylim([-200, 200])
    plt.savefig(save_folder + "\\fig\\1d_{}".format(xlabel) + ".png")
    plt.close()


### For Echo Measurement
def save_data_2d_echo(
    x_scan, t, I_2d, Q_2d, save_folder, xlabel, EXP_NAME, subfolder=""
):
    """
    Generate and save the figure from 2d array of I and Q data.
    This function is for echo measurement

    ------------------
    x_scan : 1d np array int / float /str
            Scaning parameter of x-axis; ex tau for T2 measurement.
    t : 1d np array / int [ns]
            Digitizer time [ns].
    I_2d : 2d np array float
            I data correspond to x_scan and t.
    Q_2d : 2d np array float
            Q data correspond to x_scan and t.
    save_folder : str
            Experiment save folder. yyyymm/dd/xxxx-EXP_NAME.
    xlabel : str
            label name of x axis.
    EXP_NAME : str
            Figure title.

    Returns
    ------------------
    None

    Product (saved fig and csv)
    ------------------
    2D heatmap for I, Q, Amp, Phase (Fig. and csv raw data).
    1D graph for each x_scan parameter (Fig. and csv raw data).
    """
    df_2d_amp = pd.DataFrame(np.sqrt(I_2d**2 + Q_2d**2).T, index=t, columns=x_scan)
    raw_data_path_2d = os.path.join(save_folder, "Raw_Data_2D", subfolder)
    os.makedirs(raw_data_path_2d, exist_ok=True)
    df_2d_amp.to_csv(
        os.path.join(raw_data_path_2d, "2d_Amp.csv"),
        header=True,
        index=True,
        index_label=xlabel + "/time[ns]",
    )
    df_2d_phase = pd.DataFrame(np.arctan2(Q_2d, I_2d).T, index=t, columns=x_scan)
    df_2d_phase.to_csv(
        os.path.join(raw_data_path_2d, "2d_Phase.csv"),
        header=True,
        index=True,
        index_label=xlabel + "/time[ns]",
    )
    df_2d_I = pd.DataFrame(I_2d.T, index=t, columns=x_scan)
    df_2d_I.to_csv(
        os.path.join(raw_data_path_2d, "2d_I.csv"),
        header=True,
        index=True,
        index_label=xlabel + "/time[ns]",
    )
    df_2d_Q = pd.DataFrame(Q_2d.T, index=t, columns=x_scan)
    df_2d_Q.to_csv(
        os.path.join(raw_data_path_2d, "2d_Q.csv"),
        header=True,
        index=True,
        index_label=xlabel + "/time[ns]",
    )

    draw_pcolorMesh_echo(
        x_scan,
        t,
        df_2d_amp.values,
        xlabel,
        "Amp [V]",
        EXP_NAME,
        save_folder,
        display=False,
    )
    draw_pcolorMesh_echo(
        x_scan, t, df_2d_phase.values, xlabel, "Pahse [Rad]", EXP_NAME, save_folder
    )
    draw_pcolorMesh_echo(
        x_scan, t, df_2d_I.values, xlabel, "I [V]", EXP_NAME, save_folder
    )
    draw_pcolorMesh_echo(
        x_scan, t, df_2d_Q.values, xlabel, "Q [V]", EXP_NAME, save_folder
    )

    for ii, x in enumerate(x_scan):
        save_data_1d_echo(
            t, I_2d[ii], Q_2d[ii], save_folder, xlabel + "={:.4f}".format(x), subfolder
        )


def save_data_1d_echo(t, I_1d, Q_1d, save_folder, xlabel, subfolder=""):
    phase_1d = np.arctan2(Q_1d, I_1d)
    amp_1d = np.sqrt(I_1d**2 + Q_1d**2)
    df_1d = pd.DataFrame(
        np.array((I_1d, Q_1d, phase_1d, amp_1d)).T,
        index=t,
        columns=["I[V]", "Q[V]", "Phase[rad.]", "Amp[V]"],
    )
    raw_data_1d_path = os.path.join(save_folder, "Raw_Data_1D", subfolder)
    os.makedirs(raw_data_1d_path, exist_ok=True)
    df_1d.to_csv(
        os.path.join(raw_data_1d_path, "1d_{}.csv".format(xlabel)),
        header=True,
        index=True,
        index_label="time[ns]",
    )
    # xlabel is scan parameter ex xlabel = 'RFfreq5p923'
    fig, ax = plt.subplots(facecolor="w")
    ax.plot(t, I_1d, label="I")
    ax.plot(t, Q_1d, label="Q")

    ax.set_xlabel("time [ns]")
    ax.set_ylabel("Amp [V]")
    raw_data_1d_fig_path = os.path.join(save_folder, "Fig_1D", subfolder)
    os.makedirs(raw_data_1d_fig_path, exist_ok=True)
    plt.savefig(os.path.join(raw_data_1d_fig_path, "1d_{}".format(xlabel) + ".png"))
    plt.close()
    yes = True
    if yes:
        fig, ax = plt.subplots(facecolor="w")
        ax.plot(t, amp_1d, label="Amp")
        # ax.plot(t, Q_1d, label="Q")

        ax.set_xlabel("time [ns]")
        ax.set_ylabel("Amp [V]")
        raw_data_1d_fig_path = os.path.join(save_folder, "Fig_1D", subfolder)
        os.makedirs(raw_data_1d_fig_path, exist_ok=True)
        plt.savefig(
            os.path.join(raw_data_1d_fig_path, "1d_{}".format(xlabel) + "amp" + ".png")
        )
        plt.close()


def draw_pcolorMesh_echo(
    x,
    t,
    z,
    xlabel,
    z_label,
    title,
    folder,
    display=False,
    ylabel="time [ns]",
    subfolder="",
):
    if display:
        plt.figure(facecolor="w")
        plt.pcolormesh(x, t, z)
        plt.xlabel(xlabel)
        plt.ylabel("time [ns]")
        plt.colorbar(label=z_label)
        plt.title(title)
        plt.show()

    plt.figure(facecolor="w")
    plt.pcolormesh(x, t, z)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.colorbar(label=z_label)
    plt.title(title)
    raw_data_2d_fig_path = os.path.join(folder, "Fig_2D", subfolder)
    os.makedirs(raw_data_2d_fig_path, exist_ok=True)
    plt.savefig(raw_data_2d_fig_path + "\\2d_" + z_label + "_" + subfolder + ".png")
    plt.close()


import queue
import threading
import time


class Input(threading.Thread):
    """
    Customized input() function. This class enable us to use input()
    function without blocking.
    Input.input() will return the None if there are no input.

    cin = Input()
    for i in range(10):
            time.sleep(1)  # 何かの仕事のつもり
            t = cin.input(block=False)
            print('{}: t={}'.format(i, t))
    """

    def __init__(self, mes=""):
        super().__init__(daemon=True)
        self.mes = mes
        self.queue = queue.Queue()
        self.start()

    def run(self):
        while True:
            t = input(self.mes)
            self.queue.put(t)

    def input(self, block=False, timeout=1):
        """
        ------------------
        block : bool
                False: return the None when there are no input.
                True: Will not return until user input something.
        timeout: float [s]
                block == True: wait timeout second and return the input or None.
                block == False: return None when there are no input.

        Returns
        ------------------
        str or None
        """
        try:
            return self.queue.get(block, timeout=timeout)
        except queue.Empty:
            return None
