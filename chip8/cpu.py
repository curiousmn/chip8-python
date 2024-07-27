from memory import Memory
from display import Screen
from keyboard import Keyboard
from random import randint
import logging

class CPU:
    def __init__(self):
        self.V = bytearray(16)
        self.I = 0
        self.PC = 0x200
        self.stack = [0] * 16
        self.SP = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.memory = Memory()
        self.screen = Screen(64, 32)
        self.keyboard = Keyboard()
        self.cycle_count = 0
        self.max_cycles = 1000000  # Prevent infinite loops
        self.start_counter = 0

    def push_to_stack(self, value: int) -> None:
        if self.SP < 16:
            self.stack[self.SP] = value
        else:
            raise OverflowError("Stack overflow")
    def pop_from_stack(self) -> None:
        if self.SP > 0:
            self.SP -= 1
            return self.stack[self.SP]
        else:
            raise IndexError("Stack underflow")

    def fetch(self) -> int:
        """ Get the byte at the memory address pointed by PC then shift 8 bit to make some room for other 8 bit, increase the PC by 1 then read the memory address,
            combine both of them with OR
        """
        opcode = (self.memory.read(self.PC) << 8) | self.memory.read(self.PC + 1)
        self.PC += 2
        return opcode

    def update_timers(self) -> None:
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def decode_and_execute(self, opcode: int) -> callable:

        ins = (opcode & 0xF000) >> 12
        X = (opcode & 0x0F00) >> 8
        Y = (opcode & 0x00F0) >> 4
        NNN = opcode & 0x0FFF
        NN = opcode & 0x00FF
        N = opcode & 0x000F
        logging.debug(f"Decoding opcode {opcode:04X}: ins={ins:X}, X={X:X}, Y={Y:X}, NNN={NNN:03X}, NN={NN:02X}, N={N:X}")

        if ins == 0x0:
            if NN == 0xE0:
                self.clear_display()
            elif NN == 0xEE:
                self.return_from_subroutine()
        elif ins == 0x1:
            self.jump(NNN)
        elif ins == 0x2:
            self.call_subroutine(NNN)
        elif ins == 0x3:
            self.skip_if_equal(X, NN)
        elif ins == 0x4:
            self.skip_if_not_equal(X, NN)
        elif ins == 0x5 and N == 0x0:
            self.skip_if_register_equal(X, Y)
        elif ins == 0x6:
            self.set_register(X, NN)
        elif ins == 0x7:
            self.add_register(X, NN)
        elif ins == 0x8:
            instruction_table = {
                    0x0: lambda: self.set_x_y(X, Y),
                    0x1: lambda: self.x_or_y(X, Y),
                    0x2: lambda: self.x_and_y(X, Y),
                    0x3: lambda: self.x_xor_y(X, Y),
                    0x4: lambda: self.add_x_y(X,Y),
                    0x5: lambda :self.sub_x_y(X, Y),
                    0x6: lambda: self.shr_x(X),
                    0x7: lambda: self.subn_x_y(X, Y),
                    0xE: lambda: self.shl_x(X)
            }
            if N in instruction_table:
                instruction_table[N]()
            else:
                raise ValueError(f"Unknown 0x8 instruction: {opcode: X}")
        elif ins  == 0x9 and N == 0x0:
            self.skip_if_registers_not_equal(X, Y)
        elif ins == 0xA:
            self.set_I(NNN)
        elif ins == 0xB:
            self.jump_to_nnn(NNN)
        elif ins == 0xC:
            self.set_x_random(NN, X)
        elif ins == 0xD:
            self.draw_sprite(X, Y, N)
        elif ins == 0xE:
            if N == 0xE:
                self.skip_if_pressed(X)
            elif N == 0x1:
                self.skip_if_not_pressed(X)
        elif ins == 0xF:
            if NN == 0x07:
                self.set_x_to_dt(X)
            elif NN == 0x0A:
                self.wait_for_key_press(X)
            elif NN == 0x15:
                self.set_dt_to_x(X)
            elif NN == 0x18:
                self.set_st_to_x(X)
            elif NN == 0x1E:
                self.add_I_x(X)
            elif NN == 0x29:
                self.set_I_to_sprite(X)
            elif NN == 0x33:
                self.store_bcd(X)
            elif NN == 0x55:
                self.store_registers(X)
            elif NN == 0x65:
                self.load_registers(X)
        else:
            logging.warning(f"Unknown opcode: {opcode:X}")

    def cycle(self) -> None:
        self.cycle_count += 1
        if self.cycle_count > self.max_cycles:

            raise Exception("Maximum cycle count exceeded. Possible infinite loop.")

        opcode = self.fetch()
        print(f"Opcode executing: {opcode}")
        self.decode_and_execute(opcode)
        self.keyboard.update()
        self.update_timers()

    def clear_display(self) -> None:
        """Clear the entire display."""
        for y in range(self.screen.height):
            for x in range(self.screen.width):
                self.screen.set_pixel(x, y, False)

    def return_from_subroutine(self) -> None:
        if self.SP > 0:
            self.PC = self.pop_from_stack()


    def jump(self, NNN: int) -> None:
        self.PC = NNN
    def call_subroutine(self, NNN: int) -> None:
        if self.SP < 16:  # Ensure we don't overflow the stack
           self.push_to_stack(self.PC)
           self.PC = NNN & 0x0FFF  # Ensure address is within valid range
           self.last_op = f"CALL {self.PC:04X}"  # For debugging
        else:
           raise OverflowError("Stack overflow")

    def skip_if_equal(self, X: int, NN: int) -> None:
        if self.V[X] == NN:
            self.PC += 2

    def skip_if_not_equal(self, X: int, NN: int) -> None:
        if self.V[X] != NN:
            self.PC += 2

    def skip_if_register_equal(self, X: int, Y: int) -> None:
        if self.V[X] == self.V[Y]:
            self.PC += 2

    def set_register(self, X: int, NN: int) -> None:
        self.V[X] = NN

    def add_register(self, X: int, NN: int) -> None:
        self.V[X] = (self.V[X] + NN) & 0xFF

    def set_x_y(self, X: int, Y: int) -> None:
        self.V[X] = self.V[Y]

    def x_or_y(self, X: int, Y: int) -> None:
        self.V[X] = self.V[X] | self.V[Y]

    def x_and_y(self, X: int, Y: int) -> None:
        self.V[X] = self.V[X] & self.V[Y]

    def x_xor_y(self, X: int, Y: int) -> None:
        self.V[X] = self.V[X] ^ self.V[Y]

    def add_x_y(self, X: int, Y: int) -> None:
        res = self.V[X] + self.V[Y]
        self.V[0xF] = 1 if res > 0xFF else 0
        self.V[X] = res & 0xFF

    def sub_x_y(self, X: int, Y: int) -> None:
        self.V[0xF] = 1 if self.V[X] > self.V[Y] else 0
        self.V[X] = (self.V[X] - self.V[Y]) & 0xFF

    def shr_x(self, X: int) -> None:
        self.V[0xF] = 1 if (self.V[X] & 1) == 1 else 0
        self.V[X] >>= 1

    def subn_x_y(self, X: int, Y: int) -> None:
        self.V[0xF] = 1 if self.V[Y] > self.V[X] else 0
        self.V[X] =  (self.V[X] - self.V[Y]) & 0xFF

    def shl_x(self, X: int) -> None:
        self.V[0xF] = (self.V[X] & 0x80) >> 7
        self.V[X] = (self.V[X] << 1) & 0xFF

    def skip_if_registers_not_equal(self, X: int, Y: int) -> None:
        if self.V[X] != self.V[Y]:
            self.PC += 2

    def set_I(self, NNN: int) -> None:
        self.I = NNN

    def jump_to_nnn(self, NNN: int) -> None:
        self.PC = NNN + self.V[0x0]

    def set_x_random(self, NN: int, X: int) -> None:
        self.V[X] = randint(0, 255) & NN

    def draw_sprite(self, X: int, Y: int, N: int) -> None:
        read_address = self.I
        self.V[0xF] = 0
        for row in range(N):
            sprite_byte = self.memory.read(read_address + row)
            for bit in range(8):
                x = ((self.V[X] + bit) % self.screen.width)
                y = ((self.V[Y] + row) % self.screen.height)
                if (sprite_byte & (0x80 >> bit)) != 0:
                    curr_pixel = self.screen.get_pixel(x, y)
                    new_pixel = not curr_pixel
                    self.screen.set_pixel(x, y, new_pixel)
                    if curr_pixel and not new_pixel:
                        self.V[0xF] = 1

    def skip_if_pressed(self, X: int) -> None:
        key = self.V[X]
        if self.keyboard.is_key_pressed(key):
            self.PC += 2

    def skip_if_not_pressed(self, X: int) -> None:
        key = self.V[X]
        if not self.keyboard.is_key_pressed(key):
            self.PC += 2

    def set_x_to_dt(self, X: int) -> None:
        self.V[X] = self.dt

    def wait_for_key_press(self, X: int) -> None:
        key = self.keyboard.wait_for_key_press()
        self.V[X] = key

    def set_dt_to_x(self, X: int) -> None:
        self.dt = self.V[X]

    def set_st_to_x(self, X: int) -> None:
        self.st = self.V[X]

    def add_I_x(self, X: int) -> None:
        self.I = (self.I + self.V[X]) & 0xFFFF

    def set_I_to_sprite(self, X: int) -> None:
        self.I = self.V[X] * 5

    def store_bcd(self, X: int) -> None:
        value = self.V[X]
        self.memory.write(self.I, value // 100)
        self.memory.write(self.I + 1, (value % 100) // 10)
        self.memory.write(self.I + 2, value % 10)

    def store_registers(self, X: int) -> None:
        for i in range(X + 1):
           self.memory.write(self.I + i, self.V[i])

    def load_registers(self, X: int) -> None:
        for i in range(X + 1):
           self.V[i] = self.memory.read(self.I + i)
