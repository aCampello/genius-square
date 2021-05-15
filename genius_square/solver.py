import itertools
import json
import time

import tqdm
from bokeh.plotting import output_file, show
from bokeh.layouts import column
from joblib import Parallel, delayed

from base_classes import Board, Piece, plot_board

grey = Piece('grey')
green = Piece('green')
blue = Piece('deepskyblue')
orange = Piece('darkorange')
yellow = Piece('yellow')
red = Piece('red')
brown = Piece('sienna')
purple = Piece('purple')
navy = Piece('navy')


def solve(board: Board, pieces=[grey, green, blue, orange, yellow, red, brown, purple, navy],
          all_solutions=False):
    """Recursive solver for the board. Returns a list with (piece_type, (rotation, position))"""
    positions = board.check_possible_positions(pieces[0])

    if len(pieces) == 1 and len(positions) > 0:
        if all_solutions:
            return [((pieces[0], position),) for position in positions]
        else:
            return [(pieces[0], positions[0])]

    solutions = []
    for rotation, position in positions:
        board.place_piece(pieces[0], position=position, rotation=rotation)

        solution_remaining_pieces = solve(board, pieces[1:], all_solutions=all_solutions)

        # If this position yields a valid solution in the recursion stack, add/returns to the stack
        # Then removes the piece and proceeds to next position

        if solution_remaining_pieces:
            # If we are interested in all solutions, we have to keep track of all
            # Otherwise we can just return a valid solution
            if all_solutions:
                solutions += [
                    ((pieces[0], (rotation, position)),) + solution
                     for solution in solution_remaining_pieces
                ]
            else:
                solutions = [(pieces[0], (rotation, position))] + \
                           solution_remaining_pieces
                return solutions

        board.remove_piece(pieces[0], position=position, rotation=rotation)

    return solutions


def place_solution(board, sol):
    for piece, (rotation, position) in sol:
        board.place_piece(piece, position=position, rotation=rotation)

    return board


def clear_board(board, sol):
    for piece, (rotation, position) in sol:
        board.remove_piece(piece, position=position, rotation=rotation)

    return board


def random_board_and_solutions(initial_dice=None):
    board = Board(initial_dice=initial_dice)
    plot_board(board)

    start = time.time()

    sol = solve(board)
    output_file('output.html')

    board = place_solution(board, sol)

    print(f"Time to find 1 solution: {time.time()-start:.5f}")

    board = clear_board(board, sol)
    sols = solve(board, all_solutions=True)
    print(len(set(sols)))

    print(f"Time to find all solutions: {time.time()-start:.5f}")

    p_sols = []
    for sol in sols[:10]:
        board = place_solution(board, sol)
        p_sols.append(plot_board(board))
        board = clear_board(board, sol)

    show(column(*p_sols))

    return sols


all_dice_combinations = list(itertools.product(*Board.dice))

if __name__ == "__main__":
    #random_board_and_solutions()

    start = time.time()
    # Clears board and tries to find all solutions

    def one_iteration_solve(dice):
        board = Board(initial_dice=dice)

        sols = solve(board, all_solutions=True)

        return ",".join(board.initial_dice), len(set(sols))


    # for dice in all_dice_combinations[:5]:
    #     one_iteration_solve(dice)

    results = \
        Parallel(n_jobs=8)(
            delayed(one_iteration_solve)(dice) for dice in all_dice_combinations[:1000]
        )

    print(f"{time.time()-start:.5f}")

    dice_to_number_of_solutions = {
        key: value
        for key, value in results
    }
    with open('solutions.json', 'w') as f:
        json.dump(dice_to_number_of_solutions, f, indent=4, sort_keys=True)

