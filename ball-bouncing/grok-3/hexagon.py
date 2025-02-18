import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the window
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Define parameters
s = 10.0  # Radius of the hexagon (distance from center to vertex)
r = 0.5  # Ball radius
g = 9.8  # Gravity (units/s²)
omega = 1.0  # Angular speed of the hexagon (rad/s)
e = 0.8  # Coefficient of restitution (bounciness, 0 to 1)
f = 0.1  # Friction factor (reduces tangential velocity, 0 to 1)
dt = 1 / 60.0  # Time step (assuming 60 fps)
scale = 36.0  # Scale factor to map simulation units to pixels
center_x, center_y = width / 2, height / 2  # Center of the screen
N_trail = 10  # Number of trail positions

# Initial conditions in the rotating frame
theta = 0.0  # Initial rotation angle of the hexagon
r_rot = [0.0, 0.0]  # Initial position of the ball (x_rot, y_rot)
v_rot = [2.0, 0.0]  # Initial velocity of the ball (vx_rot, vy_rot)

# Hexagon vertices in the rotating frame (stationary)
vertices_rot = [
    [s * math.cos(2 * math.pi * k / 6), s * math.sin(2 * math.pi * k / 6)]
    for k in range(6)
]

# Trail for the ball
trail = []

# Main simulation loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the rotation angle
    theta += omega * dt

    # Compute gravity in the rotating frame
    g_rot = [-g * math.sin(theta), -g * math.cos(theta)]

    # Compute total acceleration in the rotating frame
    a_rot = [
        g_rot[0] + omega**2 * r_rot[0] + 2 * omega * v_rot[1],
        g_rot[1] + omega**2 * r_rot[1] - 2 * omega * v_rot[0],
    ]

    # Update velocity and position
    v_rot[0] += a_rot[0] * dt
    v_rot[1] += a_rot[1] * dt
    r_rot[0] += v_rot[0] * dt
    r_rot[1] += v_rot[1] * dt

    # Check for collisions with each side of the hexagon
    for k in range(6):
        P1 = vertices_rot[k]
        P2 = vertices_rot[(k + 1) % 6]
        V = [P2[0] - P1[0], P2[1] - P1[1]]
        length = math.sqrt(V[0] ** 2 + V[1] ** 2)
        N_outward = [V[1] / length, -V[0] / length]
        N = [-N_outward[0], -N_outward[1]]  # Inward normal
        d = (r_rot[0] - P1[0]) * N[0] + (r_rot[1] - P1[1]) * N[1]
        if d < r:
            penetration = r - d
            # Correct position
            r_rot[0] += penetration * N[0]
            r_rot[1] += penetration * N[1]
            # Update velocity with reflection and friction
            dot_v_N = v_rot[0] * N[0] + v_rot[1] * N[1]
            v_tangential = [v_rot[0] - dot_v_N * N[0], v_rot[1] - dot_v_N * N[1]]
            v_rot[0] = (1 - f) * v_tangential[0] - e * dot_v_N * N[0]
            v_rot[1] = (1 - f) * v_tangential[1] - e * dot_v_N * N[1]

    # Transform positions to the inertial frame
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    # Ball position
    x_inertial = r_rot[0] * cos_theta - r_rot[1] * sin_theta
    y_inertial = r_rot[0] * sin_theta + r_rot[1] * cos_theta
    ball_screen = [center_x + x_inertial * scale, center_y - y_inertial * scale]
    # Hexagon vertices
    hexagon_screen = [
        [
            center_x + (vx * cos_theta - vy * sin_theta) * scale,
            center_y - (vx * sin_theta + vy * cos_theta) * scale,
        ]
        for vx, vy in vertices_rot
    ]

    # Add current ball position to trail
    trail.append(ball_screen.copy())
    if len(trail) > N_trail:
        trail.pop(0)

    # Draw everything
    screen.fill((0, 0, 0))  # Black background

    # Draw the trail
    for i, pos in enumerate(trail):
        alpha = (i + 1) / len(trail)  # Ranges from 1/len(trail) to 1
        radius = int(r * scale * alpha)  # Scales from small to full size
        if radius > 0:
            color = (int(255 * alpha), 0, 0)  # Red intensity from dim to bright
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), radius)

    # Draw the hexagon outline
    pygame.draw.polygon(screen, (255, 255, 255), hexagon_screen, 3)

    # Draw the current ball
    pygame.draw.circle(
        screen, (255, 0, 0), (int(ball_screen[0]), int(ball_screen[1])), int(r * scale)
    )

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 fps
    clock.tick(60)

# Quit Pygame
pygame.quit()
