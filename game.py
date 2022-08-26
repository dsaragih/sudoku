try:
    import random
    import math
    import pygame
    import sys
    import time
    import numpy as np
    from typing import Tuple
    from pygame.locals import *
except ImportError as err:
    print ("couldn't load module. %s" % (err))
    sys.exit(2)


class Grid:
    """Grid on which the game is played"""
    width: int
    height: int
    square_width: int
    matrix: np.array
    selected_square: Tuple[int, int]

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.square_width = width // 9
        self.matrix = np.zeros((9, 9), dtype=np.intp)
        self.selected_square = None

    def _row_safe(self, row: int, n: int) -> bool:
        for i in range(9):
            if self.matrix[row, i] == n:
                return False
        return True

    def _col_safe(self, col: int, n: int) -> bool:
        for i in range(9):
            if self.matrix[i, col] == n:
                return False
        return True

    def _sub_grid_safe(self, row: int, col: int, n: int) -> bool:
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if self.matrix[start_row + i, start_col + j] == n:
                    return False
        return True
    
    def _input_safe(self, row: int, col: int, n: int) -> bool:
        """Checks whether {n} is a valid number to be placed in
        self.matrix[row, col].
        """
        return self._row_safe(row, n) and self._col_safe(col, n) and \
            self._sub_grid_safe(row, col, n)

    def _find_empty(self) -> Tuple[int, int]:
        """Finds the next empty square"""
        for i in range(9):
            for j in range(9):
                if self.matrix[i, j] == 0:
                    return (i, j)
    
    def clear(self) -> None:
        """Clears the grid."""
        self.matrix = np.zeros((9, 9), dtype=np.intp)

    def solve(self) -> bool:
        """Backtracks to find the solution to the Sudoku."""
        empty_square = self._find_empty()
        if not empty_square:
            return True

        row = empty_square[0]
        col = empty_square[1]
        for i in random.sample(range(1, 10), 9):
            if self._input_safe(row, col, i):
                self.matrix[row, col] = i

                if self.solve():
                    return True
                self.matrix[row, col] = 0
        return False

    def set_selected_square(self, pos: Tuple[float, float]) -> None:
        """Updates the selected square according to where the player clicked."""
        x = math.floor(pos[0] / self.square_width) * self.square_width
        y = math.floor(pos[1] / self.square_width) * self.square_width
        self.selected_square = (x, y)

    def highlight_square(self, screen: pygame.display) -> None:
        """Fills in the selected square with a light blue color."""
        if not self.selected_square: return

        x, y = self.selected_square
        background = pygame.Surface((self.square_width - 2, self.square_width - 2))
        background.convert()
        background.fill((204, 255, 255))
        
        # Small adjustment to ensure the fill fits inside the square
        screen.blit(background, (x + 1, y + 1))

    def update_selected_square(self, input: int) -> None:
        """Updates the number on the selected square."""
        col, row = self.selected_square
        row //= self.square_width
        col //= self.square_width

        if self._input_safe(row, col, input): self.matrix[row, col] = input


    def draw(self, screen: pygame.display) -> None:
        """Draws everything on the grid."""

        for div in range(3 * self.square_width, self.width, 3 * self.square_width):
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(div, 0, 2, self.height))
        for div in range(3 * self.square_width, self.height, 3 * self.square_width):
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, div, self.width, 2))
        for div in range(self.square_width, self.width, self.square_width):
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(div, 0, 1, self.height))
        for div in range(self.square_width, self.height, self.square_width):
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, div, self.width, 1))

        
        self.highlight_square(screen)
        
        NUMBER_FONT = pygame.font.SysFont("Arial", 30)
        SCORE_FONT = pygame.font.SysFont("Arial", 100)

        # Displays the integers on self.matrix
        for y in range(9):
            for x in range(9):
                if self.matrix[y, x] != 0:
                    number_text = NUMBER_FONT.render(str(self.matrix[y, x]), 1, (0, 0, 0))
                    font_x = (self.square_width - number_text.get_width())//2 + self.square_width*x
                    font_y = (self.square_width - number_text.get_height())//2 + self.square_width*y
                    screen.blit(number_text, (font_x, font_y))
        


def main() -> None:
    # Initialize the screen
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    pygame.display.set_caption('Sudoku')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    # Initialize the grid
    grid = Grid(640, 640)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    grid.draw(screen)
    pygame.display.flip()

    clock = pygame.time.Clock()

    # Event loop
    while 1:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                grid.set_selected_square(pos)

            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    grid.update_selected_square(0)
                if event.unicode.isnumeric():
                    grid.update_selected_square(int(event.unicode))
                if event.key == K_SPACE:
                    grid.solve()
                if event.key == K_r:
                    grid.clear()

        screen.blit(background, (0, 0))
        grid.draw(screen)
        pygame.display.flip()



if __name__ == '__main__': main()