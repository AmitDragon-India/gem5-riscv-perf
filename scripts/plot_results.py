"""
Plotting Script for gem5-riscv-perf
TIMING vs O3 comparison + cache sweep
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

os.makedirs("plots", exist_ok=True)
df = pd.read_csv("results/summary.csv")

size_order = {"8kB": 8, "16kB": 16, "32kB": 32, "64kB": 64}
df["L1D_KB"] = df["L1D"].map(size_order)
df = df.sort_values(["Workload", "CPU", "L1D_KB"])

workloads = ["matmul", "memcopy", "conv"]
wl_labels = {"matmul": "MatMul", "memcopy": "MemCopy", "conv": "Conv2D"}
wl_colors = {"matmul": "#1F4E79", "memcopy": "#C00000", "conv": "#375623"}
cpu_styles = {"TIMING": "--", "O3": "-"}
cpu_markers = {"TIMING": "s", "O3": "o"}

# ── Plot 1: IPC vs L1D — TIMING vs O3 per workload ────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, wl in zip(axes, workloads):
    for cpu in ["TIMING", "O3"]:
        d = df[(df["Workload"] == wl) & (df["CPU"] == cpu)]
        if d.empty: continue
        ipc_vals = pd.to_numeric(d["IPC"], errors="coerce")
        ax.plot(d["L1D_KB"], ipc_vals,
                color=wl_colors[wl],
                linestyle=cpu_styles[cpu],
                marker=cpu_markers[cpu],
                linewidth=2, markersize=8,
                label=f"{cpu}")
    ax.set_title(f"{wl_labels[wl]}", fontsize=13, fontweight="bold")
    ax.set_xlabel("L1D Cache Size (kB)", fontsize=11)
    ax.set_ylabel("IPC", fontsize=11)
    ax.set_xticks([8, 16, 32, 64])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

fig.suptitle("IPC vs L1D Cache Size — TIMING vs O3 CPU", fontsize=14)
plt.tight_layout()
plt.savefig("plots/ipc_timing_vs_o3.png", dpi=150)
print("Saved: plots/ipc_timing_vs_o3.png")

# ── Plot 2: IPC Speedup O3 vs TIMING at 32kB ──────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

baseline = df[df["L1D"] == "32kB"].copy()
timing = baseline[baseline["CPU"] == "TIMING"].set_index("Workload")
o3     = baseline[baseline["CPU"] == "O3"].set_index("Workload")

speedups = []
wl_names = []
for wl in workloads:
    if wl in timing.index and wl in o3.index:
        t_ipc = float(timing.loc[wl, "IPC"])
        o_ipc = float(o3.loc[wl, "IPC"])
        speedups.append(round(o_ipc / t_ipc, 2))
        wl_names.append(wl_labels[wl])

bars = ax.bar(wl_names, speedups,
              color=[wl_colors[w] for w in workloads],
              edgecolor="white", linewidth=0.5)
ax.axhline(y=1.0, color="black", linestyle="--", linewidth=1, label="No speedup (1x)")
ax.set_ylabel("IPC Speedup (O3 / TIMING)", fontsize=12)
ax.set_title("O3 Speedup over TIMING CPU at 32kB L1D Cache", fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, axis="y", alpha=0.3)
for bar, val in zip(bars, speedups):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.05,
            f"{val}x", ha="center", va="bottom",
            fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("plots/o3_speedup.png", dpi=150)
print("Saved: plots/o3_speedup.png")

# ── Plot 3: L1D Miss Rate TIMING vs O3 ────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, wl in zip(axes, workloads):
    for cpu in ["TIMING", "O3"]:
        d = df[(df["Workload"] == wl) & (df["CPU"] == cpu)]
        if d.empty: continue
        miss_vals = pd.to_numeric(d["L1D Miss%"], errors="coerce")
        ax.plot(d["L1D_KB"], miss_vals,
                color=wl_colors[wl],
                linestyle=cpu_styles[cpu],
                marker=cpu_markers[cpu],
                linewidth=2, markersize=8,
                label=f"{cpu}")
    ax.set_title(f"{wl_labels[wl]}", fontsize=13, fontweight="bold")
    ax.set_xlabel("L1D Cache Size (kB)", fontsize=11)
    ax.set_ylabel("L1D Miss Rate (%)", fontsize=11)
    ax.set_xticks([8, 16, 32, 64])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

fig.suptitle("L1D Miss Rate — TIMING vs O3 CPU", fontsize=14)
plt.tight_layout()
plt.savefig("plots/l1d_miss_timing_vs_o3.png", dpi=150)
print("Saved: plots/l1d_miss_timing_vs_o3.png")

# ── Plot 4: Memory Wall Visualization ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

categories = ["MatMul\nTIMING", "MatMul\nO3",
              "Conv2D\nTIMING", "Conv2D\nO3",
              "MemCopy\nTIMING", "MemCopy\nO3"]
ipc_vals   = [0.6786, 3.0828, 0.6107, 4.1898, 0.3941, 0.5243]
bar_colors = ["#1F4E79", "#2E75B6",
              "#375623", "#70AD47",
              "#C00000", "#FF7575"]

bars = ax.bar(categories, ipc_vals, color=bar_colors,
              edgecolor="white", linewidth=0.5)
ax.set_ylabel("IPC (Instructions Per Cycle)", fontsize=12)
ax.set_title("Memory Wall Effect — O3 Cannot Fix Bandwidth Bottleneck", fontsize=13)
ax.grid(True, axis="y", alpha=0.3)
for bar, val in zip(bars, ipc_vals):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.03,
            f"{val}", ha="center", va="bottom", fontsize=10)

# Annotation
ax.annotate("Memory Wall:\nO3 only 1.3x faster",
            xy=(4.5, 0.52), fontsize=10, color="#C00000",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#C00000"))
plt.tight_layout()
plt.savefig("plots/memory_wall.png", dpi=150)
print("Saved: plots/memory_wall.png")

print("\nAll plots saved to plots/")
