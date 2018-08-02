import argparse
from myhdl import *
from math import atan2, pi


@block
def cordic_gen(clk, rst, phase, start, sinout, done, phasebits, stages):

    phases = [atan2(1, 2**i) for i in range(stages)]
    phases = tuple([int(x * (4.0 * (1<<(phasebits-2)))/(2.0*pi)) for x in phases])
    # No floats in FPGA land. Keeping the old floats in case I can create comments
    # from them in future for generated VHDL
    # 360/45 = 8 so if we want to split into 45 degree blocks only need 3 bits
    # to represent a block 

    x = [Signal(intbv(0)[phasebits+1:]) for i in range(stages)]
    y = [Signal(intbv(0)[phasebits+1:]) for i in range(stages)]
    p = [Signal(intbv(0)[phasebits+1:]) for i in range(stages)]
    phase_top = phase[phasebits:phasebits-3]


    @always(clk.posedge)
    def update():
        if rst == 1:
            y[0] = 0
            x[0] = 0
            p[0] = 0
        elif start == 1:
            if phase[0:3] == 0:
                x[0] = 1
                y[0] = 4
                p[0] = phase<<1
            elif phase[0:3] == 1:
                x[0] = 1
                y[0] = 4
                p[0] = (phase-0x10000) <<1
            elif phase[0:3] == 2:
                x[0] = 1
                y[0] = 4
                p[0] = (phase-0x10000)<<1
            elif phase[0:3] == 3:
                x[0] = 1
                y[0] = 4
                p[0] = (phase-0x20000)<<1
            elif phase[0:3] == 4:
                x[0] = 1
                y[0] = 4
                p[0] = (phase-0x20000)<<1
            elif phase[0:3] == 5:
                x[0] = 1
                y[0] = 4
                p[0] = (phase-0x30000)<<1
            elif phase[0:3] == 6:
                x[0] = 1
                y[0] = 4
                p[0] = (phase-0x30000)<<1
            elif phase[0:3] == 7:
                y[0] = 1
                x[0] = 1
                p[0] = phase<<1
            done.next = False
        else:
            for s in range(stages):
                x[s] = x[s-1] + (y[s-1]>>s) 
                y[s] = y[s-1] - (x[s-1]>>s)
                temp_phase = phases[s-1]
                p[s] = p[s-1] + temp_phase

            done.next=True
        sinout.next = y[-1]
        

    return update



parser = argparse.ArgumentParser()
parser.add_argument('--stages', '-s', help='Number of stages in the CORDIC processor', type=int, default = 8)
parser.add_argument('--phasebits', '-p', help='Number of bits used to store phase values', type=int, default = 15)
parser.add_argument('--out-width', '-ow', help='Output width', type=int, default=5)
parser.add_argument('--in-width', '-iw', help='Input data width', type=int, default=3)
parser.add_argument('--out', '-o', help='Output filename', type=str, default='CORDIC.vhd')

args = parser.parse_args()

print(args)

clk = Signal(bool(0))
rst = ResetSignal(0, active=0, async=True)
start = Signal(bool(0))
done = Signal(bool(0))
phase = Signal(intbv(0)[args.phasebits:])
sinout = Signal(intbv(0)[args.phasebits:])

concrete_cordic = cordic_gen(clk, rst, phase, start, sinout, done, args.phasebits, args.stages)
concrete_cordic.convert(hdl='VHDL')
