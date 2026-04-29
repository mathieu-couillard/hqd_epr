import pandas as pd

# import matplotlib as mpl
# mpl.rcParams["backend"] = "QtAgg"
import matplotlib.pyplot as plt
from pathlib import Path
import re  # Needed for parsing B-field values from column names
import numpy as np

CSV_FILE_A = Path("./Data2D_mag_4p5809095GHz_-10dBm_strong.csv")
CSV_FILE_B = Path("./Data2D_mag_4p5809095GHz_-10dBm_weak.csv")
X_AXIS_COLUMN = "Magnetic field (mT)"
Y_AXIS_COLUMN = "Frequency (GHz)"


def generate_single_heatmap(
    csv_filepath: Path,
    freq_col_label: str,
    plot_title: str,
    ax: plt.Axes,
    target_frequency: float = None,
    b_field_offset: float = 0,
):
    """
    Reads a standard 2D spectroscopic CSV file (B-field in header, Frequency in index),
    performs background subtraction by subtracting the '158.6' column from all others,
    and generates a 2D heatmap plot.

    Args:
        csv_filepath (Path): The path to the input CSV file.
        freq_col_label (str): The label to use for the Frequency Y-axis.
        plot_title (str): The title for the specific subplot.
        ax (plt.Axes): The Matplotlib Axes object to draw the plot on.
    """

    try:
        # 1. Read the CSV file: header=0 means the first row is the header (B-field values).
        # index_col=0 means the first column is the index (Frequency values).
        df = pd.read_csv(csv_filepath, header=0, index_col=0)
        print(f"\nProcessing data from {csv_filepath.name}. Shape: {df.shape}")

        # --- Background Subtraction ---
        COLUMN_TO_SUBTRACT = "158.6"

        if COLUMN_TO_SUBTRACT in df.columns:
            # Extract the background signal Series
            background_signal = df[COLUMN_TO_SUBTRACT]

            # Subtract the background signal from ALL columns, aligned by the Frequency index (axis=0).
            # This uses pandas broadcasting.
            df = df.sub(background_signal, axis=0)
            print(f"Subtracted column '{COLUMN_TO_SUBTRACT}' from all other signal columns.")

            # Drop the background column, which is now near-zero
            df = df.drop(columns=[COLUMN_TO_SUBTRACT])
        else:
            print(f"Column '{COLUMN_TO_SUBTRACT}' not found, skipping subtraction.")

        # --- Data Preparation for Heatmap ---

        # New X-Axis data (B-Field) - Extracted from the remaining column names, converted to float
        b_field_values = df.columns.astype(float).values - b_field_offset
        X_min_B, X_max_B = (
            b_field_values.min(),
            b_field_values.max(),
        )

        # New Y-Axis data (Frequency) - Extracted from the DataFrame index, converted to float
        frequency_values = df.index.astype(float).values
        frequency_values = frequency_values * 1e-9
        Y_min_F, Y_max_F = frequency_values.min(), frequency_values.max()

        # Extract the Signal Intensity matrix (Z data).
        # Rows (Frequency) -> Y-axis, Columns (B-field) -> X-axis.
        Z_data = df.values

        # --- Heatmap Plotting ---

        # Use ax.imshow for the 2D data visualization
        # extent is [X_min_B, X_max_B, Y_min_F, Y_max_F]
        im = ax.imshow(
            Z_data,
            aspect="auto",
            origin="lower",
            extent=[X_min_B, X_max_B, Y_min_F, Y_max_F],
            cmap="jet",
        )

        # Add a color bar
        plt.colorbar(im, ax=ax, label="Reflection (dB)")

        # 4. Set titles and labels for clarity
        # ax.set_title(plot_title, fontsize=14, fontweight='bold')
        ax.set_xlabel("Magnetic Field (mT)", fontsize=12)  # B-field is X-axis
        ax.set_ylabel(Y_AXIS_COLUMN, fontsize=12)  # Frequency is Y-axis

        # --- Add Oblique Line (B) ---
        # The line relationship is y = m * x, where x is B-field (T) and y is Frequency (MHz).
        # Slope m = 28 MHz/mT. Convert to plot units (MHz/T): 28 * 1000 = 28000 MHz/T.
        slope_MHz_per_mT = 28.023

        # Calculate the corresponding frequency (Y-values) for each B-field value (X-values)
        b_field_values_t = (
            df.columns.astype(float).values - b_field_offset
        )  # X-axis data in Tesla
        oblique_frequency_line = slope_MHz_per_mT * 1e-3 * b_field_values_t  # Y-axis data in MHz

        ax.plot(
            b_field_values_t,  # X-data (Tesla)
            oblique_frequency_line,  # Y-data (MHz)
            color="white",
            linestyle="-",
            linewidth=2.0,
            # label=f"Slope: {slope_MHz_per_mT} MHz/mT",
        )
        # ax.legend(loc="upper right")
        print(f"Added oblique line with slope {slope_MHz_per_mT} MHz/mT.")

        if target_frequency is not None:
            # Scale the target frequency just like the axis data
            scaled_target_freq = target_frequency
            ax.axhline(
                y=scaled_target_freq,
                color="white",  # Use cyan for high visibility on magma cmap
                linestyle="--",
                linewidth=1.5,
            )
            print(f"Added horizontal line at scaled frequency: {scaled_target_freq:.4f}")

        # Ensure consistent tick marks for B-field (X-axis) and Frequency (Y-axis)

        # Use a subset of B-field values for X-ticks to avoid overlap (display approx 5 ticks)
        tick_interval_B = max(1, len(b_field_values) // 5)
        b_field_ticks = b_field_values[::tick_interval_B]

        ax.set_xticks(b_field_ticks)  # Use subset of B-field for X-ticks
        # Rotate X-labels for better readability
        ax.set_xticklabels([f"{b:.1f}" for b in b_field_ticks], rotation=45, ha="right")

        # Use a subset of Freq values for Y-ticks to keep the axis clean
        tick_interval_F = max(1, len(frequency_values) // 5)
        ax.set_yticks(frequency_values[::tick_interval_F])
        ax.set_yticklabels([f"{f:.1f}" for f in frequency_values[::tick_interval_F]])

    except FileNotFoundError:
        print(f"\nError: The file '{csv_filepath}' was not found.")
    except Exception as e:
        print(f"\nAn unexpected error occurred while plotting {csv_filepath.name}: {e}")
        # print(f"Debug DataFrame head:\n{df.head().to_string()}")


if __name__ == "__main__":
    # --- Setup ---
    CSV_FILE_A = CSV_FILE_A
    CSV_FILE_B = CSV_FILE_B

    # This is the label for the Y-axis
    FREQUENCY_COLUMN_LABEL = "Unnamed: 0"

    # --- Plotting ---

    # 2. Setup the side-by-side subplot figure
    # Create a figure and a set of subplots (1 row, 2 columns)
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))  # Slightly taller figure for rotated labels
    # fig.suptitle("Comparison of 2D Spectroscopic Data (Heatmaps) - Background Subtracted", fontsize=20, fontweight='bold')

    # 3. Plot the first file (on the left axis)
    generate_single_heatmap(
        csv_filepath=CSV_FILE_A,
        freq_col_label=FREQUENCY_COLUMN_LABEL,
        plot_title="No Magnetic field gradient",
        ax=axes[0],
        target_frequency=4.5806595,
        b_field_offset=1.07,
    )
    # Add subplot label (a)
    axes[0].text(
        0.02,
        0.98,
        "(a)",
        transform=axes[0].transAxes,
        fontsize=18,
        fontweight="bold",
        verticalalignment="top",
        color="white",
    )

    # 4. Plot the second file (on the right axis)
    generate_single_heatmap(
        csv_filepath=CSV_FILE_B,
        freq_col_label=FREQUENCY_COLUMN_LABEL,
        plot_title="Magnetic field gradient",
        ax=axes[1],
        target_frequency=4.5806595,
        b_field_offset=1.14,
    )
    axes[1].text(
        0.02,
        0.98,
        "(b)",
        transform=axes[1].transAxes,
        fontsize=18,
        fontweight="bold",
        verticalalignment="top",
        color="white",
    )
    # Adjust layout to prevent overlap and display
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust for suptitle

    output_filename = Path("comparison_heatmap.png")
    plt.savefig(output_filename)
    print(f"\nComparison plot saved successfully as '{output_filename.name}'.")
    plt.show()
