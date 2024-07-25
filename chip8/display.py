class Screen:

    def __init__(self, W, H):
        self.width = W
        self.height = H
        self.screen = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def set_pixel(self, x: int, y: int, value: bool) -> None:
        x %= self.width
        y %= self.height
        self.screen[y][x] = value

    def get_pixel(self, x: int, y: int) -> bool:
        x %= self.width
        y %= self.height
        return self.screen[y][x]

    def get_screen(self) -> list[list[bool]]:
        return self.screen

