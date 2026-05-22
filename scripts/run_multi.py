"""
Multi-Program Experiment Runner for gem5-riscv-perf
Usage: python scripts/run_multi.py <workload1,workload2,...> [l1d] [l2] [cpu]
Example: python scripts/run_multi.py matmul,memcopy 32kB 256kB timing
         python scripts/run_multi.py matmul,conv,memcopy 32kB 256kB o3
"""

import subprocess
import sys
import os

GEM5         = "gem5/build/RISCV/gem5.opt"
CONFIG       = "configs/multiprogram_riscv.py"
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

def run_multi(workload_combo, l1d="32kB", l2="256kB", cpu="timing"):
    binaries = []
    for wl in workload_combo:
        if wl not in WORKLOADS:
            print(f"Unknown workload: {wl}")
            print(f"Available: {list(WORKLOADS.keys())}")
            sys.exit(1)
        binaries.append(os.path.abspath(f"{WORKLOAD_DIR}/{WORKLOADS[wl]}"))

    combo_name = "_".join(workload_combo)
    out_name   = f"multi_{combo_name}_l1d_{l1d}_l2_{l2}_{cpu}"
    out_dir    = f"results/{out_name}"
    binary_str = ",".join(binaries)

    cmd = [
        f"./{GEM5}",
        f"--outdir={out_dir}",
        CONFIG,
        f"--binaries={binary_str}",
        f"--l1d-size={l1d}",
        f"--l1i-size=32kB",
        f"--l2-size={l2}",
        f"--cpu-type={CPU_TYPES[cpu]}",
    ]

    print(f"\n{'='*60}")
    print(f"Multi-Program : {' + '.join(workload_combo)}")
    print(f"Cores         : {len(workload_combo)}")
    print(f"CPU           : {cpu.upper()}")
    print(f"L1D Size      : {l1d}")
    print(f"L2  Size      : {l2}")
    print(f"Output        : {out_dir}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, cwd=os.path.abspath("."))
    if result.returncode == 0:
        print(f"\n✓ Done — results in {out_dir}/stats.txt")
    else:
        print(f"\n✗ Failed — check output above")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_multi.py <workloads> [l1d] [l2] [cpu]")
        print("Examples:")
        print("  python scripts/run_multi.py matmul,memcopy")
        print("  python scripts/run_multi.py matmul,memcopy 32kB 256kB timing")
        print("  python scripts/run_multi.py matmul,conv,memcopy 32kB 256kB o3")
        sys.exit(1)

    combo = sys.argv[1].split(",")
    l1d   = sys.argv[2] if len(sys.argv) > 2 else "32kB"
    l2    = sys.argv[3] if len(sys.argv) > 3 else "256kB"
    cpu   = sys.argv[4] if len(sys.argv) > 4 else "timing"

    run_multi(combo, l1d, l2, cpu)
