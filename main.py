import pygame
import sys
from chip8 import Chip8

if __name__ == "__main__":
	pygame.init()
	w, h = 640, 320
	screen = pygame.display.set_mode((w, h))

	BLACK = (0, 0, 0)
	WHITE= (255, 255, 255)

	chip8 = Chip8()

	rom_path = "caveexplorer.ch8"
	chip8.load_rom(rom_path)

	clock = pygame.time.Clock()

	pygame.mixer.init()
	#beep = pygame.mixer.Sound("path/to/beep.wav")

	running = True

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
		keys = pygame.key.get_pressed()
		chip8.keypad = [
			   keys[pygame.K_x], keys[pygame.K_1], keys[pygame.K_2], keys[pygame.K_3],
			   keys[pygame.K_q], keys[pygame.K_w], keys[pygame.K_e], keys[pygame.K_a],
			   keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_z], keys[pygame.K_c],
			   keys[pygame.K_4], keys[pygame.K_r], keys[pygame.K_f], keys[pygame.K_v]
			   ]
		chip8.emulate_cycle()

		if chip8.delay_timer > 0:
			chip8.delay_timer -= 1

		if chip8.sound_timer> 0:
			chip8.sound_timer-= 1
		#	beep.play()
		#else:
		#	beep.stop()

		if chip8.draw_flag:
			screen.fill(BLACK)
			for y in range(32):
				for x in range(64):
					if chip8.display[y][x]:
						pygame.draw.rect(screen, WHITE, (x * 10, y * 10, 10, 10))
			pygame.display.flip()
			chip8.draw_flag = False

		clock.tick(60)

	pygame.quit()
	sys.exit()





