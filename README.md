# gem5 RISC-V Multi-Core Performance Analysis

A systematic performance characterization study of RISC-V multi-core systems using gem5, analyzing cache hierarchy behavior, memory bandwidth bottlenecks, microarchitecture impact, and multi-program contention across compute-bound and memory-bound workloads.

## Key Findings

### 1. Memory Wall Effect
Out-of-order (O3) execution provides **4.54x–6.86x IPC improvement** for compute-bound workloads (MatMul, Conv2D), but only **1.33x improvement** for memory-bound workloads (MemCopy). No CPU sophistication can overcome a memory bandwidth bottleneck.

### 2. Cache Threshold Effect
MatMul shows a sharp IPC transition at 32kB L1D cache — miss rate drops from **6.2% → 0.05%** and IPC jumps from **0.59 → 0.68 (TIMING)** and **1.66 → 3.08 (O3)**. Below this threshold the working set thrashes; above it performance plateaus.

### 3. O3 Amplifies Cache Pressure
O3 CPU issues memory requests aggressively — MemCopy L1D miss rate jumps from **1.33% (TIMING) → 64.5% (O3)**, confirming that out-of-order execution amplifies memory pressure on bandwidth-bound workloads.

### 4. Bandwidth Thief Effect (Multi-Program Contention)
In shared multi-core systems, memory-bound workloads act as silent bandwidth thieves — they suffer no contention themselves but degrade compute-bound neighbors by up to **11.6%** under O3 execution. This effect is invisible with simple in-order cores (< 1.2% degradation).

## Workloads

| Workload | Type | Description |
|---|---|---|
| MatMul | Compute-bound | 64×64 integer matrix multiplication |
| MemCopy | Memory-bound | 4MB streaming memory copy |
| Conv2D | Mixed (AI proxy) | 8-filter 2D convolution — models DNN inference |

## Experiments

| Experiment | Config |
|---|---|
| Cache sweep | L1D: 8kB, 16kB, 32kB, 64kB — L2: 256kB fixed |
| CPU comparison | TIMING (in-order) vs O3 (out-of-order) |
| Multi-program contention | All workload combinations on 2–3 cores simultaneously |
| Workload characterization | IPC, CPI, L1D/L2 miss rates, SimTicks |

## Results Summary

### IPC at 32kB L1D Cache — TIMING vs O3

| Workload | TIMING IPC | O3 IPC | Speedup |
|---|---|---|---|
| MatMul | 0.678 | 3.083 | 4.54x |
| Conv2D | 0.611 | 4.190 | 6.86x |
| MemCopy | 0.394 | 0.524 | 1.33x |

### Multi-Program Contention — IPC Degradation vs Solo (O3 CPU)

| Workload | Running With | Solo IPC | Multi IPC | Degradation |
|---|---|---|---|---|
| Conv2D | + MemCopy | 4.190 | 3.797 | -9.37% |
| Conv2D | + MatMul + MemCopy | 4.190 | 3.703 | -11.63% |
| MatMul | + MemCopy | 3.083 | 2.982 | -3.29% |
| MatMul | + Conv + MemCopy | 3.083 | 2.957 | -4.07% |
| MemCopy | + Any | 0.524 | ~0.524 | < 0.1% |

## Plots

### Single-Workload Analysis
| Plot | Description |
|---|---|
| `ipc_timing_vs_o3.png` | IPC vs L1D cache size — TIMING vs O3 per workload |
| `o3_speedup.png` | O3 speedup over TIMING at 32kB L1D |
| `memory_wall.png` | Memory wall effect — O3 cannot fix bandwidth bottleneck |
| `l1d_miss_timing_vs_o3.png` | L1D miss rate — TIMING vs O3 |
| `ipc_vs_l1d.png` | IPC vs cache size (TIMING only) |
| `l1d_miss_vs_size.png` | L1D miss rate vs cache size |
| `l2_miss_vs_size.png` | L2 miss rate vs L1D cache size |
| `workload_comparison.png` | Workload comparison at 32kB baseline |

