import pygame
from pygame.locals import *
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Snake - Space Adventure")

# Set up the clock for controlling frame rate
clock = pygame.time.Clock()

# Define colors
BLACK = (0, 0, 0)  # Background
GRAY = (100, 100, 100)  # Asteroids
DARK_GRAY = (70, 70, 70)  # Asteroid shading
SILVER = (192, 192, 192)  # Spaceship
WHITE = (255, 255, 255)  # Stars, text, particles
YELLOW = (255, 255, 0)  # Food stars

# Game states
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Game variables
head_y = height / 2
y_velocity = 0
gravity = 0.5
flap_strength = -10
speed = 5
segment_spacing = 20
D = 4
head_history = []
snake_length = 1
obstacles = []  # [x, gap_center, gap_height]
food = []  # [x, y]
particles = []  # [x, y, vx, vy, life]
score = 0
ticks = 0
state = STATE_START

# Background scrolling
bg_x = 0
bg_speed = 1
stars = [
    (random.uniform(0, width), random.uniform(0, height), random.uniform(1, 2))
    for _ in range(200)
]


# Function to reset game variables
def reset_game():
    global head_y, y_velocity, head_history, snake_length, obstacles, food, particles, score, ticks, state
    head_y = height / 2
    y_velocity = 0
    head_history = []
    snake_length = 1
    obstacles = []
    food = []
    particles = []
    score = 0
    ticks = 0
    state = STATE_PLAYING


