// Global game variables and game states
let gameState = 'menu' // "menu", "playing", "levelComplete", "gameOver", "win"
let currentLevel = 1
const totalLevels = 5

let ball
let paddle
let bricks = []
let cols = 8 // Number of brick columns
let brickWidth
let brickHeight = 20
let score = 0
let gradientBuffer // Offscreen graphics buffer for background gradient

function setup() {
  // Create a full screen canvas
  createCanvas(windowWidth, windowHeight)
  frameRate(60)
  textFont('Roboto')
  // For a smooth modern look, use no stroke for shapes in gameplay
  noStroke()

  // Precompute the gradient background buffer
  createGradientBuffer()
}

function windowResized() {
  // Resize canvas and update gradient background when window size changes
  resizeCanvas(windowWidth, windowHeight)
  createGradientBuffer()
  // Update brick configuration if desired, e.g. reposition elements if you use full-screen layout.
}

// Precompute the gradient background to boost performance.
function createGradientBuffer() {
  gradientBuffer = createGraphics(width, height)
  for (let y = 0; y < height; y++) {
    let inter = map(y, 0, height, 0, 1)
    let c = lerpColor(color(20, 20, 20), color(50, 50, 50), inter)
    gradientBuffer.stroke(c)
    gradientBuffer.line(0, y, width, y)
  }
  gradientBuffer.noStroke()
}

function draw() {
  // Draw the cached gradient background
  image(gradientBuffer, 0, 0)

  // Switch by state
  switch (gameState) {
    case 'menu':
      drawMenu()
      break
    case 'playing':
      runGameLevel()
      break
    case 'levelComplete':
      drawLevelComplete()
      break
    case 'gameOver':
      drawGameOver()
      break
    case 'win':
      drawWin()
      break
  }
}

// -----------------------------------------------------
// Menu and State Screens
// -----------------------------------------------------

function drawMenu() {
  fill(255)
  textAlign(CENTER, CENTER)
  textSize(60)
  text('Brick Breaker', width / 2, height / 2 - 80)

  textSize(24)
  text('Click to Start', width / 2, height / 2)
  textSize(16)
  text('Use Left / Right Arrow Keys to Move', width / 2, height / 2 + 40)
}

function drawLevelComplete() {
  fill(0, 200, 0)
  textAlign(CENTER, CENTER)
  textSize(50)
  text('Level ' + currentLevel + ' Complete!', width / 2, height / 2 - 40)

  textSize(24)
  if (currentLevel < totalLevels) {
    text('Click to proceed to next level', width / 2, height / 2 + 10)
  } else {
    text('Click to see your victory', width / 2, height / 2 + 10)
  }
}

function drawGameOver() {
  fill(255, 50, 50)
  textAlign(CENTER, CENTER)
  textSize(50)
  text('Game Over!', width / 2, height / 2 - 40)

  textSize(24)
  text('Click to return to Menu', width / 2, height / 2 + 10)
}

function drawWin() {
  fill(0, 255, 0)
  textAlign(CENTER, CENTER)
  textSize(50)
  text('You Win!', width / 2, height / 2 - 40)

  textSize(24)
  text('Click to return to Menu', width / 2, height / 2 + 10)
}

// -----------------------------------------------------
// Game Loop for Playing State
// -----------------------------------------------------

function runGameLevel() {
  // Display current score and level at the top left
  fill(255)
  textSize(20)
  textAlign(LEFT, TOP)
  text('Score: ' + score, 10, 10)
  text('Level: ' + currentLevel, 10, 35)

  paddle.show()
  paddle.update()

  ball.show()
  ball.update()

  // Check collisions with bricks in reverse order
  for (let i = bricks.length - 1; i >= 0; i--) {
    bricks[i].show()
    if (bricks[i].collides(ball)) {
      ball.reverse('y') // Reverse ball's vertical direction
      score++
      bricks.splice(i, 1)
    }
  }

  ball.checkEdges()
  ball.checkPaddle(paddle)

  // Level/game progression
  if (ball.offScreen()) {
    gameState = 'gameOver'
  }
  if (bricks.length === 0) {
    if (currentLevel < totalLevels) {
      gameState = 'levelComplete'
    } else {
      gameState = 'win'
    }
  }
}

