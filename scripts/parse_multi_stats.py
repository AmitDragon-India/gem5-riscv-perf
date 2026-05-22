"""
Multi-Program Stats Parser for gem5-riscv-perf
Correct contention: compares O3 multi vs O3 solo
"""

import os
import pandas as pd

RESULTS_DIR = "results"

def parse_stat(lines, key):
    for line in lines:
        if key in line:
            parts = line.split()
            for p in parts:
                try:
                    val = float(p)
                    if val == val:
                        return val
                except ValueError:
                    continue
    return None

def get_core_ipc(lines, core_idx):
    return parse_stat(lines, f"processor.cores{core_idx}.core.ipc")

def get_core_l1d_miss(lines, core_idx):
    return parse_stat(lines, f"l1d-cache-{core_idx}.demandMissRate::total")

def get_core_l2_miss(lines, core_idx):
    return parse_stat(lines, f"l2-cache-{core_idx}.demandMissRate::total")

rows = []
for folder in sorted(os.listdir(RESULTS_DIR)):
    if not folder.startswith("multi_"):
        continue

    stats_file = os.path.join(RESULTS_DIR, folder, "stats.txt")
    if not os.path.exists(stats_file):
        continue

    try:
        parts     = folder.replace("multi_", "").split("_")
        cpu       = parts[-1]
        l2        = parts[-2]
        l1d       = parts[-4]
        l1d_idx   = parts.index(l1d)
        workloads = parts[:l1d_idx-1]
    except Exception as e:
        print(f"Skipping {folder}: {e}")
        continue

    with open(stats_file) as f:
        lines = f.readlines()

    sim_ticks = parse_stat(lines, "simTicks")

    for i, wl in enumerate(workloads):
        ipc      = get_core_ipc(lines, i)
        l1d_miss = get_core_l1d_miss(lines, i)
        l2_miss  = get_core_l2_miss(lines, i)

        rows.append({
            "Combo":     " + ".join(workloads),
            "Workload":  wl,
            "Core":      i,
            "CPU":       cpu.upper(),
            "L1D":       l1d,
            "L2":        l2,
            "IPC":       round(ipc, 4)           if ipc      else "N/A",
            "L1D Miss%": round(l1d_miss*100, 4)  if l1d_miss else "N/A",
            "L2 Miss%":  round(l2_miss*100, 4)   if l2_miss  else "N/A",
            "SimTicks":  int(sim_ticks)          if sim_ticks else "N/A",
        })

df = pd.DataFrame(rows)
print("\n" + "="*95)
print("gem5 RISC-V Multi-Program Contention Analysis")
print("="*95)
print(df.to_string(index=False))
print("="*95)

# Correct contention baseline — O3 solo vs TIMING solo
solo_ipc = {
    ("matmul", "TIMING"): 0.6786,
    ("memcopy", "TIMING"): 0.3941,
    ("conv",   "TIMING"): 0.6107,
    ("matmul", "O3"):     3.0828,
    ("memcopy", "O3"):    0.5243,
    ("conv",   "O3"):     4.1898,
}

print("\n── Contention Summary (correct: multi vs solo same CPU) ──")
print(f"  {'Workload':8s} {'Combo':35s} {'CPU':6s} {'Solo':8s} {'Multi':8s} {'Delta':>8s}")
print("  " + "-"*80)

for _, row in df.iterrows():
    wl  = row["Workload"]
    cpu = row["CPU"]
    key = (wl, cpu)
    if key in solo_ipc and row["IPC"] != "N/A":
        solo  = solo_ipc[key]
        multi = float(row["IPC"])
        delta = ((multi - solo) / solo) * 100
        print(f"  {wl:8s} [{row['Combo']:33s}] "
              f"{cpu:6s} "
              f"{solo:.4f}   {multi:.4f}   {delta:+.2f}%")

df.to_csv("results/multi_summary.csv", index=False)
print("\nSaved to results/multi_summary.csv")
