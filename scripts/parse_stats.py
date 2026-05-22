"""
Stats Parser for gem5-riscv-perf project
Handles both TIMING and O3 results
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

def get_ipc(lines):
    for key in ["processor.cores.core.ipc", "processor.cores0.core.ipc"]:
        val = parse_stat(lines, key)
        if val: return val
    return None

def get_cpi(lines):
    for key in ["processor.cores.core.cpi", "processor.cores0.core.cpi"]:
        val = parse_stat(lines, key)
        if val: return val
    return None

rows = []
for folder in sorted(os.listdir(RESULTS_DIR)):
    stats_file = os.path.join(RESULTS_DIR, folder, "stats.txt")
    if not os.path.exists(stats_file):
        continue

    # Format: workload_c{cores}_l1d_{l1d}_l2_{l2}_{cpu}
    try:
        parts    = folder.split("_")
        workload = parts[0]
        cores    = int(parts[1].replace("c", ""))
        l1d      = parts[3]
        l2       = parts[5]
        cpu      = parts[6] if len(parts) > 6 else "timing"
    except:
        continue

    with open(stats_file) as f:
        lines = f.readlines()

    ipc       = get_ipc(lines)
    cpi       = get_cpi(lines)
    l1d_miss  = parse_stat(lines, "l1d-cache-0.demandMissRate::total")
    l1i_miss  = parse_stat(lines, "l1i-cache-0.demandMissRate::total")
    l2_miss   = parse_stat(lines, "l2-cache-0.demandMissRate::total")
    sim_ticks = parse_stat(lines, "simTicks")

    rows.append({
        "Workload":  workload,
        "CPU":       cpu.upper(),
        "Cores":     cores,
        "L1D":       l1d,
        "L2":        l2,
        "IPC":       round(ipc, 4)           if ipc      else "N/A",
        "CPI":       round(cpi, 4)           if cpi      else "N/A",
        "L1D Miss%": round(l1d_miss*100, 4)  if l1d_miss else "N/A",
        "L1I Miss%": round(l1i_miss*100, 4)  if l1i_miss else "N/A",
        "L2 Miss%":  round(l2_miss*100, 4)   if l2_miss  else "N/A",
        "SimTicks":  int(sim_ticks)          if sim_ticks else "N/A",
    })

df = pd.DataFrame(rows)
print("\n" + "="*90)
print("gem5 RISC-V Performance Analysis — TIMING vs O3")
print("="*90)
print(df.to_string(index=False))
print("="*90)

df.to_csv("results/summary.csv", index=False)
print("\nSaved to results/summary.csv")
