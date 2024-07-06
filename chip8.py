import random


class Chip8:
    def __init__(self):
        self.memory = bytearray(4096)
        self.V = bytearray(16)
        self.I = 0
        self.pc = 0x200
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16
        self.display = [[0 for _ in range(64)] for  _ in range(32)]
        self.opcode = 0
        self.draw_flag = False

        self.fontset = [
                0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
                0x20, 0x60, 0x20, 0x20, 0x70, # 1
                0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
                0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
                0x90, 0x90, 0xF0, 0x10, 0x10, # 4
                0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
                0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
                0xF0, 0x10, 0x20, 0x40, 0x40, # 7
                0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
                0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
                0xF0, 0x90, 0xF0, 0x90, 0x90, # A
                0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
                0xF0, 0x80, 0x80, 0x80, 0xF0, # C
                0xE0, 0x90, 0x90, 0x90, 0xE0, # D
                0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
                0xF0, 0x80, 0xF0, 0x80, 0x80  # F
                ]

        for i, byte in enumerate(self.fontset):
            self.memory[i] = byte

    def emulate_cycle(self):
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.execute_opcode()


        if self.delay_timer > 0:
            self.delay_timer -= 1
        elif self.sound_timer> 0:
            self.sound_timer -= 1

    def execute_opcode(self):
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        nnn = self.opcode & 0x0FFF
        nn = self.opcode & 0x00FF
        n = self.opcode & 0x000F

        if self.opcode & 0xF000 == 0x0000:
            if self.opcode == 0x00E0:
                self.display = [[0 for _ in range(64)] for _ in range(32)]
                self.draw_flag = False
                self.pc += 2
        elif self.opcode & 0xF000 == 0x1000:
            self.pc = nnn
        elif self.opcode & 0xF000 == 0x2000:
            self.pc = nnn
        elif self.opcode & 0xF000 == 0x3000:
            if self.V[x] == nn:
                self.pc += 4
            else:
                self.pc += 2
        elif self.opcode & 0xF000 == 0x4000:
            if self.V[x] != nn:
                self.pc += 4
            else:
                self.pc += 2
        elif self.opcode & 0xF000 == 0x5000:
            if self.V[x] == self.V[y]:
                self.pc += 4
            else:
                self.pc += 2
        elif self.opcode & 0xF000 == 0x6000:
            self.V[x] = nn
            self.pc += 2
        elif self.opcode & 0XF000 == 0x7000:
            self.V[x] = (self.V[x] + nn) & 0xFF
            self.pc += 2
        elif self.opcode & 0xF000 == 0x8000:
            if n == 0x0:
                self.V[x] = self.V[y]
            elif n == 0x1:
                self.V[x] |= self.V[y]
            elif n == 0x2:
                self.V[x] &= self.V[y]
            elif n == 0x3:
                self.V[x] ^= self.V[y]
            elif n == 0x4:
                sumOf = self.V[x] + self.V[y]
                if sumOf > 0xFF:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[x] =  sumOf & 0xFF
            elif n == 0x5:
                if self.V[x] > self.V[y]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[x] = (self.V[x] - selfV[y]) & 0XFF
            elif n == 0x6:
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif n == 0x7:
                if self.V[y] > self.V[x]:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
            self.pc += 2
        elif self.opcode & 0xF000 == 9000:
            if self.V[x] != self.V[y]:
                self.pc += 4
            else:
                self.pc += 2
        elif self.opcode & 0xF000 == 0xA000:
            self.I = nnn
            self.pc += 2
        elif self.opcode & 0xF000 == 0xB000:
            self.pc = nnn + self.V[0]
        elif self.opcode & 0xF000 == 0xC000:
            self.V[x] = random.randint(0, 255) & nn
            self.pc += 2
        elif self.opcode & 0xF000 == 0xD000:
            self.V[0xF] = 0
            for y_line in range(n):
                pxl = self.memory[self.I + y_line]
                for x_line in range(8):
                    if (pxl & (0x80 >> x_line)) != 0:
                        if self.display[self.V[y] + y_line][self.V[x] + x_line] == 1:
                            self.V[0xF] = 1
                        self.display[self.V[y]+ y_line][self.V[x] + x_line] ^= 1
            self.draw_flag = True
            self.pc += 2
        elif self.opcode & 0xF000 == 0xE000:
            if nn == 0x9E:
                if self.keypad[self.V[x]]:
                    self.pc += 4
                else:
                    self.pc += 2
            elif nn == 0xA1:
                if not self.keypad[self.V[x]]:
                    self.pc += 4
                else:
                    self.pc += 2
        elif self.opcode & 0xF000 == 0xF000:
            if nn == 0x07:
                self.V[x] = self.delay_timer
            elif nn == 0x0A:
                key_pressed = False
                for i in range(16):
                    if self.keypad[i]:
                        self.V[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    return
            elif nn == 0x15:
                self.delay_timer = self.V[x]
            elif nn == 0x18:
                self.sound_timer = self.V[x]
            elif nn == 0x1E:
                self.I += self.V[x]
                if self.I > 0xFFF:
                    self.V[0xF]  = 1
                else:
                    self.V[0xF] = 0
            elif nn == 0x29:
                self.I = self.V[x] * 5
            elif nn == 0x33:
                self.memory[self.I] = self.V[x] // 100
                self.memory[self.I + 1] = (self.V[x] % 100) // 100
                self.memory[self.I + 2] = (self.V[x] % 10)
            elif nn == 0x55:
                for i in range(x+1):
                    self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:
                for i in range(x+1):
                    self.V[i] = self.memory[self.I + i]
            self.pc += 2
        else:
            print(f"Unknown opcode: {self.opcode:X}")
            self.pc += 2

    def load_rom(self, filename):
        with open(filename, 'rb') as f:
            rom_data = f.read()
            for i, byte  in enumerate(rom_data):
                self.memory[0x200 + i] = byte
