// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const STORAGE_KEY = 'sudoku-leaderboard';
let puzzle = [];
let currentDifficulty = 'easy';
let gameStartTime = null;
let hintsUsed = 0;
let completedGame = false;

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.dataset.row = i;
      input.dataset.col = j;
      const blockClass = (Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 0 ? 'block-even' : 'block-odd';
      input.dataset.blockClass = blockClass;
      input.className = 'sudoku-cell';
      input.classList.add(blockClass);
      input.addEventListener('input', (event) => {
        const val = event.target.value.replace(/[^1-9]/g, '');
        event.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.className = 'sudoku-cell';
      inp.classList.add(inp.dataset.blockClass);
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function updateStatus() {
  const timerElement = document.getElementById('timer');
  const hintsElement = document.getElementById('hints-used');
  if (gameStartTime === null) {
    timerElement.innerText = 'Time: 0s';
  } else {
    const elapsed = Math.floor((Date.now() - gameStartTime) / 1000);
    timerElement.innerText = `Time: ${elapsed}s`;
  }
  hintsElement.innerText = `Hints used: ${hintsUsed}`;
}

function getStoredEntries() {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    return [];
  }
}

function saveScore(timeSeconds) {
  const nameInput = document.getElementById('player-name');
  const playerName = (nameInput.value || 'Anonymous').trim() || 'Anonymous';
  const entry = {
    name: playerName,
    time: timeSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed,
    completedAt: new Date().toISOString(),
  };
  const entries = [...getStoredEntries(), entry]
    .sort((left, right) => left.time - right.time)
    .slice(0, 10);
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  renderLeaderboard();
}

function renderLeaderboard() {
  const entries = getStoredEntries()
    .sort((left, right) => left.time - right.time)
    .slice(0, 10);
  const list = document.getElementById('leaderboard-list');
  list.innerHTML = '';

  if (entries.length === 0) {
    const item = document.createElement('li');
    item.innerText = 'No scores yet.';
    list.appendChild(item);
    return;
  }

  entries.forEach((entry, index) => {
    const item = document.createElement('li');
    item.innerText = `${index + 1}. ${entry.name} — ${entry.time}s — ${entry.difficulty} — hints: ${entry.hints}`;
    list.appendChild(item);
  });
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  currentDifficulty = data.difficulty || difficulty;
  gameStartTime = Date.now();
  hintsUsed = 0;
  completedGame = false;
  updateStatus();
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const incorrect = new Set(data.incorrect.map((cell) => cell[0] * SIZE + cell[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) {
      continue;
    }
    inp.className = 'sudoku-cell';
    inp.classList.add(inp.dataset.blockClass);
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }

  if (incorrect.size === 0) {
    if (!completedGame) {
      const elapsedSeconds = Math.floor((Date.now() - gameStartTime) / 1000);
      saveScore(elapsedSeconds);
      completedGame = true;
    }
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! Your score was saved.';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function getHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const emptyCell = Array.from(inputs).find((input) => !input.disabled && input.value === '');
  if (!emptyCell) {
    return;
  }

  const row = parseInt(emptyCell.dataset.row, 10);
  const col = parseInt(emptyCell.dataset.col, 10);
  const res = await fetch(`/hint?row=${row}&col=${col}`);
  const data = await res.json();

  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }

  emptyCell.value = data.value;
  emptyCell.disabled = true;
  emptyCell.classList.add('prefilled');
  puzzle[row][col] = data.value;
  hintsUsed = data.hints_used ?? hintsUsed + 1;
  updateStatus();
  document.getElementById('message').innerText = 'Hint used.';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', getHint);
  renderLeaderboard();
  updateStatus();
  newGame();
});