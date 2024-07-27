import pygame
from cpu import CPU
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Emulator:
    def __init__(self, rom_path):
        try:
            self.cpu = CPU()
            self.cpu.memory.load_rom(rom_path)
            logging.info(f"ROM loaded successfully from {rom_path}")

            pygame.init()
            self.scale_factor = 15
            self.window = pygame.display.set_mode((64 * self.scale_factor, 32 * self.scale_factor))
            pygame.display.set_caption("CHIP-8 Emulator")

            self.clock = pygame.time.Clock()
            self.screen_surface = pygame.Surface((64, 32))
        except Exception as e:
            logging.error(f"Error during initialization: {str(e)}")
            raise

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.cpu.cycle()

            self.update_display()
            self.cpu.update_timers()
            self.cpu.keyboard.update()

            self.clock.tick(120)


    def update_display(self):
        try:
            current_screen_state = self.cpu.screen.get_screen()
            self.screen_surface.fill((0, 0, 0))
            for y in range(32):
                for x in range(64):
                    if current_screen_state[y][x]:
                        self.screen_surface.set_at((x, y), (255, 255, 255))

            pygame.transform.scale(self.screen_surface, self.window.get_size(), self.window)
            pygame.display.flip()
        except Exception as e:
            logging.error(f"Error updating display: {str(e)}")
            raise


