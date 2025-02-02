import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)

# Neon colors for the rainbow effect
NEON_COLORS = [
    (255, 0, 128),  # Pink
    (255, 0, 255),  # Magenta
    (128, 0, 255),  # Purple
    (0, 0, 255),    # Blue
    (0, 255, 255),  # Cyan
    (0, 255, 0)     # Green
]

# Physics constants
GRAVITY = 0.5
FRICTION = 0.98
BOUNCE_FACTOR = 0.85

class Ball:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Apply friction
        self.vel_x *= FRICTION
        self.vel_y *= FRICTION
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, screen):
        # Draw glow effect
        for i in range(3):
            glow_radius = self.radius + i * 2
            alpha = 100 - i * 30
            glow_surface = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*NEON_COLORS[0][:3], alpha), 
                             (glow_radius + 2, glow_radius + 2), glow_radius)
            screen.blit(glow_surface, 
                       (int(self.x - glow_radius - 2), int(self.y - glow_radius - 2)))
        
        # Draw the main ball
        pygame.draw.circle(screen, NEON_COLORS[0], (int(self.x), int(self.y)), self.radius)

class Hexagon:
    def __init__(self, center_x, center_y, radius=150):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.angle = 0
        self.rotation_speed = 0.02

    def get_points(self):
        points = []
        for i in range(6):
            angle = self.angle + (i * math.pi / 3)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            points.append((x, y))
        return points

    def rotate(self):
        self.angle += self.rotation_speed

    def draw(self, screen):
        points = self.get_points()
        
        # Draw multiple layers for glow effect
        for i in range(3):
            width = 4 - i
            color_index = int((self.angle * 2) % len(NEON_COLORS))
            next_color_index = (color_index + 1) % len(NEON_COLORS)
            
            # Interpolate between colors
            progress = (self.angle * 2) % 1
            current_color = NEON_COLORS[color_index]
            next_color = NEON_COLORS[next_color_index]
            
            color = tuple(int(current_color[j] * (1 - progress) + next_color[j] * progress) for j in range(3))
            
            # Draw the hexagon with current interpolated color
            pygame.draw.polygon(screen, color, points, width)

    def check_collision(self, ball):
        points = self.get_points()
        for i in range(6):
            p1 = points[i]
            p2 = points[(i + 1) % 6]
            
            # Check collision with each wall segment
            self.handle_line_collision(ball, p1, p2)

    def handle_line_collision(self, ball, p1, p2):
        # Vector from p1 to p2
        wall_vec_x = p2[0] - p1[0]
        wall_vec_y = p2[1] - p1[1]
        
        # Vector from p1 to ball
        ball_vec_x = ball.x - p1[0]
        ball_vec_y = ball.y - p1[1]
        
        # Wall length squared
        wall_length_sq = wall_vec_x * wall_vec_x + wall_vec_y * wall_vec_y
        
        # Projection of ball vector onto wall vector
        t = max(0, min(1, (ball_vec_x * wall_vec_x + ball_vec_y * wall_vec_y) / wall_length_sq))
        
        # Closest point on the line
        closest_x = p1[0] + t * wall_vec_x
        closest_y = p1[1] + t * wall_vec_y
        
        # Distance from ball to closest point
        dist_x = ball.x - closest_x
        dist_y = ball.y - closest_y
        distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
        
        if distance <= ball.radius:
            # Normalize the normal vector
            normal_length = math.sqrt(dist_x * dist_x + dist_y * dist_y)
            if normal_length > 0:
                normal_x = dist_x / normal_length
                normal_y = dist_y / normal_length
                
                # Calculate relative velocity
                dot_product = (ball.vel_x * normal_x + ball.vel_y * normal_y)
                
                # Apply bounce
                ball.vel_x -= (1 + BOUNCE_FACTOR) * dot_product * normal_x
                ball.vel_y -= (1 + BOUNCE_FACTOR) * dot_product * normal_y
                
                # Move ball outside the wall
                overlap = ball.radius - distance
                ball.x += overlap * normal_x
                ball.y += overlap * normal_y

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")
    clock = pygame.time.Clock()

    ball = Ball(WIDTH // 2, HEIGHT // 2)
    hexagon = Hexagon(WIDTH // 2, HEIGHT // 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update
        ball.update()
        hexagon.rotate()
        hexagon.check_collision(ball)

        # Draw
        screen.fill(BLACK)
        hexagon.draw(screen)
        ball.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()