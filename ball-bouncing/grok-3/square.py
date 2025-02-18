import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the window
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Define parameters
s = 10.0  # Side length of the square
r = 0.5  # Ball radius
g = 9.8  # Gravity (units/s²)
omega = 1.0  # Angular speed of the square (rad/s)
e = 0.8  # Coefficient of restitution (bounciness, 0 to 1)
f = 0.1  # Friction factor (reduces tangential velocity, 0 to 1)
dt = 1 / 60.0  # Time step (assuming 60 fps)
scale = 500 / s  # Scale factor to map simulation units to pixels
center_x, center_y = width / 2, height / 2  # Center of the screen

# Initial conditions in the rotating frame
theta = 0.0  # Initial rotation angle of the square
r_rot = [0.0, 0.0]  # Initial position of the ball (x_rot, y_rot)
v_rot = [2.0, 0.0]  # Initial velocity of the ball (vx_rot, vy_rot)

# Square vertices in the rotating frame (stationary)
vertices_rot = [
    [s / 2, s / 2],  # Top-right
    [-s / 2, s / 2],  # Top-left
    [-s / 2, -s / 2],  # Bottom-left
    [s / 2, -s / 2],  # Bottom-right
]

# Main simulation loop
running = True
while running:
    # Handle events (e.g., closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the rotation angle
    theta += omega * dt

    # Compute gravity in the rotating frame
    # In the inertial frame, gravity is along -y, so in the rotating frame,
    # it rotates with the frame: g_rot = R(-theta) * (0, -g)
    g_rot = [-g * math.sin(theta), -g * math.cos(theta)]

    # Compute total acceleration in the rotating frame
    # a_rot = g_rot + centrifugal_force + Coriolis_force
    # Centrifugal force: omega² * (x_rot, y_rot)
    # Coriolis force: 2 * omega * (v_y_rot, -v_x_rot)
    a_rot = [
        g_rot[0] + omega**2 * r_rot[0] + 2 * omega * v_rot[1],
        g_rot[1] + omega**2 * r_rot[1] - 2 * omega * v_rot[0],
    ]

    # Update velocity using acceleration (v = v + a * dt)
    v_rot[0] += a_rot[0] * dt
    v_rot[1] += a_rot[1] * dt

    # Update position using velocity (r = r + v * dt)
    r_rot[0] += v_rot[0] * dt
    r_rot[1] += v_rot[1] * dt

    # Check for collisions with the square's walls
    # Right wall (x = s/2)
    if r_rot[0] > s / 2 - r:
        v_rot[0] = -e * v_rot[0]  # Reflect normal velocity (x)
        v_rot[1] *= 1 - f  # Reduce tangential velocity (y) due to friction
        r_rot[0] = s / 2 - r  # Correct position to prevent penetration
    # Left wall (x = -s/2)
    elif r_rot[0] < -s / 2 + r:
        v_rot[0] = -e * v_rot[0]  # Reflect normal velocity (x)
        v_rot[1] *= 1 - f  # Reduce tangential velocity (y)
        r_rot[0] = -s / 2 + r  # Correct position
    # Top wall (y = s/2)
    if r_rot[1] > s / 2 - r:
        v_rot[1] = -e * v_rot[1]  # Reflect normal velocity (y)
        v_rot[0] *= 1 - f  # Reduce tangential velocity (x)
        r_rot[1] = s / 2 - r  # Correct position
    # Bottom wall (y = -s/2)
    elif r_rot[1] < -s / 2 + r:
        v_rot[1] = -e * v_rot[1]  # Reflect normal velocity (y)
        v_rot[0] *= 1 - f  # Reduce tangential velocity (x)
        r_rot[1] = -s / 2 + r  # Correct position

    # Transform positions to the inertial frame for display
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    # Ball position in the inertial frame
    x_inertial = r_rot[0] * cos_theta - r_rot[1] * sin_theta
    y_inertial = r_rot[0] * sin_theta + r_rot[1] * cos_theta

    # Square vertices in the inertial frame
    vertices_inertial = []
    for vx, vy in vertices_rot:
        vx_inertial = vx * cos_theta - vy * sin_theta
        vy_inertial = vx * sin_theta + vy * cos_theta
        vertices_inertial.append([vx_inertial, vy_inertial])

    # Convert to screen coordinates for drawing
    # Ball
    ball_screen = [
        center_x + x_inertial * scale,
        center_y - y_inertial * scale,  # Flip y-axis (Pygame has y increasing downward)
    ]
    # Square vertices
    square_screen = []
    for vx, vy in vertices_inertial:
        sx = center_x + vx * scale
        sy = center_y - vy * scale
        square_screen.append([sx, sy])

    # Draw everything
    screen.fill((255, 255, 255))  # White background

    # Draw the square (outline)
    pygame.draw.lines(screen, (0, 0, 0), True, square_screen, 2)

    # Draw the ball
    pygame.draw.circle(
        screen, (255, 0, 0), (int(ball_screen[0]), int(ball_screen[1])), int(r * scale)
    )

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 fps
    clock.tick(60)

# Quit Pygame
pygame.quit()
