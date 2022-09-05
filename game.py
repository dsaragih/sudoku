try:
    import random
    import math
    import pygame
    import sys
    import copy
    import numpy as np
    from typing import Tuple, List, Dict
    from pygame.locals import *
except ImportError as err:
    print("couldn't load module. %s" % (err))
    sys.exit(2)


class Grid:
    """Grid on which the game is played"""
    width: int
    height: int
    square_width: int
    matrix: np.array
    penciled_squares: Dict[Tuple[int, int], List[int]]
    screen: pygame.display
    is_solved: bool
    to_be_highlighted: List[Tuple[int, int]]
    selected_square: Tuple[int, int]
    solution: np.array

    def __init__(self, width: int, height: int, screen: pygame.display) -> None:
        self.width = width
        self.height = height
        self.square_width = width // 9
        self.matrix = np.zeros((9, 9), dtype=np.intp)
        self.screen = screen
        self.penciled_squares = {}
        self.is_solved = False
        self.selected_square = None
        self.to_be_highlighted = None
        self.create_game()
    
    def create_game(self) -> None:
        """Initializes the game with a few numbers on the board."""
        self.solve()
        self.solution = copy.deepcopy(self.matrix)
        for _ in range(3):
            # Swaps rows
            r1, r2 = random.sample(range(3), 2)
            self.matrix[[r1, r2]] = self.matrix[[r2, r1]]
            self.matrix[[r1 + 3, r2 + 3]] = self.matrix[[r2 + 3, r1 + 3]]
            self.matrix[[r1 + 6, r2 + 6]] = self.matrix[[r2 + 6, r1 + 6]]

        for _ in range(3):
            # Swaps columns
            c1, c2 = random.sample(range(3), 2)
            self.matrix[:, [c1, c2]] = self.matrix[:, [c2, c1]]
            self.matrix[:, [c1 + 3, c2 + 3]] = self.matrix[:, [c2 + 3, c1 + 3]]
            self.matrix[:, [c1 + 6, c2 + 6]] = self.matrix[:, [c2 + 6, c1 + 6]]

        for _ in range(30):
            # Removes values while maintaining rotational symmetry.
            x, y = random.choice(range(-4, 5)), random.choice(range(-4, 5))
            self.matrix[x + 4, y + 4] = 0
            self.matrix[4 - x, 4 - y] = 0


    def _find_row_dupes(self, row: int, n: int) -> Tuple[int, int]:
        for i in range(9):
            if self.matrix[row, i] == n:
                return (row, i)

    def _find_col_dupes(self, col: int, n: int) -> Tuple[int, int]:
        for i in range(9):
            if self.matrix[i, col] == n:
                return (i, col)

    def _find_sub_grid_dupes(self, row: int, col: int, n: int) -> Tuple[int, int]:
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if self.matrix[start_row + i, start_col + j] == n:
                    return (start_row + i, start_col + j)

    def _input_safe(self, row: int, col: int, n: int) -> bool:
        """Checks whether {n} is a valid number to be placed in
        self.matrix[row, col].
        """
        return not(self._find_row_dupes(row, n) or self._find_col_dupes(col, n) or \
            self._find_sub_grid_dupes(row, col, n))
    
    def _get_dupes(self, row: int, col: int, n: int) -> List[Tuple[int, int]]:
        """Returns a list of coordinates of the locations of duplicated values."""
        res = [self._find_row_dupes(row, n), self._find_col_dupes(col, n), \
            self._find_sub_grid_dupes(row, col, n)]
        return list(filter(lambda x: x is not None, res))

    def _find_empty(self) -> Tuple[int, int]:
        """Finds the next empty square"""
        for i in range(9):
            for j in range(9):
                if self.matrix[i, j] == 0:
                    return (i, j)

    def reset(self) -> None:
        """Resets the grid."""
        self.matrix = np.zeros((9, 9), dtype=np.intp)
        self.penciled_squares = {}
        self.is_solved = False
        self.selected_square = None
        self.to_be_highlighted = None
        self.create_game()

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

