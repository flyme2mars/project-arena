import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Texts in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
]  # Red, Green, Blue, Yellow

# Hexagon properties
CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 200  # Distance from center to vertex
ANGLE_STEP = 0.01  # Angular velocity in radians per frame

# Text setup
WORDS = ["STOP", "MAKING", "FUCKING", "BALLS"]
font = pygame.font.Font(None, 36)

# Create text objects
texts = []
for i, word in enumerate(WORDS):
    text_surface = font.render(word, True, COLORS[i])
    # Initial position inside the hexagon
    while True:
        pos = [
            random.randint(CENTER[0] - RADIUS + 50, CENTER[0] + RADIUS - 50),
            random.randint(CENTER[1] - RADIUS + 50, CENTER[1] + RADIUS - 50),
        ]
        # Ensure position is inside hexagon (simple distance check)
        if math.hypot(pos[0] - CENTER[0], pos[1] - CENTER[1]) < RADIUS - 20:
            break
    velocity = [random.uniform(-5, 5), random.uniform(-5, 5)]
    # Approximate text as a circle with radius as half the diagonal of its bounding box
    radius = math.hypot(text_surface.get_width() / 2, text_surface.get_height() / 2)
    texts.append(
        {
            "surface": text_surface,
            "pos": pos,
            "velocity": velocity,
            "radius": radius,
            "rect": text_surface.get_rect(),  # Will be updated each frame
        }
    )

# Main loop
clock = pygame.time.Clock()
angle = 0  # Hexagon rotation angle

while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update hexagon rotation
    angle += ANGLE_STEP
    # Calculate current vertices of the hexagon
    current_vertices = []
    for i in range(6):
        theta = 2 * math.pi * i / 6 + angle
        x = CENTER[0] + RADIUS * math.cos(theta)
        y = CENTER[1] + RADIUS * math.sin(theta)
        current_vertices.append((x, y))

    # Update each text object
    for text in texts:
        # Apply gravity (downward acceleration)
        text["velocity"][1] += 0.1  # Adjust gravity strength as needed

        # Apply friction (slows velocity)
        text["velocity"][0] *= 0.99
        text["velocity"][1] *= 0.99

        # Update position based on velocity
        text["pos"][0] += text["velocity"][0]
        text["pos"][1] += text["velocity"][1]

        # Collision detection with hexagon edges
        for i in range(6):
            p1 = current_vertices[i]
            p2 = current_vertices[(i + 1) % 6]
            # Find the closest point on the edge to the text's center
            line_vec = (p2[0] - p1[0], p2[1] - p1[1])
            to_text = (text["pos"][0] - p1[0], text["pos"][1] - p1[1])
            line_len_sq = line_vec[0] ** 2 + line_vec[1] ** 2
            if line_len_sq == 0:
                continue
            proj = max(
                0,
                min(
                    1,
                    (to_text[0] * line_vec[0] + to_text[1] * line_vec[1]) / line_len_sq,
                ),
            )
            closest = (p1[0] + proj * line_vec[0], p1[1] + proj * line_vec[1])
            dist_vec = (text["pos"][0] - closest[0], text["pos"][1] - closest[1])
            dist = math.hypot(dist_vec[0], dist_vec[1])

            # Check if the text's circle intersects the edge
            if dist < text["radius"]:
                # Collision detected
                # Calculate outward normal (perpendicular to edge)
                edge_vec = (p2[0] - p1[0], p2[1] - p1[1])
                normal = (-edge_vec[1], edge_vec[0])  # Rotate 90 degrees
                norm_len = math.hypot(normal[0], normal[1])
                if norm_len > 0:
                    normal = (normal[0] / norm_len, normal[1] / norm_len)
                # Ensure normal points outward
                to_center = (p1[0] - CENTER[0], p1[1] - CENTER[1])
                if normal[0] * to_center[0] + normal[1] * to_center[1] < 0:
                    normal = (-normal[0], -normal[1])

                # Reflect velocity over the normal
                v_dot_n = (
                    text["velocity"][0] * normal[0] + text["velocity"][1] * normal[1]
                )
                text["velocity"][0] -= 2 * v_dot_n * normal[0]
                text["velocity"][1] -= 2 * v_dot_n * normal[1]

                # Move text out of collision to prevent sticking
                overlap = text["radius"] - dist
                text["pos"][0] += normal[0] * overlap
                text["pos"][1] += normal[1] * overlap
                break  # Handle one collision per frame for simplicity

    # Render everything
    screen.fill(BLACK)  # Clear screen with black background

    # Draw the hexagon
    pygame.draw.polygon(screen, WHITE, current_vertices, 2)  # Width 2 for visibility

    # Draw the texts
    for text in texts:
        text["rect"].center = (int(text["pos"][0]), int(text["pos"][1]))
        screen.blit(text["surface"], text["rect"])

    pygame.display.flip()  # Update display
    clock.tick(60)  # Limit to 60 FPS
