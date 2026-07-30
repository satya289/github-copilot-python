import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    """Return a deep copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board():
    """Create an empty 9x9 Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return True when placing num at (row, col) is valid."""
    for index in range(SIZE):
        if board[row][index] == num:
            return False

        if board[index][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3

    for row_offset in range(3):
        for col_offset in range(3):
            if board[start_row + row_offset][start_col + col_offset] == num:
                return False

    return True


def find_empty_cell(board):
    """Return the first empty coordinate or None when solved."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col

    return None


def get_candidates(board, row, col):
    """Return the valid values that can go in a cell."""
    candidates = list(range(1, SIZE + 1))
    random.shuffle(candidates)

    return [num for num in candidates if is_safe(board, row, col, num)]


def fill_board(board):
    """Recursively solve a board and return True when a solution exists."""
    empty = find_empty_cell(board)

    if empty is None:
        return True

    row, col = empty

    for number in get_candidates(board, row, col):
        board[row][col] = number

        if fill_board(board):
            return True

        board[row][col] = EMPTY

    return False


def create_completed_board():
    """Generate a complete valid Sudoku solution."""
    board = create_empty_board()
    if not fill_board(board):
        raise RuntimeError("Unable to generate a valid Sudoku board")
    return board


def count_solutions(board, limit=2):
    """Count up to limit solutions for a Sudoku board."""
    working_board = deep_copy(board)

    def search():
        nonlocal solutions
        if solutions >= limit:
            return

        empty = find_empty_cell(working_board)
        if empty is None:
            solutions += 1
            return

        row, col = empty

        for number in get_candidates(working_board, row, col):
            working_board[row][col] = number
            search()
            working_board[row][col] = EMPTY

            if solutions >= limit:
                return

    solutions = 0
    search()
    return solutions


def has_unique_solution(board):
    """Return True when a board has exactly one valid solution."""
    return count_solutions(board, limit=2) == 1


def get_target_clues(clues=36, difficulty=None):
    """Convert a difficulty label or clue count into a target clue count."""
    difficulty_map = {
        "easy": 40,
        "medium": 32,
        "hard": 25,
    }

    if difficulty is not None:
        if difficulty in difficulty_map:
            return max(17, min(81, difficulty_map[difficulty]))
        raise ValueError("difficulty must be 'easy', 'medium', or 'hard'")

    return max(17, min(81, clues))


def remove_cells(puzzle, target_clues):
    """Remove cells from a solved board while preserving a unique solution."""
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        current_clues = sum(1 for row_values in puzzle for value in row_values if value != EMPTY)
        if current_clues <= target_clues:
            break

        original_value = puzzle[row][col]
        puzzle[row][col] = EMPTY

        if not has_unique_solution(puzzle):
            puzzle[row][col] = original_value

    return puzzle


def generate_puzzle(clues=36, difficulty=None):
    """Create a puzzle and its unique solution from a complete board."""
    for _ in range(5):
        solution = create_completed_board()
        puzzle = deep_copy(solution)
        target_clues = get_target_clues(clues=clues, difficulty=difficulty)
        puzzle = remove_cells(puzzle, target_clues)

        if has_unique_solution(puzzle):
            return puzzle, solution

    raise RuntimeError("Unable to generate a puzzle with exactly one solution")


def create_board():
    """Create a complete Sudoku board for compatibility."""
    return create_completed_board()


def generate_board():
    """Compatibility function for tests and the Flask app."""
    return create_board()