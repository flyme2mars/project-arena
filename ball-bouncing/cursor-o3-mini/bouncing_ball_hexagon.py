import pygame
import math
import sys
import colorsys
import random

# ----- Simulation Settings -----
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Physics parameters (tweak these for different behavior)
GRAVITY = 500  # pixels/s^2
AIR_FRICTION = 0.999  # simple air drag each frame
RESTITUTION = 0.9  # How "bouncy" the collisions are (0 < r <= 1)
COLLISION_FRICTION = 0.8  # Coefficient to reduce the tangential component on collision

# Hexagon parameters
HEX_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
HEX_RADIUS = 250
hexagon_angle = 0.0  # initial rotation angle (radians)
HEX_ANGULAR_SPEED = 1.0  # radians/s (constant angular speed)

# Ball parameters
ball_radius = 10
# Start at the center of the screen (inside the hexagon)
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
# Some initial velocity (pixels per second)
ball_velocity = [200, -150]


# ----- Helper Functions -----
def vector_length(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def vector_normalize(v):
    length = vector_length(v)
    if length == 0:
        return (0, 0)
    return (v[0] / length, v[1] / length)


def vector_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def vector_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def vector_scale(v, s):
    return (v[0] * s, v[1] * s)


def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def get_hexagon_vertices(center, radius, angle):
    """
    Returns the vertices (as a list of (x,y) tuples) of a regular hexagon
    with the given center and radius. The hexagon is rotated by "angle" radians.
    """
    vertices = []
    for i in range(6):
        theta = angle + i * (2 * math.pi / 6)
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        vertices.append((x, y))
    return vertices


def closest_point_on_segment(p, a, b):
    """
    For point p and segment ab, returns the point on ab that is closest to p.
    """
    ax, ay = a
    bx, by = b
    px, py = p
    abx = bx - ax
    aby = by - ay
    ab_length_sq = abx * abx + aby * aby
    if ab_length_sq == 0:
        return a  # a and b are the same point
    t = ((px - ax) * abx + (py - ay) * aby) / ab_length_sq
    t = max(0, min(1, t))
    return (ax + t * abx, ay + t * aby)


# ----- Main Program -----
def main():
    global hexagon_angle

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Modern Bouncing Ball in a Spinning Hexagon")
    clock = pygame.time.Clock()

    # Create a trail surface for the ball (with per-pixel alpha) to achieve a glowing trail.
    ball_trail_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ball_trail_surface.fill((0, 0, 0, 0))

    # Generate a small star field for a modern animated background.
    stars = []
    for _ in range(50):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        phase = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.0)
        stars.append({"pos": (x, y), "phase": phase, "speed": speed})

    running = True
    while running:
        # Calculate delta time (in seconds)
        dt = clock.tick(FPS) / 1000.0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Update Ball Physics ---
        ball_velocity[1] += GRAVITY * dt
        ball_velocity[0] *= AIR_FRICTION
        ball_velocity[1] *= AIR_FRICTION
        ball_pos[0] += ball_velocity[0] * dt
        ball_pos[1] += ball_velocity[1] * dt

        # --- Collision Detection and Response ---
        # Check collisions with each edge of the hexagon
        vertices = get_hexagon_vertices(HEX_CENTER, HEX_RADIUS, hexagon_angle)
        for i in range(len(vertices)):
            a = vertices[i]
            b = vertices[(i + 1) % len(vertices)]
            cp = closest_point_on_segment(ball_pos, a, b)
            diff = vector_sub(ball_pos, cp)
            dist = vector_length(diff)

            if dist < ball_radius:
                # Collision detected: push the ball out and reflect its velocity.
                penetration = ball_radius - dist

                if dist != 0:
                    normal = vector_normalize(diff)
                else:
                    edge_vec = vector_sub(b, a)
                    normal = vector_normalize((-edge_vec[1], edge_vec[0]))

                ball_pos[0] += normal[0] * penetration
                ball_pos[1] += normal[1] * penetration

                # Determine the wall's velocity at the contact point (due to hexagon rotation)
                r = vector_sub(cp, HEX_CENTER)
                wall_velocity = (-HEX_ANGULAR_SPEED * r[1], HEX_ANGULAR_SPEED * r[0])

                # Relative velocity (ball velocity relative to the wall)
                rel_vel = (
                    ball_velocity[0] - wall_velocity[0],
                    ball_velocity[1] - wall_velocity[1],
                )
                rel_normal = dot(rel_vel, normal)

                if rel_normal < 0:
                    # Reflect the velocity along the collision normal, applying restitution
                    new_rel_vel = (
                        rel_vel[0] - (1 + RESTITUTION) * rel_normal * normal[0],
                        rel_vel[1] - (1 + RESTITUTION) * rel_normal * normal[1],
                    )

                    # Apply friction to the tangential component
                    rel_vel_dot = dot(new_rel_vel, normal)
                    normal_component = vector_scale(normal, rel_vel_dot)
                    tangent_component = vector_sub(new_rel_vel, normal_component)
                    tangent_component = vector_scale(
                        tangent_component, COLLISION_FRICTION
                    )
                    new_rel_vel = vector_add(normal_component, tangent_component)

                    ball_velocity[0] = new_rel_vel[0] + wall_velocity[0]
                    ball_velocity[1] = new_rel_vel[1] + wall_velocity[1]

        # --- Update the Hexagon's Rotation ---
        hexagon_angle += HEX_ANGULAR_SPEED * dt

        # --- Dynamic Colors & Background Animations ---
        elapsed_time = pygame.time.get_ticks() / 1000.0

        # Compute dynamic colors using HSV (cycle hues over time)
        hue_hex = (elapsed_time * 0.1) % 1.0
        hexagon_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue_hex, 1, 1))
        hue_ball = (elapsed_time * 0.2 + 0.5) % 1.0
        ball_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue_ball, 1, 1))

        # --- Drawing ---
        # Fill the background with black
        screen.fill((0, 0, 0))

        # Draw the twinkling star field
        for star in stars:
            x, y = star["pos"]
            brightness = 128 + 127 * math.sin(
                elapsed_time * star["speed"] + star["phase"]
            )
            b = max(0, min(255, int(brightness)))
            pygame.draw.circle(screen, (b, b, b), (x, y), 2)

        # Convert hexagon vertices to integers for drawing
        int_vertices = [(int(x), int(y)) for (x, y) in vertices]

        # Create a glow effect for the hexagon using a temporary surface with per-pixel alpha
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Outer glow (thick, translucent edge)
        glow_color = (hexagon_color[0], hexagon_color[1], hexagon_color[2], 50)
        pygame.draw.polygon(glow_surface, glow_color, int_vertices, 15)
        # Middle glow (medium thickness)
        glow_color = (hexagon_color[0], hexagon_color[1], hexagon_color[2], 100)
        pygame.draw.polygon(glow_surface, glow_color, int_vertices, 7)
        # Sharp hexagon outline
        pygame.draw.polygon(glow_surface, hexagon_color, int_vertices, 3)
        screen.blit(glow_surface, (0, 0))

        # Update the ball trail surface to create a motion blur (fading old trails)
        ball_trail_surface.fill((0, 0, 0, 20))
        # Draw a glowing circle on the trail surface
        pygame.draw.circle(
            ball_trail_surface,
            (ball_color[0], ball_color[1], ball_color[2], 80),
            (int(ball_pos[0]), int(ball_pos[1])),
            ball_radius + 4,
        )
        # Blit the trail onto the main screen
        screen.blit(ball_trail_surface, (0, 0))

        # Draw the current ball (crisp circle) on top
        pygame.draw.circle(
            screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
