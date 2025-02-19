import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ball Bouncing in Spinning Hexagon")

# Define colors
BLACK = (0, 0, 0)  # Background color
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
COLORS = [
    RED,
    GREEN,
    BLUE,
    YELLOW,
    CYAN,
    MAGENTA,
]  # Vibrant colors for hexagon and particles

# Hexagon parameters
center = (width / 2, height / 2)  # Center of the screen
radius = 200  # Distance from center to hexagon vertex
theta = 0  # Rotation angle (radians)
omega = 0.01  # Angular speed (radians per frame)

# Pre-calculate local hexagon vertices (unrotated)
local_vertices = [
    (radius * math.cos(2 * math.pi * k / 6), radius * math.sin(2 * math.pi * k / 6))
    for k in range(6)
]

# Pre-calculate inward normals for each wall (for collision detection)
local_normals = []
for k in range(6):
    v1 = local_vertices[k]
    v2 = local_vertices[(k + 1) % 6]
    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    normal = (-dy, dx)  # Perpendicular to wall
    length = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
    normal = (normal[0] / length, normal[1] / length)
    local_normals.append(normal)

# Distance from center to each wall (apothem)
h = radius * math.sqrt(3) / 2

# Ball parameters
ball_radius = 10
ball_pos = [center[0], center[1]]  # Start at center
ball_vel = [random.uniform(-5, 5), random.uniform(-10, -5)]  # Initial velocity
trail = []  # Store trail positions

# Physics parameters
gravity = 0.1  # Downward acceleration per frame
friction = 0.95  # Velocity reduction after bounce


# Particle class for bounce effects
class Particle:
    def __init__(self, pos, vel, color, lifetime):
        self.pos = list(pos)
        self.vel = list(vel)
        self.color = color
        self.lifetime = lifetime

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / 30))
            color = (*self.color[:3], alpha)
            pygame.draw.circle(screen, color, (int(self.pos[0]), int(self.pos[1])), 2)


# Particle list
particles = []


# Function to rotate a point by an angle
def rotate(point, angle):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x, y = point
    return (cos_a * x - sin_a * y, sin_a * x + cos_a * y)


# Clock for frame rate control
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    theta += omega
    theta %= 2 * math.pi  # Keep angle in [0, 2π)

    # Apply gravity to ball velocity
    ball_vel[1] += gravity

    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Add current position to trail (limited to 50 points)
    trail.append((ball_pos[0], ball_pos[1]))
    if len(trail) > 50:
        trail.pop(0)

    # Transform ball position to hexagon's rotating frame
    rel_pos = (ball_pos[0] - center[0], ball_pos[1] - center[1])
    ball_pos_rot = rotate(rel_pos, -theta)

    # Check collisions with hexagon walls
    signed_distances = [
        local_normals[k][0] * ball_pos_rot[0]
        + local_normals[k][1] * ball_pos_rot[1]
        + h
        for k in range(6)
    ]
    min_d = min(signed_distances)
    wall_idx = signed_distances.index(min_d)

    # Handle collision if ball is too close to a wall
    if min_d < ball_radius:
        # Transform velocity to rotating frame
        ball_vel_rot = rotate(ball_vel, -theta)

        # Reflect velocity across wall normal
        n = local_normals[wall_idx]
        dot = ball_vel_rot[0] * n[0] + ball_vel_rot[1] * n[1]
        ball_vel_rot = (
            ball_vel_rot[0] - 2 * dot * n[0],
            ball_vel_rot[1] - 2 * dot * n[1],
        )

        # Apply friction
        ball_vel_rot = (ball_vel_rot[0] * friction, ball_vel_rot[1] * friction)

        # Transform velocity back to world frame
        ball_vel = list(rotate(ball_vel_rot, theta))

        # Adjust ball position to prevent sinking into wall
        adjustment = ((ball_radius - min_d) * n[0], (ball_radius - min_d) * n[1])
        ball_pos_rot = (
            ball_pos_rot[0] + adjustment[0],
            ball_pos_rot[1] + adjustment[1],
        )

        # Transform position back to world frame
        rotated_back = rotate(ball_pos_rot, theta)
        ball_pos = [center[0] + rotated_back[0], center[1] + rotated_back[1]]

        # Add colorful particles on bounce
        for _ in range(10):
            particle_vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
            particles.append(
                Particle(ball_pos, particle_vel, random.choice(COLORS), 30)
            )

    # Update particles
    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)

    # Draw everything
    screen.fill(BLACK)  # Black background

    # Draw spinning hexagon with colorful sides
    world_vertices = [
        (center[0] + rotate(v, theta)[0], center[1] + rotate(v, theta)[1])
        for v in local_vertices
    ]
    world_vertices = [(int(x), int(y)) for x, y in world_vertices]
    for i in range(6):
        start_pos = world_vertices[i]
        end_pos = world_vertices[(i + 1) % 6]
        pygame.draw.line(screen, COLORS[i % len(COLORS)], start_pos, end_pos, 3)

    # Draw ball trail (fading white)
    for i, pos in enumerate(trail):
        if len(trail) > 1:
            factor = i / (len(trail) - 1)
        else:
            factor = 1
        radius = int(1 + (ball_radius - 1) * factor)
        brightness = int(255 * factor)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), radius)

    # Draw ball (solid white)
    pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # Draw colorful particles
    for particle in particles:
        particle.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap frame rate at 60 FPS
    clock.tick(60)

# Clean up
pygame.quit()
