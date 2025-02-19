import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800  # Window size
FPS = 60  # Frames per second
DT = 0.01  # Time step for simulation
GRAVITY = 0.1  # Gravity acceleration
OMEGA = 1.0  # Angular velocity of the square (rad/s)
E = 0.8  # Coefficient of restitution (elasticity)
F = 0.9  # Friction factor (reduces tangential velocity)
SCALE = 300  # Scale from simulation units to pixels

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Bouncing in Spinning Square")
clock = pygame.time.Clock()

# Ball properties
x, y = 0, 0  # Initial position at center
v_x, v_y = 1, 0  # Initial velocity

# Simulation time
t = 0


# Function to handle collision with the square's walls
def handle_collision(n_rot, theta):
    global x, y, v_x, v_y
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    # Compute velocity in the rotating frame
    omega_cross_r = (-OMEGA * y, OMEGA * x)
    v_lab_minus_omega_cross_r = (v_x + OMEGA * y, v_y - OMEGA * x)
    v_rot_x = (
        v_lab_minus_omega_cross_r[0] * cos_theta
        + v_lab_minus_omega_cross_r[1] * sin_theta
    )
    v_rot_y = (
        -v_lab_minus_omega_cross_r[0] * sin_theta
        + v_lab_minus_omega_cross_r[1] * cos_theta
    )
    v_rot = (v_rot_x, v_rot_y)

    # Decompose velocity into normal and tangential components
    v_normal_mag = v_rot[0] * n_rot[0] + v_rot[1] * n_rot[1]
    v_normal = (v_normal_mag * n_rot[0], v_normal_mag * n_rot[1])
    v_tangential = (v_rot[0] - v_normal[0], v_rot[1] - v_normal[1])

    # Apply collision response with elasticity and friction
    v_rot_after = (
        -E * v_normal[0] + F * v_tangential[0],
        -E * v_normal[1] + F * v_tangential[1],
    )

    # Transform velocity back to lab frame
    v_lab_after_x = (
        cos_theta * v_rot_after[0] - sin_theta * v_rot_after[1]
    ) + omega_cross_r[0]
    v_lab_after_y = (
        sin_theta * v_rot_after[0] + cos_theta * v_rot_after[1]
    ) + omega_cross_r[1]
    v_x, v_y = v_lab_after_x, v_lab_after_y


# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update ball velocity due to gravity
    v_y -= GRAVITY * DT

    # Update ball position
    x += v_x * DT
    y += v_y * DT

    # Compute rotation angle of the square
    theta = OMEGA * t
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    # Compute ball position in the rotating frame
    x_rot = x * cos_theta + y * sin_theta
    y_rot = -x * sin_theta + y * cos_theta

    # Check for collisions with the square's sides (square size is 2x2 in simulation units)
    if x_rot > 1 and abs(y_rot) <= 1:
        handle_collision((-1, 0), theta)  # Right side
    elif x_rot < -1 and abs(y_rot) <= 1:
        handle_collision((1, 0), theta)  # Left side
    elif y_rot > 1 and abs(x_rot) <= 1:
        handle_collision((0, -1), theta)  # Top side
    elif y_rot < -1 and abs(x_rot) <= 1:
        handle_collision((0, 1), theta)  # Bottom side

    # Clear the screen
    screen.fill((0, 0, 0))  # Black background

    # Draw the spinning square
    vertices = [
        (1, 1),
        (1, -1),
        (-1, -1),
        (-1, 1),
    ]  # Square corners in simulation units
    rotated_vertices = [
        (vx * cos_theta - vy * sin_theta, vx * sin_theta + vy * cos_theta)
        for vx, vy in vertices
    ]
    screen_vertices = [
        (WIDTH // 2 + vx * SCALE, HEIGHT // 2 - vy * SCALE)
        for vx, vy in rotated_vertices
    ]
    pygame.draw.lines(screen, (255, 255, 255), True, screen_vertices, 2)

    # Draw the ball
    screen_x = WIDTH // 2 + x * SCALE
    screen_y = HEIGHT // 2 - y * SCALE
    pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 10)

    # Update the display
    pygame.display.flip()

    # Increment time and control frame rate
    t += DT
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
