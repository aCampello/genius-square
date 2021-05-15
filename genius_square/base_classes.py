import numpy as np
import random
import time

from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column


class Piece:
    piece_to_shape = {
        'grey': [(0, 0), (1, 0), (2, 0), (3, 0)],
        'green': [(0, 0), (1, 0), (0, 1), (1, 1)],
        'deepskyblue': [(0, 0), (0, 1), (0, 2), (1, 2)],
        'darkorange': [(0, 0), (1, 0), (2, 0)],
        'yellow': [(1, 0), (0, 1), (1, 1), (2, 1)],
        'red': [(0, 1), (1, 1), (1, 0), (2, 0)],
        'sienna': [(0, 0), (1, 0)],
        'purple': [(0, 0), (0, 1), (1, 1)],
        'navy': [(0, 0)]
    }

    piece_to_number = {
        'grey': 1,
        'green': 2,
        'deepskyblue': 3,
        'darkorange': 4,
        'yellow': 5,
        'red': 6,
        'sienna': 7,
        'purple': 8,
        'navy': 9
    }
    number_to_piece = {number: piece for piece, number in piece_to_number.items()}

    piece_to_rot_1 = {
        'grey': [(0, 0), (0, 1), (0, 2), (0, 3)],
        'deepskyblue': [(0, 1), (1, 1), (2, 1), (2, 0)],
        'darkorange': [(0, 0), (0, 1), (0, 2)],
        'yellow': [(0, 1), (1, 0), (1, 1), (1, 2)],
        'red': [(0, 0), (0, 1), (1, 1), (1, 2)],
        'sienna': [(0, 0), (0, 1)],
        'purple': [(1, 0), (1, 1), (0, 1)]
    }

    piece_to_rot_2 = {
        'deepskyblue': [(0, 0), (1, 0), (1, 1), (1, 2)],
        'yellow': [(0, 0), (1, 0), (2, 0), (1, 1)],
        'red': [(0, 0), (1, 0), (1, 1), (2, 1)],
        'purple': [(0, 0), (1, 0), (1, 1)]
    }

    piece_to_rot_3 = {
        'deepskyblue': [(0, 0), (1, 0), (2, 0), (0, 1)],
        'yellow': [(0, 0), (0, 1), (1, 1), (0, 2)],
        'red': [(1, 0), (1, 1), (0, 1), (0, 2)],
        'purple': [(0, 0), (1, 0), (0, 1)]
    }

    # By abuse of notation, rotations from 4 to 7 are actually a flip + a rotation
    # It is only relevant in the case of deepskyeblue pieces
    piece_to_rot_4 = {
        'deepskyblue': [(0, 2), (1, 2), (1, 1), (1, 0)]

    }

    piece_to_rot_5 = {
        'deepskyblue': [(0, 0), (1, 0), (2, 0), (2, 1)]

    }

    piece_to_rot_6 = {
        'deepskyblue': [(0, 0), (0, 1), (0, 2), (1, 0)]

    }

    piece_to_rot_7 = {
        'deepskyblue': [(0, 0), (0, 1), (1, 1), (2, 1)]

    }

    def __init__(self, piece_type: str):
        self.piece_type = piece_type
        self.shape = self.piece_to_shape[piece_type]
        self.number = self.piece_to_number[piece_type]
        self.rot = [None]*8
        self.rot[0] = self.shape
        self.rot[1] = self.piece_to_rot_1.get(self.piece_type)
        self.rot[2] = self.piece_to_rot_2.get(self.piece_type)
        self.rot[3] = self.piece_to_rot_3.get(self.piece_type)
        self.rot[4] = self.piece_to_rot_4.get(self.piece_type)
        self.rot[5] = self.piece_to_rot_5.get(self.piece_type)
        self.rot[6] = self.piece_to_rot_6.get(self.piece_type)
        self.rot[7] = self.piece_to_rot_7.get(self.piece_type)

    def __repr__(self):
        return self.piece_type


