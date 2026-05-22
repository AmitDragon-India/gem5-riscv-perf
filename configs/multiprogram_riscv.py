"""
Multi-Program RISC-V Performance Analysis
Runs different workloads simultaneously on different cores
Models real-world resource contention
"""

import m5
from m5.objects import *
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource
import argparse

parser = argparse.ArgumentParser(description="Multi-Program RISC-V Contention Sim")
parser.add_argument("--binaries", type=str, required=True,
                    help="Comma-separated binary paths, one per core")
parser.add_argument("--l1d-size", type=str, default="32kB")
parser.add_argument("--l1i-size", type=str, default="32kB")
parser.add_argument("--l2-size",  type=str, default="256kB")
parser.add_argument("--cpu-type", type=str, default="TIMING")
args = parser.parse_args()

# Parse binaries
binary_list = [b.strip() for b in args.binaries.split(",")]
num_cores   = len(binary_list)

cpu_map  = {"TIMING": CPUTypes.TIMING, "O3": CPUTypes.O3}
cpu_type = cpu_map.get(args.cpu_type.upper(), CPUTypes.TIMING)

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size=args.l1d_size,
    l1i_size=args.l1i_size,
    l2_size=args.l2_size,
)

memory    = SingleChannelDDR4_2400(size="2GiB")
processor = SimpleProcessor(
    cpu_type=cpu_type,
    isa=ISA.RISCV,
    num_cores=num_cores,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Set multiple binaries — one per core
board.set_se_multi_binary_workload(
    binaries=[BinaryResource(b) for b in binary_list]
)

simulator = Simulator(board=board)
print(f"\n=== Multi-Program Simulation ===")
for i, b in enumerate(binary_list):
    print(f"  Core {i}: {b.split('/')[-1]}")
print(f"  CPU: {args.cpu_type} | L1D: {args.l1d_size} | L2: {args.l2_size}")
print(f"================================\n")
simulator.run()
print(f"\n=== Simulation Complete ===")
