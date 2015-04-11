import sys, cpu

ROM = sys.argv[1]

def main():
    emulator = cpu.CPU(640, 320)
    emulator.initialize()
    emulator.load_rom(ROM)
    while True:
        emulator.emulate_cycle()

main()