# --------------------------------------------
    def set_selected_square(self, pos: Tuple[float, float]) -> None:
        """Updates the selected square according to where the player clicked."""
        x = math.floor(pos[0] / self.square_width) * self.square_width
        y = math.floor(pos[1] / self.square_width) * self.square_width
        self.selected_square = (x, y)

    def highlight_square(self) -> None:
        """Fills in the selected square with a light blue color."""
        if not self.selected_square:
            return

        x, y = self.selected_square
        background = pygame.Surface(
            (self.square_width - 2, self.square_width - 2))
        background.convert()
        background.fill((204, 255, 255))

        # Small adjustment to ensure the fill fits inside the square
        self.screen.blit(background, (x + 1, y + 1))
    
    def highlight_dupes(self) -> None:
        """Fills in the squares with duplicated values with a light red color."""
        fade = pygame.Surface((self.square_width - 2, self.square_width - 2))
        fade.convert()
        fade.fill((255, 114, 111))
        
        fade.set_alpha(60)
        for (row, col) in self.to_be_highlighted:
            self.screen.blit(fade, (col * self.square_width + 1, row * self.square_width + 1))
    
    def pencil_selected_square(self, input: int) -> None:
        """Adds the pencil inputs to {self.penciled_squares}."""
        if self.is_solved: return

        col, row = self.selected_square
        row //= self.square_width
        col //= self.square_width

        if self.matrix[row, col] != 0: return

        if (row, col) not in self.penciled_squares:
            self.penciled_squares[(row, col)] = [input]
        elif input not in self.penciled_squares[(row, col)]:
            self.penciled_squares[(row, col)].append(input)

    def delete_pencils_on_square(self) -> None:
        """Delete the pencil markings on the square."""
        col, row = self.selected_square
        row //= self.square_width
        col //= self.square_width

        if (row, col) in self.penciled_squares:
            self.penciled_squares[(row, col)].pop()

    def display_pencil_ints(self, row: int, col: int) -> None:
        """Displays the pencil markings."""
        PENCIL_FONT = pygame.font.SysFont("Arial", 10)
        calibrating_text = PENCIL_FONT.render(str(1), 1, (0, 0, 0))
        x0 = (self.square_width - calibrating_text.get_width())//2 + self.square_width \
                * col - 2 * calibrating_text.get_width()
        y0 = (self.square_width - calibrating_text.get_height())//2 + self.square_width \
                * row - 2 * calibrating_text.get_height()

        for int in sorted(self.penciled_squares.get((row, col), [])):
            pencil_text = PENCIL_FONT.render(str(int), 1, (0, 0, 0))
            dx = (int - 1) % 3
            dy = (int - 1) // 3
            font_x = x0 + 2 * dx * calibrating_text.get_width()
            font_y = y0 + 2 * dy * calibrating_text.get_height()
            self.screen.blit(pencil_text, (font_x, font_y))

    def write_selected_square(self, input: int) -> None:
        """Writes the number on the selected square."""
        if self.is_solved: return

        col, row = self.selected_square
        row //= self.square_width
        col //= self.square_width

        if input == 0:
            self.matrix[row, col] = input
            self.to_be_highlighted = None
            self.penciled_squares.pop((row, col), None)
            return

        is_safe = self._input_safe(row, col, input)
        is_in_solution = self.solution[row, col] == input
        if is_in_solution:
            self.matrix[row, col] = input
            self.to_be_highlighted = None
            self.penciled_squares.pop((row, col), None)
        elif is_safe:
            self.to_be_highlighted = [(row, col)]
        else:
            self.to_be_highlighted = self._get_dupes(row, col, input)

    def update_game_state(self) -> None:
        """Updates the game state."""
        self.is_solved = 0 not in self.matrix
        
    def draw(self) -> None:
        """Draws everything on the grid."""
        for div in range(3 * self.square_width, self.width, 3 * self.square_width):
            pygame.draw.rect(self.screen, (0, 0, 0),
                             pygame.Rect(div, 0, 2, self.height))
        for div in range(3 * self.square_width, self.height, 3 * self.square_width):
            pygame.draw.rect(self.screen, (0, 0, 0),
                             pygame.Rect(0, div, self.width, 2))
        for div in range(self.square_width, self.width, self.square_width):
            pygame.draw.rect(self.screen, (0, 0, 0),
                             pygame.Rect(div, 0, 1, self.height))
        for div in range(self.square_width, self.height, self.square_width):
            pygame.draw.rect(self.screen, (0, 0, 0),
                             pygame.Rect(0, div, self.width, 1))

        self.highlight_square()
        if self.to_be_highlighted: self.highlight_dupes()

        NUMBER_FONT = pygame.font.SysFont("Arial", 30)

        # Displays the integers on self.matrix
        for y in range(9):
            for x in range(9):
                self.display_pencil_ints(y, x)
                if self.matrix[y, x] != 0:
                    number_text = NUMBER_FONT.render(
                        str(self.matrix[y, x]), 1, (0, 0, 0))
                    font_x = (self.square_width -
                              number_text.get_width())//2 + self.square_width*x
                    font_y = (self.square_width -
                              number_text.get_height())//2 + self.square_width*y
                    self.screen.blit(number_text, (font_x, font_y))

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
    grid = Grid(640, 640, screen)

    # Initialize mode
    pencil_mode = False

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    grid.draw()
    pygame.display.flip()

    clock = pygame.time.Clock()

    # Event loop
    while 1:
        # Sets the FPS to 60.
        clock.tick(60)
        grid.update_game_state()
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                grid.set_selected_square(pos)

            elif event.type == KEYDOWN:
                if event.key == K_m:
                    pencil_mode = not pencil_mode
                if event.key == K_BACKSPACE:
                    if pencil_mode: grid.delete_pencils_on_square()
                    else: grid.write_selected_square(0)
                if event.unicode.isnumeric() and int(event.unicode) != 0:
                    if pencil_mode: grid.pencil_selected_square(int(event.unicode))
                    else: grid.write_selected_square(int(event.unicode))
                if event.key == K_SPACE:
                    grid.solve()
                if event.key == K_r:
                    grid.reset()

        screen.blit(background, (0, 0))
        grid.draw()
        if grid.is_solved: 
            font = pygame.font.Font(None, 90)
            text = font.render("Solved!", 1, (255, 42, 38))
            textpos = text.get_rect()
            textpos.centerx = background.get_rect().centerx
            textpos.centery = background.get_rect().centery
            screen.blit(text, textpos)

        pygame.display.flip()



if __name__ == '__main__':
    main()
