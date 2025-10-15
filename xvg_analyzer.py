import matplotlib.pyplot as plt
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# === Properties and units ===
properties = ["area", "gyrate", "hydrogen-bonds", "pressure", "rmsd", "rmsf", "temperature"]

units = {
    "area": " (Å²)",
    "RoG": " (Å)",
    "hydrogen-bonds": " (count)",
    "pressure": " (bar)",
    "rmsd": " (Å)",
    "rmsf": " (Å)",
    "temperature": " (K)"
}

y_labels = {
    "area": "Area",
    "gyrate": "RoG",
    "hydrogen-bonds": "Hydrogen Bonds",
    "pressure": "Pressure",
    "rmsd": "RMSD",
    "rmsf": "RMSF",
    "temperature": "Temperature"
}

# === Functions ===
def load_xvg(filename):
    """Load XVG data, ignoring comment lines."""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    continue
    return np.array(data)

def set_legend_top_right():
    plt.legend(loc="upper right", frameon=True)

def inflate_ylim(y_wt, y_mut, frac=0.15, min_pad=0.05):
    """Compute y-limits with padding to avoid cramped/superimposed look."""
    y_all = np.concatenate([y_wt, y_mut])
    y_min, y_max = np.nanmin(y_all), np.nanmax(y_all)
    if np.isclose(y_min, y_max):
        pad = max(abs(y_max) * frac, min_pad)
        return (y_min - pad, y_max + pad)
    span = y_max - y_min
    pad = max(span * frac, min_pad)
    return (y_min - pad, y_max + pad)

# === GUI for file selection ===
root = tk.Tk()
root.withdraw()  # hide main window

messagebox.showinfo("XVG Analyzer", "Select all XVG files (WT and mutant together). Mutant files should have a suffix like '_V698I'.")
all_files = filedialog.askopenfilenames(title="Select all XVG files", filetypes=[("XVG files", "*.xvg")])
if not all_files:
    messagebox.showerror("Error", "No files selected, exiting.")
    exit()

save_dir = filedialog.askdirectory(title="Select folder to save plots")
if not save_dir:
    messagebox.showerror("Error", "No output folder selected, exiting.")
    exit()

os.makedirs(save_dir, exist_ok=True)

# === Separate WT and mutant files ===
wt_files = [f for f in all_files if "_" not in os.path.basename(f).split('.')[0]]
mut_files = [f for f in all_files if "_" in os.path.basename(f).split('.')[0]]

# Create a dictionary for mutant files keyed by property prefix
mut_dict = {}
for f in mut_files:
    prop = os.path.basename(f).split('_')[0]  # take part before first _
    mut_dict[prop] = f

# === Main plotting loop ===
for wt_file in wt_files:
    prop = os.path.basename(wt_file).split('.')[0]  # e.g., "area", "rmsd"
    if prop not in properties:
        print(f"⚠️ Skipping {prop}: not a recognized property")
        continue

    if prop not in mut_dict:
        print(f"⚠️ Skipping {os.path.basename(wt_file)}: no matching mutant file")
        continue

    mut_file = mut_dict[prop]

    wt = load_xvg(wt_file)
    mut = load_xvg(mut_file)

    if wt.size == 0 or mut.size == 0:
        print(f"⚠️ Skipping {prop}: file empty or unreadable")
        continue

    # Time axis fix
    if prop != "rmsf" and wt[-1, 0] > 500:
        wt[:, 0] /= 1000.0
        mut[:, 0] /= 1000.0

    # Convert units
    if prop in ["rmsd", "rmsf", "gyrate"]:
        wt[:, 1] *= 10.0
        mut[:, 1] *= 10.0
    elif prop == "area":
        wt[:, 1] *= 100.0
        mut[:, 1] *= 100.0

    # RMSF special case
    if prop == "rmsf":
        plt.figure(figsize=(8, 6))
        plt.plot(wt[:, 0], wt[:, 1], label="WT", color="black")
        plt.plot(mut[:, 0], mut[:, 1], label="Mutant", color="red", linestyle="--")
        plt.xlabel("Residue Index", fontsize=12)
        plt.ylabel(f"RMSF{units[prop]}", fontsize=12)
        plt.title("RMSF per Residue", fontsize=14)
        set_legend_top_right()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.xticks(np.arange(200, 1101, 100))
        ylo, yhi = inflate_ylim(wt[:, 1], mut[:, 1], frac=0.10)
        plt.ylim(ylo, yhi)
        plt.tight_layout()
        save_path = os.path.join(save_dir, f"{prop}_comparison.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"✅ Saved: {save_path}")
        continue

    # Time-based plots
    plt.figure(figsize=(8, 6))
    plt.plot(wt[:, 0], wt[:, 1], label="WT", color="black")
    plt.plot(mut[:, 0], mut[:, 1], label="Mutant", color="red", linestyle="--")
    plt.xlabel("Time (ns)", fontsize=12)
    unit_key = "RoG" if prop == "gyrate" else prop
    plt.ylabel(y_labels[prop] + units[unit_key], fontsize=12)
    plt.title(f"{y_labels[prop]} over Time", fontsize=14)
    set_legend_top_right()
    plt.grid(True, linestyle="--", alpha=0.5)
    x_max = float(np.nanmax(np.concatenate([wt[:, 0], mut[:, 0]])))
    plt.xlim(0.0, x_max)
    plt.margins(x=0)
    if prop in ["temperature", "pressure"]:
        ylo, yhi = inflate_ylim(wt[:, 1], mut[:, 1], frac=0.25, min_pad=0.1)
    else:
        ylo, yhi = inflate_ylim(wt[:, 1], mut[:, 1], frac=0.10, min_pad=0.05)
    plt.ylim(ylo, yhi)
    plt.tight_layout()
    save_path = os.path.join(save_dir, f"{prop}_comparison.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"✅ Saved: {save_path}")

print("\n🎉 All plots saved in:", os.path.abspath(save_dir))
messagebox.showinfo("XVG Analyzer", f"🎉 All plots saved in:\n{os.path.abspath(save_dir)}")