// -----------------------------------------------------
// mousePressed for Menu, Level Progress, and Reset
// -----------------------------------------------------

function mousePressed() {
  // In menu and all end states, clicking will either start or reset the game
  if (gameState === 'menu') {
    startGame()
  } else if (gameState === 'levelComplete') {
    currentLevel++
    resetLevel()
    gameState = 'playing'
  } else if (gameState === 'gameOver' || gameState === 'win') {
    gameState = 'menu'
    currentLevel = 1
    score = 0
  }
}

// -----------------------------------------------------
// Start Game and Level Reset Functions
// -----------------------------------------------------

function startGame() {
  currentLevel = 1
  score = 0
  resetLevel()
  gameState = 'playing'
}

function resetLevel() {
  // Create a new ball and paddle
  ball = new Ball()
  paddle = new Paddle()
  bricks = []
  // Increase rows per level for added difficulty
  let rows = currentLevel + 4 // level 1 = 5 rows, etc.
  brickWidth = width / cols
  // Create bricks in grid formation with some padding at the top
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      bricks.push(new Brick(j * brickWidth, i * brickHeight + 50, brickWidth, brickHeight))
    }
  }
}

// -----------------------------------------------------
// Ball Class
// -----------------------------------------------------

class Ball {
  constructor() {
    this.r = 10
    this.x = width / 2
    this.y = height - 70
    // Increase speed with level
    this.speed = 5 + currentLevel - 1
    // Random horizontal direction
    this.xSpeed = random(-this.speed, this.speed)
    this.ySpeed = -this.speed
  }

  show() {
    fill(255)
    ellipse(this.x, this.y, this.r * 2, this.r * 2)
  }

  update() {
    this.x += this.xSpeed
    this.y += this.ySpeed
  }

  checkEdges() {
    if (this.x < this.r || this.x > width - this.r) {
      this.reverse('x')
    }
    if (this.y < this.r) {
      this.reverse('y')
    }
  }

  reverse(axis) {
    if (axis === 'x') {
      this.xSpeed *= -1
    } else if (axis === 'y') {
      this.ySpeed *= -1
    }
  }

  checkPaddle(paddle) {
    if (this.x > paddle.x && this.x < paddle.x + paddle.w && this.y + this.r > paddle.y && this.y - this.r < paddle.y + paddle.h) {
      this.y = paddle.y - this.r // Position ball on top of paddle
      this.reverse('y')
      // Adjust horizontal speed based on contact point
      let hitPoint = this.x - (paddle.x + paddle.w / 2)
      this.xSpeed = hitPoint * 0.1
    }
  }

  offScreen() {
    return this.y - this.r > height
  }
}

// -----------------------------------------------------
// Paddle Class
// -----------------------------------------------------

class Paddle {
  constructor() {
    this.w = 120
    this.h = 20
    this.x = width / 2 - this.w / 2
    this.y = height - this.h - 10
    this.speed = 7
  }

  show() {
    fill(200)
    rect(this.x, this.y, this.w, this.h, 5)
  }

  update() {
    if (keyIsDown(LEFT_ARROW)) {
      this.x -= this.speed
    }
    if (keyIsDown(RIGHT_ARROW)) {
      this.x += this.speed
    }
    this.x = constrain(this.x, 0, width - this.w)
  }
}

// -----------------------------------------------------
// Brick Class
// -----------------------------------------------------

class Brick {
  constructor(x, y, w, h) {
    this.x = x
    this.y = y
    this.w = w
    this.h = h
    // Create a random yet sleek color
    this.color = color(random(100, 255), random(100, 255), random(100, 255))
  }

  show() {
    fill(this.color)
    rect(this.x, this.y, this.w, this.h, 3)
  }

  collides(ball) {
    let closestX = constrain(ball.x, this.x, this.x + this.w)
    let closestY = constrain(ball.y, this.y, this.y + this.h)
    let distanceX = ball.x - closestX
    let distanceY = ball.y - closestY
    let distance = sqrt(distanceX * distanceX + distanceY * distanceY)

    return distance < ball.r
  }
}
