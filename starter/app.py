from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle, solution, and hint usage
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'easy').lower()
    clues_value = request.args.get('clues', 35)

    try:
        clues = int(clues_value)
    except (TypeError, ValueError):
        clues = 35

    puzzle, solution = sudoku_logic.generate_puzzle(
        clues=clues,
        difficulty=difficulty,
    )
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')

    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            value = board[row][col]
            if value == 0:
                continue
            if value != solution[row][col]:
                incorrect.append([row, col])

    return jsonify({'incorrect': incorrect})


@app.route('/hint')
def get_hint():
    row = request.args.get('row', type=int)
    col = request.args.get('col', type=int)
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')

    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    if row is None or col is None:
        return jsonify({'error': 'Missing row or col'}), 400

    if not 0 <= row < sudoku_logic.SIZE or not 0 <= col < sudoku_logic.SIZE:
        return jsonify({'error': 'Row and col must be within bounds'}), 400

    if puzzle[row][col] != 0:
        return jsonify({'error': 'Cell is already filled'}), 400

    puzzle[row][col] = solution[row][col]
    CURRENT['hints_used'] = CURRENT.get('hints_used', 0) + 1

    return jsonify({'value': solution[row][col], 'hints_used': CURRENT['hints_used']})


if __name__ == '__main__':
    app.run(debug=True)