# Function to check if a position is safe from obstacles
def is_position_safe(x, y, obstacles):
    time_to_reach = (x - 100) / speed
    for obs in obstacles:
        obs_x_at_time = obs[0] - speed * time_to_reach
        if 75 <= obs_x_at_time <= 125:
            gap_top = obs[1] - obs[2] / 2
            gap_bottom = obs[1] + obs[2] / 2
            if not (gap_top < y < gap_bottom):
                return False
    return True


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if state == STATE_START and event.key == K_SPACE:
                reset_game()
            elif state == STATE_PLAYING and event.key == K_SPACE:
                y_velocity = flap_strength
            elif state == STATE_GAME_OVER and event.key == K_SPACE:
                reset_game()
            elif state == STATE_GAME_OVER and event.key == K_q:
                pygame.quit()
                exit()

    if state == STATE_START:
        # Render start screen
        screen.fill(BLACK)
        bg_x -= bg_speed
        if bg_x <= -width:
            bg_x += width
        for star in stars:
            star_x = (star[0] - bg_x) % width
            pygame.draw.circle(screen, WHITE, (int(star_x), int(star[1])), int(star[2]))

        # Centered title
        font = pygame.font.SysFont("Arial", 36)  # Reduced from 48
        text_string = "Flappy Snake - Space Adventure"
        text = font.render(text_string, True, WHITE)
        text_width, text_height = font.size(text_string)
        x = (width / 2) - (text_width / 2)
        y = height / 2 - 50
        screen.blit(text, (x, y))

        # Centered instructions
        font = pygame.font.SysFont("Arial", 24)
        text_string = "Press SPACE to Start"
        text = font.render(text_string, True, WHITE)
        text_width, text_height = font.size(text_string)
        x = (width / 2) - (text_width / 2)
        y = height / 2 + 50
        screen.blit(text, (x, y))

        pygame.display.flip()
        clock.tick(60)
        continue

    elif state == STATE_PLAYING:
        ticks += 1

        # Update snake
        y_velocity += gravity
        head_y += y_velocity
        if head_y < 0 or head_y > height:
            state = STATE_GAME_OVER
        head_history.append(head_y)
        if len(head_history) > 1000:
            head_history = head_history[-1000:]

        # Update obstacles
        for obs in obstacles:
            obs[0] -= speed
        obstacles = [obs for obs in obstacles if obs[0] > -50]
        if len(obstacles) < 3:
            last_x = max([obs[0] for obs in obstacles]) if obstacles else width
            new_x = last_x + 300
            gap_center = random.uniform(100, height - 100)
            gap_height = 150
            obstacles.append([new_x, gap_center, gap_height])

        # Update and generate food
        for f in food:
            f[0] -= speed
        food = [f for f in food if f[0] > -10]
        if len(food) < 2 and random.random() < 0.05:
            attempts = 0
            while attempts < 10:
                food_x = width + random.uniform(0, 300)
                food_y = random.uniform(50, height - 50)
                if is_position_safe(food_x, food_y, obstacles):
                    food.append([food_x, food_y])
                    break
                attempts += 1

        # Update particles
        for p in particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 1
        particles = [p for p in particles if p[4] > 0]

        # Collision with food
        head_rect = pygame.Rect(100 - 10, head_y - 10, 20, 20)
        for f in food[:]:
            f_rect = pygame.Rect(f[0] - 5, f[1] - 5, 10, 10)
            if head_rect.colliderect(f_rect):
                food.remove(f)
                snake_length += 1
                score += 1
                for _ in range(10):
                    vx = random.uniform(-2, 2)
                    vy = random.uniform(-2, 2)
                    particles.append([f[0], f[1], vx, vy, 30])

        # Collision with obstacles
        for obs in obstacles:
            upper_rect = pygame.Rect(obs[0], 0, 50, obs[1] - obs[2] / 2)
            lower_rect = pygame.Rect(
                obs[0], obs[1] + obs[2] / 2, 50, height - (obs[1] + obs[2] / 2)
            )
            if head_rect.colliderect(upper_rect) or head_rect.colliderect(lower_rect):
                state = STATE_GAME_OVER

        # Rendering
        screen.fill(BLACK)
        bg_x -= bg_speed
        if bg_x <= -width:
            bg_x += width
        for star in stars:
            star_x = (star[0] - bg_x) % width
            pygame.draw.circle(screen, WHITE, (int(star_x), int(star[1])), int(star[2]))

        # Draw asteroid obstacles
        for obs in obstacles:
            for y in range(0, int(obs[1] - obs[2] / 2), 20):
                x_offset = random.randint(-5, 5)
                pygame.draw.circle(screen, GRAY, (int(obs[0] + 25 + x_offset), y), 15)
                pygame.draw.circle(
                    screen, DARK_GRAY, (int(obs[0] + 25 + x_offset), y), 10
                )
            for y in range(int(obs[1] + obs[2] / 2), height, 20):
                x_offset = random.randint(-5, 5)
                pygame.draw.circle(screen, GRAY, (int(obs[0] + 25 + x_offset), y), 15)
                pygame.draw.circle(
                    screen, DARK_GRAY, (int(obs[0] + 25 + x_offset), y), 10
                )

        # Draw food
        for f in food:
            scale = 5 + 3 * math.sin(ticks / 15.0 + f[0])
            pygame.draw.circle(screen, YELLOW, (int(f[0]), int(f[1])), int(scale))

        # Draw particles
        for p in particles:
            pygame.draw.circle(screen, WHITE, (int(p[0]), int(p[1])), 2)

        # Draw snake (spaceship)
        points = [(100, head_y), (80, head_y - 15), (80, head_y + 15)]
        pygame.draw.polygon(screen, SILVER, points)
        for k in range(1, snake_length):
            if len(head_history) > k * D:
                seg_y = head_history[-1 - k * D]
                seg_x = 100 - k * segment_spacing
                if seg_x > 0:
                    gray_value = max(192 - k * 20, 100)
                    color = (gray_value, gray_value, gray_value)
                    seg_points = [
                        (seg_x, seg_y),
                        (seg_x - 10, seg_y - 5),
                        (seg_x - 10, seg_y + 5),
                    ]
                    pygame.draw.polygon(screen, color, seg_points)

        # Draw score
        font = pygame.font.SysFont("Arial", 36)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    elif state == STATE_GAME_OVER:
        # Render game over screen
        screen.fill(BLACK)
        bg_x -= bg_speed
        if bg_x <= -width:
            bg_x += width
        for star in stars:
            star_x = (star[0] - bg_x) % width
            pygame.draw.circle(screen, WHITE, (int(star_x), int(star[1])), int(star[2]))

        # Centered "Game Over"
        font = pygame.font.SysFont("Arial", 72)
        text_string = "Game Over"
        text = font.render(text_string, True, WHITE)
        text_width, text_height = font.size(text_string)
        x = (width / 2) - (text_width / 2)
        y = height / 2 - 100
        screen.blit(text, (x, y))

        # Centered score
        font = pygame.font.SysFont("Arial", 36)
        text_string = f"Score: {score}"
        text = font.render(text_string, True, WHITE)
        text_width, text_height = font.size(text_string)
        x = (width / 2) - (text_width / 2)
        y = height / 2
        screen.blit(text, (x, y))

        # Centered restart/quit instructions
        text_string = "Press SPACE to Restart or Q to Quit"
        text = font.render(text_string, True, WHITE)
        text_width, text_height = font.size(text_string)
        x = (width / 2) - (text_width / 2)
        y = height / 2 + 50
        screen.blit(text, (x, y))

        pygame.display.flip()
        clock.tick(60)

pygame.quit()
