"""
Contention Analysis Plots for gem5-riscv-perf
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("plots", exist_ok=True)

# Contention data — O3 only (where contention is meaningful)
data = {
    "matmul + memcopy":       {"matmul": -3.29,  "memcopy": -0.06, "conv": None},
    "matmul + conv":          {"matmul": -0.76,  "memcopy": None,  "conv": -2.17},
    "conv + memcopy":         {"matmul": None,   "memcopy": -0.04, "conv": -9.37},
    "matmul + conv + memcopy":{"matmul": -4.07,  "memcopy": -0.23, "conv": -11.63},
}

wl_colors = {"matmul": "#1F4E79", "memcopy": "#C00000", "conv": "#375623"}
wl_labels = {"matmul": "MatMul", "memcopy": "MemCopy", "conv": "Conv2D"}

# ── Plot 1: Contention degradation per combo ──────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))

combos    = list(data.keys())
workloads = ["matmul", "conv", "memcopy"]
x         = np.arange(len(combos))
width     = 0.25

for i, wl in enumerate(workloads):
    vals = [data[c].get(wl, 0) or 0 for c in combos]
    bars = ax.bar(x + i*width, vals, width,
                  label=wl_labels[wl],
                  color=wl_colors[wl],
                  edgecolor="white")
    for bar, val in zip(bars, vals):
        if val != 0:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() - 0.3,
                    f"{val:.1f}%",
                    ha="center", va="top",
                    fontsize=8, color="white", fontweight="bold")

ax.set_ylabel("IPC Degradation (%)", fontsize=12)
ax.set_title("Multi-Program Contention — IPC Degradation vs Solo (O3 CPU)", fontsize=13)
ax.set_xticks(x + width)
ax.set_xticklabels([c.replace(" + ", "\n+ ") for c in combos], fontsize=9)
ax.legend(fontsize=10)
ax.grid(True, axis="y", alpha=0.3)
ax.axhline(y=0, color="black", linewidth=0.8)
plt.tight_layout()
plt.savefig("plots/contention_degradation.png", dpi=150)
print("Saved: plots/contention_degradation.png")

# ── Plot 2: Conv2D contention scaling ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

conv_scenarios = ["Solo", "+ MatMul", "+ MemCopy", "+ MatMul\n+ MemCopy"]
conv_ipc_o3    = [4.1898, 4.0990, 3.7971, 3.7026]
conv_ipc_timing = [0.6107, 0.6091, 0.6057, 0.6035]

x = np.arange(len(conv_scenarios))
w = 0.35

bars1 = ax.bar(x - w/2, conv_ipc_o3, w,
               label="O3", color="#375623", edgecolor="white")
bars2 = ax.bar(x + w/2, conv_ipc_timing, w,
               label="TIMING", color="#375623", alpha=0.4,
               edgecolor="white", hatch="//")

for bar, val in zip(bars1, conv_ipc_o3):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.03,
            f"{val:.3f}", ha="center", va="bottom", fontsize=9)

ax.set_ylabel("IPC", fontsize=12)
ax.set_title("Conv2D IPC Degradation Under Increasing Contention", fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(conv_scenarios, fontsize=10)
ax.legend(fontsize=10)
ax.grid(True, axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("plots/conv_contention_scaling.png", dpi=150)
print("Saved: plots/conv_contention_scaling.png")

# ── Plot 3: Bandwidth thief visualization ─────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: solo IPC
solo_labels = ["MatMul\nO3", "Conv2D\nO3", "MemCopy\nO3"]
solo_ipc    = [3.0828, 4.1898, 0.5243]
colors      = ["#1F4E79", "#375623", "#C00000"]

axes[0].bar(solo_labels, solo_ipc, color=colors, edgecolor="white")
axes[0].set_title("Solo IPC (Baseline)", fontsize=12)
axes[0].set_ylabel("IPC", fontsize=11)
axes[0].grid(True, axis="y", alpha=0.3)
for i, (bar, val) in enumerate(zip(axes[0].patches, solo_ipc)):
    axes[0].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.03,
                 f"{val}", ha="center", fontsize=10)

# Right: with all three together
multi_labels = ["MatMul\n(+Conv+Mem)", "Conv2D\n(+Mat+Mem)", "MemCopy\n(+Mat+Conv)"]
multi_ipc    = [2.9573, 3.7026, 0.5231]

axes[1].bar(multi_labels, multi_ipc, color=colors, edgecolor="white", alpha=0.85)
axes[1].set_title("IPC Running Together (3-Core)", fontsize=12)
axes[1].set_ylabel("IPC", fontsize=11)
axes[1].grid(True, axis="y", alpha=0.3)
for bar, val in zip(axes[1].patches, multi_ipc):
    axes[1].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.03,
                 f"{val}", ha="center", fontsize=10)

fig.suptitle("Bandwidth Thief Effect — MemCopy Degrades Compute Neighbors", fontsize=13)
plt.tight_layout()
plt.savefig("plots/bandwidth_thief.png", dpi=150)
print("Saved: plots/bandwidth_thief.png")

print("\nAll contention plots saved to plots/")
