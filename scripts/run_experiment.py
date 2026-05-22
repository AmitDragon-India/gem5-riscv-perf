"""
Experiment Runner for gem5-riscv-perf
Usage: python scripts/run_experiment.py <workload> [cores] [l1d] [l2] [cpu]
Example: python scripts/run_experiment.py matmul 1 32kB 256kB o3
"""

import subprocess
import sys
import os

GEM5         = "gem5/build/RISCV/gem5.opt"
CONFIG       = "configs/multicore_riscv.py"
WORKLOAD_DIR = "workloads"

WORKLOADS = {
    "matmul":  "matmul",
    "memcopy": "memcopy",
    "conv":    "conv_layer",
}

CPU_TYPES = {
    "timing": "TIMING",
    "o3":     "O3",
}

def run(workload, cores=1, l1d="32kB", l2="256kB", cpu="timing"):
    if workload not in WORKLOADS:
        print(f"Unknown workload: {workload}")
        print(f"Available: {list(WORKLOADS.keys())}")
        sys.exit(1)

    if cpu not in CPU_TYPES:
        print(f"Unknown cpu: {cpu}")
        print(f"Available: {list(CPU_TYPES.keys())}")
        sys.exit(1)

    binary   = os.path.abspath(f"{WORKLOAD_DIR}/{WORKLOADS[workload]}")
    out_name = f"{workload}_c{cores}_l1d_{l1d}_l2_{l2}_{cpu}"
    out_dir  = f"results/{out_name}"

    cmd = [
        f"./{GEM5}",
        f"--outdir={out_dir}",
        CONFIG,
        f"--cmd={binary}",
        f"--num-cores={cores}",
        f"--l1d-size={l1d}",
        f"--l1i-size=32kB",
        f"--l2-size={l2}",
        f"--cpu-type={CPU_TYPES[cpu]}",
    ]

    print(f"\n{'='*60}")
    print(f"Workload : {workload}")
    print(f"CPU      : {cpu.upper()}")
    print(f"Cores    : {cores}")
    print(f"L1D Size : {l1d}")
    print(f"L2  Size : {l2}")
    print(f"Output   : {out_dir}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=os.path.abspath("."))
    if result.returncode == 0:
        print(f"\n✓ Done — results in {out_dir}/stats.txt")
    else:
        print(f"\n✗ Failed — check output above")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_experiment.py <workload> [cores] [l1d] [l2] [cpu]")
        print("Examples:")
        print("  python scripts/run_experiment.py matmul")
        print("  python scripts/run_experiment.py matmul 1 32kB 256kB timing")
        print("  python scripts/run_experiment.py matmul 1 32kB 256kB o3")
        print("  python scripts/run_experiment.py memcopy 1 8kB 256kB o3")
        sys.exit(1)

    workload = sys.argv[1]
    cores    = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    l1d      = sys.argv[3]      if len(sys.argv) > 3 else "32kB"
    l2       = sys.argv[4]      if len(sys.argv) > 4 else "256kB"
    cpu      = sys.argv[5]      if len(sys.argv) > 5 else "timing"

    run(workload, cores, l1d, l2, cpu)
