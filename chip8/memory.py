class Memory:
    def __init__(self):
        self.mem = bytearray(4096)
        self.load_font_set()

    def load_font_set(self):
        # CHIP-8 font set
        font_set = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        # Load font set into memory starting at address 0x50
        for i, byte in enumerate(font_set):
            self.mem[i] = byte

    def read(self, address: int) -> int:
        if 0 <= address < 4096:
            return self.mem[address]
        else:
            raise ValueError(f"Memory access out of bounds: {address}")

    def write(self, address: int, value: int) -> None:
        if 0 <= address < 4096:
            self.mem[address] = value
        else:
            raise ValueError(f"Memory access out of bounds: {address}")

    def load_rom(self, path: str) -> None:
        with open(path, "rb") as f:
            rom_data = f.read()
        if len(rom_data) > 3584:  # 4096 - 512 (0x200)
            raise ValueError(f"ROM too large: {len(rom_data)} bytes")
        for i, byte in enumerate(rom_data):
            self.mem[0x200 + i] = byte
