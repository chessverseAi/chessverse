let board;
let game = new Chess();
let playerColor = null;
let socket = null;
let currentRoom = "room-1";

// Inicializar tablero
window.onload = function() {
  board = ChessBoard('board', {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
  });

  // Intentar unirse si hay sesión
  const username = document.querySelector('#user-info strong')?.innerText;
  if (username && username !== "Invitado") {
    joinRoom(username);
  }
};

function onDragStart(source, piece, position, orientation) {
  if (game.game_over() || !playerColor || game.turn() !== playerColor[0]) {
    return false;
  }
}

async function onDrop(source, target) {
  const move = game.move({
    from: source,
    to: target,
    promotion: 'q'
  });

  if (move === null) return 'snapback';

  // Evaluar movimiento
  const response = await fetch('/evaluate-move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fen: game.fen(), move: move.from + move.to })
  });

  const data = await response.json();
  const feedback = document.getElementById('feedback');

  if (data.visual_effect === 'grow') {
    feedback.innerHTML = `✅ ¡Excelente! (${(data.quality_score * 100).toFixed(1)}%)`;
    document.getElementById('board').className = 'grow';
    updateElo(10);
  } else if (data.visual_effect === 'shrink') {
    feedback.innerHTML = `❌ Arriesgado... (${(data.quality_score * 100).toFixed(1)}%)`;
    document.getElementById('board').className = 'shrink';
    updateElo(-15);
  } else {
    feedback.innerHTML = `🟡 Neutral (${(data.quality_score * 100).toFixed(1)}%)`;
  }
  setTimeout(() => {
    document.getElementById('board').className = '';
    feedback.innerHTML = '';
  }, 1500);

  // Enviar por WebSocket
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: "move",
      move: move.from + move.to,
      fen: game.fen()
    }));
  }

  // Turno de IA (si no hay WebSocket)
  setTimeout(makeRandomMove, 800);
}

function makeRandomMove() {
  if (game.game_over()) return;

  const moves = game.moves();
  if (moves.length > 0) {
    const move = moves[Math.floor(Math.random() * moves.length)];
    game.move(move);
    board.position(game.fen());
  }
}

function onSnapEnd() {
  board.position(game.fen());
}

function resetBoard() {
  game = new Chess();
  board.position('start');
}

// Temas visuales
function changeTheme(theme) {
  document.getElementById('board').className = '';
  document.getElementById('board').classList.add(`theme-${theme}`);
  localStorage.setItem('chessverse-theme', theme);
}

// WebSocket para multijugador
function joinRoom(username) {
  socket = new WebSocket(`ws://localhost:8000/ws/${currentRoom}/${username}`);
  socket.onopen = () => console.log("Conectado al servidor");
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.move) {
      game.move(data.move);
      board.position(game.fen());
    }
  };
}

// Actualizar ELO
function updateElo(delta) {
  const eloEl = document.getElementById('elo');
  let elo = parseInt(eloEl.innerText) + delta;
  elo = Math.max(800, Math.min(3000, elo));
  eloEl.innerText = elo;
}