### Multi-Program Contention Analysis
| Plot | Description |
|---|---|
| `contention_degradation.png` | IPC degradation per workload combo (O3) |
| `conv_contention_scaling.png` | Conv2D IPC degradation under increasing contention |
| `bandwidth_thief.png` | Solo vs 3-core IPC comparison |

## Project Structure

```
gem5-riscv-perf/
├── gem5/                    # gem5 simulator (cloned, not committed)
├── workloads/               # C benchmark sources + RISC-V binaries
│   ├── matmul.c
│   ├── memcopy.c
│   └── conv_layer.c
├── configs/                 # gem5 Python configuration scripts
│   ├── multicore_riscv.py   # Single-program config (TIMING/O3)
│   └── multiprogram_riscv.py # Multi-program contention config
├── scripts/                 # Experiment automation
│   ├── run_experiment.py    # Single-program runner
│   ├── run_multi.py         # Multi-program runner
│   ├── parse_stats.py       # Single-program stats parser
│   ├── parse_multi_stats.py # Multi-program contention parser
│   ├── plot_results.py      # Cache sweep + TIMING/O3 plots
│   └── plot_contention.py   # Contention analysis plots
├── results/                 # gem5 stats output (per experiment)
│   └── summary.csv
└── plots/                   # Generated performance plots
```

## Setup & Usage

### Prerequisites
- Ubuntu 22.04 / 24.04 (or WSL2)
- Python 3.10+ with: `pip install matplotlib numpy pandas seaborn`
- RISC-V cross-compiler: `sudo apt install gcc-riscv64-linux-gnu`
- gem5 build dependencies:
```bash
sudo apt install build-essential git m4 scons zlib1g zlib1g-dev \
  libprotobuf-dev protobuf-compiler libprotoc-dev \
  libgoogle-perftools-dev python3-dev libboost-all-dev pkg-config cmake
```

### Build gem5
```bash
cd gem5
scons build/RISCV/gem5.opt -j$(nproc)
```

### Compile Workloads
```bash
cd workloads
riscv64-linux-gnu-gcc -O2 -static -o matmul matmul.c
riscv64-linux-gnu-gcc -O2 -static -o memcopy memcopy.c
riscv64-linux-gnu-gcc -O2 -static -o conv_layer conv_layer.c
```

### Run Single-Program Experiments
```bash
# Syntax: python scripts/run_experiment.py <workload> [cores] [l1d] [l2] [cpu]
python scripts/run_experiment.py matmul 1 32kB 256kB timing
python scripts/run_experiment.py matmul 1 32kB 256kB o3
python scripts/run_experiment.py memcopy 1 8kB 256kB timing
python scripts/run_experiment.py conv 1 64kB 256kB o3
```

### Run Multi-Program Contention Experiments
```bash
# Syntax: python scripts/run_multi.py <w1,w2,...> [l1d] [l2] [cpu]
python scripts/run_multi.py matmul,memcopy 32kB 256kB timing
python scripts/run_multi.py conv,memcopy 32kB 256kB o3
python scripts/run_multi.py matmul,conv,memcopy 32kB 256kB o3
```

### Parse Results & Generate Plots
```bash
# Single-program analysis
python scripts/parse_stats.py
python scripts/plot_results.py

# Multi-program contention analysis
python scripts/parse_multi_stats.py
python scripts/plot_contention.py
```

## Tools & Environment
- **Simulator:** gem5 v25.1 (RISC-V ISA, SE mode)
- **CPU Models:** TimingSimpleCPU (in-order), O3CPU (out-of-order, 8-wide issue)
- **Cache:** Private L1 I/D + Private L2 per core
- **Memory:** Single-channel DDR4-2400, 2GiB
- **Cross-compiler:** riscv64-linux-gnu-gcc 11.4.0
- **OS:** Ubuntu 24.04 (WSL2)

## Author
Amit Chaudhari — M.Tech Electrical Engineering, IIT Bombay (2025)
Independent project — May 2026
[LinkedIn](https://linkedin.com/in/Amit-chaudhari) | [GitHub](https://github.com/AmitDragon-India)
