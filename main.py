import sys
import os
sys.path.append(os.path.abspath('chip8/'))
from emulator import Emulator

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python emulator.py <path_to_rom>")
        sys.exit(1)

    rom_path = sys.argv[1]
    try:
        emulator = Emulator(rom_path)
        emulator.run()
    except Exception as e:
        logging.error(f"Emulator crashed: {str(e)}")
