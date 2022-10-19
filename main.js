let selected = null;
let player_skin;
let player_id;

function createBoard() {
  var drawnBoard = []
  const size = 50;

  for (var file = 0; file < 8; file++) {
    for (var rank = 0; rank < 8; rank++) {
      drawnBoard.push({
        rank: rank,
        file: file,
        x: file * size,
        y: 7 * size - rank * size,
        width: size,
        height: size,
        fillcolor: (rank + file) % 2 == 0 ? `#${(0xaaa - (0x00a * (rank + file))).toString(16)}` : "white",
        cellType: (rank + file) % 2 == 0 ? `#${(0xaaa - (0x00a * (rank + file))).toString(16)}` : "white",
        occupiedBy: null
      })
    }
  }

  return drawnBoard;
}

function hit(rect, x, y) {
  return (x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height);
}

function clearBoard(board) {
  for (let square of board) {
    square.occupiedBy = null;
  }
}

function draw(board, checkers) {
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  clearBoard(board);
  for (var i = 0; i < board.length; i++) {
    var rect = board[i];

    for (const checker of checkers) {
      if (rect.file === checker.file && rect.rank === checker.rank) {
        rect.occupiedBy = checker.type;
        break;
      }
    }
    ctx.fillStyle = rect.fillcolor;
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
    ctx.strokeStyle = "black";
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
    ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
  }
  // Draw checkers
  for (var checker of checkers) {
    ctx.beginPath();
    ctx.arc(
      checker.file * rect.width + rect.width / 2,
      7 * rect.height - checker.rank * rect.height + rect.height / 2,
      rect.width / 2 - 5, 1 * Math.PI, 4 * Math.PI);
    ctx.closePath();
    ctx.fillStyle = checker.type;
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#7F7F7F';
    ctx.stroke();
  }
}


function renderBoard(board, checkers) {
  draw(board, checkers);

};

function initGame(websocket) {
  websocket.addEventListener("open", () => {
    const params = new URLSearchParams(window.location.search)
    let event = { type: "init" }
    console.log()
    if (params.has("join") && !params.has("start")) {
      // Second player joins an existing game.
      event.join = params.get("join")
      player_skin = "black"
      event.player_skin = player_skin
    } else if (params.has('watch')) {
      // Spectator watches an existing game
      event.watch = params.get("watch")
    } else {
      // First player starts a new game.
      player_skin = "white"
      event.player_skin = player_skin
    }
    websocket.send(JSON.stringify(event))
  })
}

function receiveMoves(board, websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data)
    // console.log(event)
    switch (event.type) {
      case "init":
        // Create link for inviting the second player
        // document.querySelector(".join").href = "?join=" + event.join;
        // document.querySelector(".watch").href = "?watch=" + event.watch_key;
        // console.log(event)
        player_id = event.player_id
        draw(board, event.checkers)
        break;
      case "play":
        // console.log(event)
        for (let rect of board) {
          let i = 0;
          if (event.action === "get_moves") {

            for (let pos of event.av_moves) {
              if (rect.file === pos[0] && rect.rank === pos[1]) {
                i++;
              }

            }
          }
          if (i === 1) {
            rect.fillcolor = "red"
          } else {
            rect.fillcolor = rect.cellType
          }
        }
        if (event.action === "move") {

          draw(board, event.checkers)
          break;
        }

        draw(board, event.checkers)
        break;
      case "join":
        player_id = event.player_id
        draw(board, event.checkers)
        break;
      case "error":
        // console.log(event.message)
        break;
      default:
        throw new Error(`Unsuported event type: ${event.type}`)
    }
  })
}

function handleMouseDown(e, rects, websocket) {
  e.preventDefault();
  var $canvas = $("#canvas");
  var canvasOffset = $canvas.offset();
  var offsetX = canvasOffset.left;
  var offsetY = canvasOffset.top;
  mouseX = parseInt(e.clientX - offsetX) + window.scrollX;
  mouseY = parseInt(e.clientY - offsetY) + window.scrollY;
  for (var i = 0; i < rects.length; i++) {
    var rect = rects[i];
    if (hit(rect, mouseX, mouseY)) {
      let event = {
        type: "play",
        position: [rect.file, rect.rank],
        player_id: player_id,
      }
      if (rect.occupiedBy === player_skin) {
        event.action = 'get_moves'
        selected = rect

      } else if (rect.fillcolor === "red") {
        event.action = 'move'
        event.init = selected
      } else {
        return;
      }
      websocket.send(JSON.stringify(event))
      return;
    }
  }
}

function sendMoves(board, websocket) {
  // Dont't send moves for a spectator wathcing a game 
  const params = new URLSearchParams(window.location.search);
  if (params.has("watch")) { return; }

  // When clicking a column, send a "play" event for a move in that column.
  $("#canvas").mousedown(function(e) {
    handleMouseDown(e, board, websocket);
  });
}

function createLobby(games) {
  var gameList = $("#active-games")
  
  console.dir(games)
  var items = "";
  for (const game of games) {
    const listItem = `<li>${game.join_key} : ${game.full ? "Full" : "1 player waiting"} <a class="btn-sm" href="?join=${game.join_key}">Join</a><a class="btn-sm" href="?watch=${game.watch_key}&action=watch">Watch</a></li>`
    items = items.concat(listItem)
  }
  console.log(items)
  gameList[0].innerHTML = items
}

function getGames(websocket) {
  websocket.addEventListener("open", () => {
    var event = {
      type: "init",
    }
    websocket.send(JSON.stringify(event))
  })
  
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data)
    if (event.type == "games") {
      createLobby(event.games)
    }
  })
}

function closeLobby() {
  $("#lobby")[0].style.display = "none"
  $(".board")[0].style.display = "block"
}

window.addEventListener("DOMContentLoaded", () => {
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket("ws://192.168.1.6:8001/");
  const url = new URLSearchParams(window.location.search);
  if (url.has("join")) {
    closeLobby()
    // Initialize the UI.
    const board = createBoard();
    renderBoard(board, [])

    initGame(websocket);
    receiveMoves(board, websocket);
    sendMoves(board, websocket);

  } else {
    getGames(websocket)
  }
});

