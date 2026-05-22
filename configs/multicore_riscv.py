"""
Multi-Core RISC-V Performance Analysis Configuration
Supports TIMING and O3 CPU models
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

parser = argparse.ArgumentParser(description="Multi-Core RISC-V Performance Sim")
parser.add_argument("--num-cores", type=int,  default=1,       help="Number of cores")
parser.add_argument("--l1d-size",  type=str,  default="32kB",  help="L1 Data cache size")
parser.add_argument("--l1i-size",  type=str,  default="32kB",  help="L1 Inst cache size")
parser.add_argument("--l2-size",   type=str,  default="256kB", help="L2 cache size")
parser.add_argument("--cmd",       type=str,  required=True,   help="Binary to simulate")
parser.add_argument("--cpu-type",  type=str,  default="TIMING",help="CPU type: TIMING or O3")
args = parser.parse_args()

# CPU type selection
cpu_map = {
    "TIMING": CPUTypes.TIMING,
    "O3":     CPUTypes.O3,
}
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
    num_cores=args.num_cores,
)

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_se_binary_workload(BinaryResource(args.cmd))

simulator = Simulator(board=board)
print(f"\n=== {args.cpu_type} | {args.cmd} | Cores: {args.num_cores} | L1D: {args.l1d_size} | L2: {args.l2_size} ===\n")
simulator.run()
print(f"\n=== Simulation Complete ===")
