let paddle;
let ball;
let bricks = [];
let gameOver = false;
let score = 0;
let lives = 3;

function setup() {
    createCanvas(800, 600);
    textFont('Arial');
    initializeGame();
}

function initializeGame() {
    // Initialize paddle
    paddle = {
        x: width / 2,
        y: height - 30,
        w: 100,
        h: 8,  // Slimmer paddle for modern look
        speed: 8
    };

    // Initialize ball
    ball = {
        x: width / 2,
        y: height - 50,
        size: 10,  // Slightly smaller ball
        speedX: 5,
        speedY: -5,
        glow: 20  // Glow effect size
    };

    // Initialize bricks with modern neon colors
    const brickRows = 5;
    const brickCols = 8;
    const brickWidth = width / brickCols;
    const brickHeight = 25;
    const colors = ['#FF0F7B', '#F89B29', '#42EADD', '#3AB4F2', '#7B4397'];

    for (let i = 0; i < brickRows; i++) {
        for (let j = 0; j < brickCols; j++) {
            bricks.push({
                x: j * brickWidth,
                y: i * brickHeight + 50,
                w: brickWidth - 4,  // More spacing between bricks
                h: brickHeight - 4,
                color: colors[i],
                visible: true
            });
        }
    }
}

function draw() {
    background(18, 18, 24);  // Dark background
    
    if (!gameOver) {
        // Move paddle
        if (keyIsDown(LEFT_ARROW) && paddle.x > 0) {
            paddle.x -= paddle.speed;
        }
        if (keyIsDown(RIGHT_ARROW) && paddle.x < width - paddle.w) {
            paddle.x += paddle.speed;
        }

        // Move ball
        ball.x += ball.speedX;
        ball.y += ball.speedY;

        // Ball collision with walls
        if (ball.x < 0 || ball.x > width) ball.speedX *= -1;
        if (ball.y < 0) ball.speedY *= -1;

        // Ball collision with paddle
        if (ball.y + ball.size/2 >= paddle.y && 
            ball.y + ball.size/2 <= paddle.y + paddle.h &&
            ball.x >= paddle.x && 
            ball.x <= paddle.x + paddle.w) {
            // Only reverse direction if ball is moving downward
            if (ball.speedY > 0) {
                // Calculate new angle based on where the ball hits the paddle
                let paddleCenter = paddle.x + paddle.w/2;
                let distanceFromCenter = ball.x - paddleCenter;
                // Normalize the distance to create an angle factor (-1 to 1)
                let angleFactor = (distanceFromCenter / (paddle.w/2));
                // Set a consistent ball speed
                let baseSpeed = 7;
                // Calculate new velocities
                ball.speedX = baseSpeed * angleFactor;
                ball.speedY = -baseSpeed;
                // Ensure ball doesn't get stuck in paddle
                ball.y = paddle.y - ball.size/2;
            }
        }

        // Ball collision with bricks
        for (let brick of bricks) {
            if (brick.visible && 
                ball.x > brick.x && 
                ball.x < brick.x + brick.w && 
                ball.y > brick.y && 
                ball.y < brick.y + brick.h) {
                brick.visible = false;
                ball.speedY *= -1;
                score += 10;
            }
        }

        // Check for game over
        if (ball.y > height) {
            lives--;
            if (lives <= 0) {
                gameOver = true;
            } else {
                // Reset ball position
                ball.x = width/2;
                ball.y = height - 50;
                ball.speedY = -5;
                ball.speedX = random(-3, 3);
            }
        }

        // Draw paddle with gradient effect
        noStroke();
        for (let i = 0; i < paddle.h; i++) {
            const inter = map(i, 0, paddle.h, 0, 1);
            const c = lerpColor(color(120, 180, 255), color(60, 120, 220), inter);
            fill(c);
            rect(paddle.x, paddle.y + i, paddle.w, 1);
        }

        // Draw ball with glow effect
        drawGlowingBall();

        // Draw bricks with modern style
        for (let brick of bricks) {
            if (brick.visible) {
                drawModernBrick(brick);
            }
        }

        // Draw score and lives with modern UI
        drawUI();

        // Check for win
        if (bricks.every(brick => !brick.visible)) {
            gameOver = true;
        }
    } else {
        // Modern game over screen
        drawGameOverScreen();
    }
}

function drawGlowingBall() {
    // Outer glow
    noStroke();
    for (let i = ball.glow; i > 0; i--) {
        const alpha = map(i, ball.glow, 0, 0, 100);
        fill(255, 70, 70, alpha);
        circle(ball.x, ball.y, ball.size + i);
    }
    // Core of the ball
    fill(255, 90, 90);
    circle(ball.x, ball.y, ball.size);
}

function drawModernBrick(brick) {
    // Brick glow effect
    const brickColor = color(brick.color);
    noStroke();
    for (let i = 4; i > 0; i--) {
        const alpha = map(i, 4, 0, 0, 100);
        fill(red(brickColor), green(brickColor), blue(brickColor), alpha);
        rect(brick.x - i/2, brick.y - i/2, brick.w + i, brick.h + i, 4);
    }
    // Main brick body
    fill(brick.color);
    rect(brick.x, brick.y, brick.w, brick.h, 2);
}

function drawUI() {
    // Score display
    fill(255);
    textSize(20);
    textAlign(LEFT, TOP);
    text(`SCORE ${score}`, 20, 20);

    // Lives display
    textAlign(RIGHT, TOP);
    const livesText = '♥'.repeat(lives);
    fill('#FF0F7B');
    textSize(24);
    text(livesText, width - 20, 15);
}

function drawGameOverScreen() {
    textAlign(CENTER);
    
    // Game Over text with glow
    let glowColor = color('#FF0F7B');
    for (let i = 20; i > 0; i--) {
        const alpha = map(i, 20, 0, 0, 100);
        fill(red(glowColor), green(glowColor), blue(glowColor), alpha);
        textSize(52 + i/2);
        text('GAME OVER', width/2, height/2 - 40);
    }

    // Score and restart text
    fill(255);
    textSize(28);
    text(`Final Score: ${score}`, width/2, height/2 + 20);
    
    // Blinking restart text
    const blinkRate = (frameCount % 60) < 30 ? 255 : 100;
    fill(255, blinkRate);
    textSize(20);
    text('Press SPACE to restart', width/2, height/2 + 70);
}

// Restart game
function keyPressed() {
    if (gameOver && keyCode === 32) { // SPACE key
        gameOver = false;
        score = 0;
        lives = 3;
        bricks = [];
        initializeGame();
    }
}
