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
        try:
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                try:
                    for _ in range(10):
                        self.cpu.cycle()
                except Exception as e:
                    logging.error(f"Error during CPU cycle: {str(e)}")
                    raise

                self.update_display()
                self.cpu.update_timers()
                self.cpu.keyboard.update()

                self.clock.tick(60)

        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
        finally:
            pygame.quit()

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


