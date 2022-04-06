import pygame
import sys
from pygame.locals import *
import pygame.freetype
import random
import numpy

ORANGE = (255, 140, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 255, 255)
VIOLET = (138, 43, 226)
YELLOW = (255, 255, 0)
PINK = (205, 50, 120)
GREY = (161, 166, 182)


class Tetromino:

    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.anchor = [0, 0]

    def rotate(self):
        result = [[0 for x in range(len(self.shape))] for y in range(len(self.shape[0]))]
        for i, array in enumerate(self.shape):
            for j, tile in enumerate(array):
                result[j][len(self.shape) - 1 - i] = self.shape[i][j]
        self.shape = result


class I(Tetromino):

    def __init__(self):
        super().__init__([[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], BLUE)


class J(Tetromino):

    def __init__(self):
        super().__init__([[0, 1, 1], [0, 1, 0], [0, 1, 0]], VIOLET)


class L(Tetromino):

    def __init__(self):
        super().__init__([[1, 1, 0], [0, 1, 0], [0, 1, 0]], ORANGE)


class O(Tetromino):

    def __init__(self):
        super().__init__([[1, 1], [1, 1]], YELLOW)


class S(Tetromino):

    def __init__(self):
        super().__init__([[1, 0, 0], [1, 1, 0], [0, 1, 0]], GREEN)


class T(Tetromino):

    def __init__(self):
        super().__init__([[0, 1, 0], [1, 1, 1], [0, 0, 0]], PINK)


class Z(Tetromino):

    def __init__(self):
        super().__init__([[0, 1, 0], [1, 1, 0], [1, 0, 0]], RED)


class Grid:

    def __init__(self):
        self.shape = [[None for x in range(10)] for y in range(20)]
        self.points = 0

    def to_string(self):
        result = [[0 for x in range(10)] for y in range(20)]
        for i, array in enumerate(self.shape):
            for j, tile in enumerate(array):
                if tile is not None:
                    result[i][j] = 1
        print(numpy.matrix(result))

    @staticmethod
    def get_empty_cols(piece_shape):
        for i, col in enumerate(piece_shape[0]):
            for j, tile in enumerate(piece_shape):
                if piece_shape[j][i] == 1:
                    return i

    def rotating_possible(self, piece):
        if len(piece.shape) + piece.anchor[1] > len(self.shape[0]):
            return False
        if len(piece.shape[0]) + piece.anchor[0] > len(self.shape):
            return False

        for i, array in enumerate(piece.shape):
            for j, tile in enumerate(array):
                p = self.shape[j + piece.anchor[0]][(len(piece.shape) - 1 - i) + piece.anchor[1]]

                if piece.shape[i][j] == 1 and p is not None and p is not piece:
                    return False

        rotated_piece = [[0 for x in range(len(piece.shape))] for y in range(len(piece.shape[0]))]
        for i, array in enumerate(piece.shape):
            for j, tile in enumerate(array):
                rotated_piece[j][len(piece.shape) - 1 - i] = piece.shape[i][j]

        difference = self.get_empty_cols(rotated_piece) - self.get_empty_cols(piece.shape)

        if piece.anchor[1] < 0 and abs(piece.anchor[1]) > difference:
            return False

        return True

    def is_placeable_here(self, piece, anchor):
        if anchor[0] + len(piece.shape) > len(self.shape):
            return False
        if anchor[1] + len(piece.shape[0]) > len(self.shape[0]):
            return False

        for i, row in piece.shape:
            for j, num in piece.shape[row]:
                tile = self.shape[i + anchor[0]][j + anchor[1]]
                if piece.shape[i][j] == 1 and tile is not None and tile is not piece:
                    return False

        return True

    def get_lowest_possible_position(self, piece):
        anchor = piece.anchor

        while self.is_placeable_here(piece, anchor):
            anchor[0] = anchor[0] + 1

        return anchor

    def place_piece(self, piece, place):
        piece.anchor = place
        for i, array in enumerate(piece.shape):
            for j, tile in enumerate(array):
                if tile == 1:
                    self.shape[i + place[0]][j + place[1]] = piece

    def has_hit_ground(self, piece):
        for tile in self.shape[-1]:
            if tile is piece:
                return True
        for i, array in enumerate(self.shape[:-1]):
            for j, tile in enumerate(array):
                if tile is piece and self.shape[i + 1][j] is not None and self.shape[i + 1][j] is not piece:
                    return True
        return False

    def clear_piece(self, piece):
        for i, array in enumerate(self.shape):
            for j, tile in enumerate(array):
                if tile is piece:
                    self.shape[i][j] = None

    def check_one_row(self, row):
        for i, tile in enumerate(self.shape[row]):
            if tile is None:
                return False
        return True

    def clear_row(self, row):
        self.points += 100
        for j, tile in enumerate(self.shape[row]):
            self.shape[row][j] = None
        for i, array in reversed(list(enumerate(self.shape[:row + 1]))):
            if i == 0:
                continue
            for j, tile in enumerate(array):
                self.shape[i][j] = self.shape[i - 1][j]
                self.shape[i - 1][j] = None

    def clear_filled_rows(self):
        for i, row in enumerate(self.shape):
            if self.check_one_row(i):
                self.clear_row(i)

    def is_moveable_right(self, piece):
        for i, array in enumerate(self.shape):
            if array[-1] == piece:
                return False
            for j, tile in enumerate(array[:-1]):
                if tile is piece and array[j + 1] is not None and array[j + 1] is not piece:
                    return False
        return True

    def is_moveable_left(self, piece):
        for i, array in enumerate(self.shape):
            if array[0] == piece:
                return False
            for j, tile in enumerate(array[0:]):
                if tile is piece and array[j - 1] is not None and array[j - 1] is not piece:
                    return False
        return True

    def move_piece_down(self, piece):
        if not self.has_hit_ground(piece):
            old_place = piece.anchor
            new_place = [old_place[0] + 1, old_place[1]]
            self.clear_piece(piece)
            self.place_piece(piece, new_place)
            self.points += 1

    def move_piece_left(self, piece):
        if self.is_moveable_left(piece):
            old_place = piece.anchor
            new_place = [old_place[0], old_place[1] - 1]
            self.clear_piece(piece)
            self.place_piece(piece, new_place)

    def move_piece_right(self, piece):
        if self.is_moveable_right(piece):
            old_place = piece.anchor
            new_place = [old_place[0], old_place[1] + 1]
            self.clear_piece(piece)
            self.place_piece(piece, new_place)

    def move_piece_to_ground(self, piece):
        while not self.has_hit_ground(piece):
            self.move_piece_down(piece)


def main():
    moving_piece = generate_piece(GRID)
    fall_ticker = 700
    move_ticker = 100
    end = False
    points = 0
    max_ticker = 500
    MIN_TICKER = 150

    while True:

        draw_grid(GRID)
        pygame.display.flip()

        if fall_ticker == 0:
            if GRID.has_hit_ground(moving_piece):
                GRID.clear_filled_rows()
                moving_piece = generate_piece(GRID)
                if max_ticker > MIN_TICKER:
                    max_ticker -= 5
                fall_ticker = max_ticker + 200
                if GRID.has_hit_ground(moving_piece):
                    draw_grid(GRID)
                    pygame.display.flip()
                    end = True

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and move_ticker == 0:
                if event.key == pygame.K_RETURN:
                    GRID.move_piece_to_ground(moving_piece)
                    draw_points(GRID)
                if event.key == pygame.K_UP or event.key == K_w:
                    if GRID.rotating_possible(moving_piece):
                        GRID.clear_piece(moving_piece)
                        moving_piece.rotate()
                        GRID.place_piece(moving_piece, moving_piece.anchor)
                        move_ticker = 60
                if event.key == pygame.K_LEFT or event.key == K_a:
                    GRID.move_piece_left(moving_piece)
                    move_ticker = 60
                if event.key == pygame.K_RIGHT or event.key == K_d:
                    GRID.move_piece_right(moving_piece)
                    move_ticker = 60
                if event.key == pygame.K_DOWN or event.key == K_s:
                    GRID.move_piece_down(moving_piece)
                    move_ticker = 30
                    draw_points(GRID)

        while end:
            game_over()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

        if fall_ticker == 0:
            GRID.move_piece_down(moving_piece)
            draw_points(GRID)
            fall_ticker = max_ticker

        if move_ticker > 0:
            move_ticker -= 1
        if fall_ticker > 0:
            fall_ticker -= 1


def draw_points(grid):
    place_x = DISPLAY.get_width() - 210
    place_y = DISPLAY.get_height() - 60
    pygame.draw.rect(DISPLAY, GREY, (place_x, place_y, 200, 200))
    game_font = pygame.freetype.SysFont('Type1', 35)
    game_font.render_to(DISPLAY, (place_x, place_y)
                        , "score: " + str(grid.points), RED)


def draw_grid(grid):
    for i, arr in enumerate(grid.shape):
        for j, tile in enumerate(arr):
            pygame.draw.rect(DISPLAY, BLACK, ((field_place_x + j * SQUARES_SIZE),
                                              (field_place_y + i * SQUARES_SIZE),
                                              SQUARES_SIZE, SQUARES_SIZE))
            if tile is None:
                pygame.draw.rect(DISPLAY, GREY, ((field_place_x + j * SQUARES_SIZE),
                                                 (field_place_y + i * SQUARES_SIZE),
                                                 SQUARES_SIZE, SQUARES_SIZE), 1)
            else:
                pygame.draw.rect(DISPLAY, tile.color, ((field_place_x + j * SQUARES_SIZE),
                                                       (field_place_y + i * SQUARES_SIZE),
                                                       SQUARES_SIZE, SQUARES_SIZE))
                pygame.draw.rect(DISPLAY, GREY, ((field_place_x + j * SQUARES_SIZE),
                                                 (field_place_y + i * SQUARES_SIZE),
                                                 SQUARES_SIZE, SQUARES_SIZE), 2)


def generate_piece(grid):
    possible_types = [I(), J(), L(),
                      L(), O(), S(), T(), Z()]
    choose_type = random.randint(0, len(possible_types) - 1)
    placement = random.randint(0, len(grid.shape[0]) - len(possible_types[choose_type].shape[0]))
    grid.place_piece(possible_types[choose_type], [0, placement])
    moving_piece = possible_types[choose_type]
    return moving_piece


def game_over():
    place_x = DISPLAY.get_width() - 250
    place_y = 60
    game_font = pygame.freetype.SysFont('Type1', 35)
    game_font.render_to(DISPLAY, (place_x, place_y), "Game Over", RED)
    pygame.display.flip()


pygame.init()
DISPLAY = pygame.display.set_mode((900, 600), 0, 32)
DISPLAY.fill(GREY)

field_width = DISPLAY.get_size()[0] - 625
field_height = field_width * 2

field_place_x = (DISPLAY.get_size()[0] - field_width) / 2
field_place_y = (DISPLAY.get_size()[1] - field_height) / 2

SQUARES_SIZE = field_width / 10

GRID = Grid()

main()