class Board:
    letter_to_index = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}
    index_to_letter = {index: letter for letter, index in letter_to_index.items()}

    dice = [
        ('C3', 'E3', 'D3', 'D4', 'B4', 'C4'),
        ('E6', 'F5', 'E4', 'F4', 'E5', 'D5'),
        ('C5', 'F6', 'A4', 'D6', 'B5', 'C6'),
        ('B1', 'C2', 'A2', 'B3', 'A3', 'B2'),
        ('E1', 'F2', 'B6', 'A5'),
        ('F3', 'D2', 'E2', 'C1', 'A1', 'D1'),
        ('A6', 'F1')
    ]

    def __init__(self, initial_dice=None):
        self.initial_dice = initial_dice

        if not initial_dice:
            self.initial_dice = self._roll_dice()

        self.matrix = np.zeros((6, 6), dtype=int)

        for dice in self.initial_dice:
            i, j = self.letter_to_index[dice[0]]-1, int(dice[1])-1

            self.matrix[i, j] = -1

    def __repr__(self):
        return f"{self.matrix}"

    def _roll_dice(self):
        initial_dice = [d[random.randint(0, len(d)-1)]for d in self.dice]
        return initial_dice

    def _is_valid(self, position, shape):
        for coord_i, coord_j in shape:
            if self.matrix[coord_i+position[0]][coord_j+position[1]] != 0:
                return False

        return True

    def check_possible_positions(self, piece: Piece, rotation=0):
        shape = piece.rot[rotation]
        max_i = max(coord[0] for coord in shape)
        max_j = max(coord[1] for coord in shape)

        possible_positions = []

        for pos_i in range(6-max_i):
            for pos_j in range(6-max_j):
                if not self._is_valid((pos_i, pos_j), shape):
                    continue

                possible_positions.append((rotation, (pos_i, pos_j)))

        if rotation < 7 and piece.rot[rotation+1]:
            possible_positions += self.check_possible_positions(piece, rotation+1)

        return possible_positions

    def place_piece(self, piece: Piece, position, rotation=0):
        shape = piece.rot[rotation]
        for coord_i, coord_j in shape:
            self.matrix[coord_i+position[0]][coord_j+position[1]] = piece.number

    def remove_piece(self, piece: Piece, position, rotation=0):
        shape = piece.rot[rotation]
        for coord_i, coord_j in shape:
            self.matrix[coord_i+position[0]][coord_j+position[1]] = 0


def plot_board(board: Board):

    rows = []
    rows_barriers = []
    cols = []
    cols_barriers = []
    colors = []
    colors_barriers = []
    number_to_colour = Piece.number_to_piece
    number_to_colour[0] = 'white'
    number_to_colour[-1] = 'white'

    for i in range(6):
        for j in range(6):
            rows.append(str(i))
            cols.append(board.index_to_letter[j+1])
            # Just get the colour
            colors.append(number_to_colour[board.matrix[j, i]].replace('_flip', ''))
            if board.matrix[j, i] == -1:
                rows_barriers.append(str(i))
                cols_barriers.append(board.index_to_letter[j+1])
                colors_barriers.append('bisque')



    data = {
        "x": rows,
        "y": cols,
        "colors": colors,
    }

    barriers = {
        "x": rows_barriers,
        "y": cols_barriers,
        "colors": colors_barriers
    }

    title = "Game"
    tools = "save,wheel_zoom"

    p = figure(title=title, x_axis_location="below", tools=tools,
               x_range=list(np.unique(rows)),
               y_range=list(reversed(np.unique(cols))))

    p.plot_width = 500
    p.plot_height = 500
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "12pt"

    p.rect('x', 'y', 1, 1, source=data,
           color='colors', line_color='black',
           hover_line_color='black', hover_color='colors')

    p.circle(x='x', y='y', radius=0.45, source=barriers,
             color='colors', line_color='black',
             hover_line_color='black', hover_color='colors')

    return p


def test_piece(piece):
    board = Board()
    plot_board(board)
    boards =[]
    for rotation in range(8):
        if Piece(piece).rot[rotation]:
            board.place_piece(Piece(piece), (0, 0), rotation=rotation)
            boards.append(plot_board(board))
            board.remove_piece(Piece(piece), (0, 0), rotation=rotation)

    show(column(*boards))
