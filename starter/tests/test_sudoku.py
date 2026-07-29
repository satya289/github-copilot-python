import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import CURRENT, app
from sudoku_logic import (
    count_solutions,
    generate_board,
    generate_puzzle,
    get_target_clues,
)


def test_board_generation():
    """Check generated board size."""

    board = generate_board()

    assert len(board) == 9
    assert len(board[0]) == 9


def test_board_values():
    """Check sudoku numbers are valid."""

    board = generate_board()

    for row in board:
        for value in row:
            assert 1 <= value <= 9


def test_generated_puzzle_has_exactly_one_solution():
    """Generated puzzles should have a unique solution."""

    puzzle, solution = generate_puzzle(clues=36)

    assert puzzle is not None
    assert solution is not None
    assert count_solutions(puzzle) == 1


def test_difficulty_targets_use_expected_clue_counts():
    """Difficulty levels should target the expected clue counts."""

    assert get_target_clues(difficulty="easy") == 40
    assert get_target_clues(difficulty="medium") == 32
    assert get_target_clues(difficulty="hard") == 25


def test_difficulties_generate_different_numbers_of_empty_cells():
    """Easy, medium, and hard puzzles should differ in clue density."""

    easy_puzzle, easy_solution = generate_puzzle(difficulty="easy")
    medium_puzzle, medium_solution = generate_puzzle(difficulty="medium")
    hard_puzzle, hard_solution = generate_puzzle(difficulty="hard")

    easy_clues = sum(cell != 0 for row in easy_puzzle for cell in row)
    medium_clues = sum(cell != 0 for row in medium_puzzle for cell in row)
    hard_clues = sum(cell != 0 for row in hard_puzzle for cell in row)

    assert easy_clues > medium_clues > hard_clues
    assert count_solutions(easy_puzzle) == 1
    assert count_solutions(medium_puzzle) == 1
    assert count_solutions(hard_puzzle) == 1
    assert easy_solution is not None
    assert medium_solution is not None
    assert hard_solution is not None


def test_check_solution_ignores_empty_cells():
    """The check endpoint should flag only non-empty incorrect entries."""

    client = app.test_client()
    solution = generate_board()
    CURRENT['solution'] = solution

    board = [row[:] for row in solution]
    board[0][1] = 9 if solution[0][1] != 9 else 1
    board[0][2] = 0

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 1]]


def test_hint_endpoint_returns_the_correct_value():
    """The hint endpoint should return the expected solution value."""

    client = app.test_client()
    solution = generate_board()
    CURRENT['solution'] = solution
    CURRENT['puzzle'] = [[0 for _ in range(9)] for _ in range(9)]
    CURRENT['hints_used'] = 0

    response = client.get('/hint?row=0&col=1')

    assert response.status_code == 200
    assert response.get_json()['value'] == solution[0][1]
    assert CURRENT['hints_used'] == 1
    assert CURRENT['puzzle'][0][1] == solution[0][1]