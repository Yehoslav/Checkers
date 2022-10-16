var drawnBoard = []

for (var file = 0; file < 8; file++) {
  for (var rank = 0; rank < 8; rank++) {
    drawnBoard.push({
      rank: rank,
      file: file,
      x: rank * 100,
      y: file * 100,
      width: 100,
      height: 100,
      fillcolor: (rank + file) % 2 == 0 ? "white" : "black",
      cellType: (rank + file) % 2 == 0 ? "white" : "black",
      isFilled: true
    })
  }
}

function renderBoard(board, checkers) {
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");
  var $canvas = $("#canvas");
  var canvasOffset = $canvas.offset();
  var offsetX = canvasOffset.left;
  var offsetY = canvasOffset.top;

  draw(board);

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < drawnBoard.length; i++) {
      var rect = drawnBoard[i];
      ctx.fillStyle = rect.fillcolor;
      ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
      ctx.strokeStyle = "black";
      ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
      ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);

    }
    // Draw checkers
    for (var checker of checkers) {
      console.log(checker)
      ctx.beginPath();
      ctx.arc(
        checker.rank * 100 + 50,
        checker.file * 100 + 50,
        45, 1 * Math.PI, 4 * Math.PI);
      ctx.closePath();
      ctx.fillStyle = checker.type;
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#7F7F7F';
      ctx.stroke();
    }
  }

  function hit(rect, x, y) {
    return (x >= rect.x && x <= rect.x + rect.width && y >= rect.y && y <= rect.y + rect.height);
  }

  function handleMouseDown(e, rects) {
    e.preventDefault();
    mouseX = parseInt(e.clientX - offsetX);
    mouseY = parseInt(e.clientY - offsetY);
    for (var i = 0; i < drawnBoard.length; i++) {
      var rect = drawnBoard[i];
      if (hit(rect, mouseX, mouseY)) {
        rect.fillcolor = rect.fillcolor == "red" ? rect.cellType : "red"
      }
    }
    draw();
  }
  $("#canvas").mousedown(function(e) {
    handleMouseDown(e);
  });
};

$(window).load(() => renderBoard(drawnBoard, [
  {
    type: "white",
    file: 0, rank: 0
  },
  {
    type: "black",
    file: 2, rank: 2
  }
]))


