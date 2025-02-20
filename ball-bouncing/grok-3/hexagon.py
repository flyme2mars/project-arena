import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Hexagon properties
HEX_RADIUS = 300
center = (WIDTH // 2, HEIGHT // 2)
rotation_angle = 0
rotation_speed = 0.5  # degrees per frame

# Ball properties
BALL_RADIUS = 20
ball_pos = [WIDTH // 2, HEIGHT // 2 - 200]  # Start near top
ball_vel = [random.uniform(-5, 5), 0]  # Initial velocity
GRAVITY = 0.2
FRICTION = 0.99  # Velocity reduction per frame
BOUNCE = 0.8  # Velocity reduction on bounce

# Clock for controlling frame rate
clock = pygame.time.Clock()


def rotate_point(point, angle, center_point):
    """Rotate a point around a center point by given angle in degrees"""
    angle_rad = math.radians(angle)
    x, y = point[0] - center_point[0], point[1] - center_point[1]
    new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return [new_x + center_point[0], new_y + center_point[1]]


def get_hexagon_vertices(center, radius, angle):
    """Calculate vertices of a rotating hexagon"""
    vertices = []
    for i in range(6):
        vertex_angle = math.radians(60 * i + angle)
        x = center[0] + radius * math.cos(vertex_angle)
        y = center[1] + radius * math.sin(vertex_angle)
        vertices.append([x, y])
    return vertices


def line_intersection(p1, p2, p3, p4):
    """Find intersection point between two lines, return None if no intersection"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    # Check if intersection is within line segments
    if (
        min(x1, x2) <= px <= max(x1, x2)
        and min(y1, y2) <= py <= max(y1, y2)
        and min(x3, x4) <= px <= max(x3, x4)
        and min(y3, y4) <= py <= max(y3, y4)
    ):
        return (px, py)
    return None


def reflect_velocity(pos, vel, wall_start, wall_end):
    """Calculate new velocity after hitting a wall"""
    # Wall vector
    wx = wall_end[0] - wall_start[0]
    wy = wall_end[1] - wall_start[1]

    # Normal vector
    nx = -wy
    ny = wx
    n_length = math.sqrt(nx * nx + ny * ny)
    nx /= n_length
    ny /= n_length

    # Dot product of velocity and normal
    dot = vel[0] * nx + vel[1] * ny

    # Reflect velocity
    new_vel_x = vel[0] - 2 * dot * nx
    new_vel_y = vel[1] - 2 * dot * ny

    return [new_vel_x * BOUNCE, new_vel_y * BOUNCE]


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update rotation
    rotation_angle += rotation_speed

    # Apply gravity and friction
    ball_vel[1] += GRAVITY
    ball_vel[0] *= FRICTION
    ball_vel[1] *= FRICTION

    # Calculate new position
    new_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]

    # Get hexagon vertices
    vertices = get_hexagon_vertices(center, HEX_RADIUS, rotation_angle)

    # Check collision with each wall
    for i in range(6):
        wall_start = vertices[i]
        wall_end = vertices[(i + 1) % 6]

        intersection = line_intersection(ball_pos, new_pos, wall_start, wall_end)

        if intersection:
            # Move ball to intersection point
            ball_pos = list(intersection)
            # Reflect velocity
            ball_vel = reflect_velocity(ball_pos, ball_vel, wall_start, wall_end)
            break
    else:
        # No collision, update position normally
        ball_pos = new_pos

    # Clear screen
    screen.fill(BLACK)

    # Draw hexagon
    pygame.draw.polygon(screen, WHITE, vertices, 2)

    # Draw ball
    pygame.draw.circle(screen, RED, [int(ball_pos[0]), int(ball_pos[1])], BALL_RADIUS)

    # Update display
    pygame.display.flip()

    # Control frame rate
    clock.tick(60)

pygame.quit()
