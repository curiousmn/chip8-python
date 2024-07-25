import pygame as pg


class Keyboard:

    def __init__(self):
        pg.init()
        self.key_map = {
            pg.K_1: 0x1, pg.K_2: 0x2, pg.K_3: 0x3, pg.K_4: 0xC,
            pg.K_q: 0x4, pg.K_w: 0x5, pg.K_e: 0x6, pg.K_r: 0xD,
            pg.K_a: 0x7, pg.K_s: 0x8, pg.K_d: 0x9, pg.K_f: 0xE,
            pg.K_z: 0xA, pg.K_x: 0x0, pg.K_c: 0xB, pg.K_v: 0xF
    }
        self.keys = [0] * 16

    def update(self) -> None:
        for event in pg.event.get([pg.KEYDOWN, pg.KEYUP]):
            if event.key in self.key_map:
                chip8_key = self.key_map[event.key]
                self.keys[chip8_key] = event.type == pg.KEYDOWN

    def is_key_pressed(self, key: int) -> bool:
        return self.keys[key] if 0 <= key <= 16 else False

    def wait_for_key_press(self) -> int:
        key_pressed = None
        while key_pressed is None:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    raise SystemExit
                if event.type == pg.KEYDOWN:
                    if event.key in self.key_map:
                        key_pressed = self.key_map[event.key]
            pg.time.wait(10)
        return key_pressed


