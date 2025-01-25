import math
import pygame
from arrow import draw_arrow

class Charge:
    def __init__(self, x, y, q):
        self.x = x
        self.y = y
        self.q = q

class ElectricField:
    def __init__(self, screen, charges, screen_width, screen_height, scale=30, spacing=50, min_distance=30, max_distance=300):
        self.screen = screen
        self.charges = charges
        self.scale = scale
        self.spacing = spacing
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x_vals = [x for x in range(-screen_width // 2, screen_width // 2, spacing)]
        self.y_vals = [y for y in range(-screen_height // 2, screen_height // 2, spacing)]

    def calculate_electric_field(self, x, y):
        """Calculate the net electric field at (x, y) due to all charges."""
        Ex, Ey = 0, 0
        for charge in self.charges:
            dx = x - charge.x
            dy = y - charge.y
            r_squared = dx**2 + dy**2
            if r_squared == 0:
                # Skip calculation for this charge if the field point coincides with the charge
                continue
            r = math.sqrt(r_squared)
            field_magnitude = charge.q / r_squared
            Ex += field_magnitude * (dx / r)
            Ey += field_magnitude * (dy / r)
        return Ex, Ey

    def should_plot_arrow(self, x, y):
        """Determine if an arrow should be plotted at (x, y)."""
        for charge in self.charges:
            distance = math.sqrt((x - charge.x)**2 + (y - charge.y)**2)
            if distance < self.min_distance or distance > self.max_distance:
                return False
        return True

    def plot(self):
        """Plot the electric field vectors."""
        for x in self.x_vals:
            for y in self.y_vals:
                if not self.should_plot_arrow(x, y):
                    continue

                Ex, Ey = self.calculate_electric_field(x, y)
                magnitude = math.sqrt(Ex**2 + Ey**2)

                # Skip invalid or zero-magnitude vectors
                if magnitude == 0 or math.isnan(magnitude):
                    continue

                # Normalize the vector for consistent arrow lengths
                Ex /= magnitude
                Ey /= magnitude

                start_pos = pygame.Vector2(*to_screen_coordinates(x, y, self.screen_width, self.screen_height))
                end_x = x + Ex * self.scale
                end_y = y + Ey * self.scale
                end_pos = pygame.Vector2(*to_screen_coordinates(end_x, end_y, self.screen_width, self.screen_height))

                # Draw the arrow using the draw_arrow function
                draw_arrow(
                    surface=self.screen,
                    start=start_pos,
                    end=end_pos,
                    color=pygame.Color(0, 0, 155),
                    body_width=2,
                    head_width=6,
                    head_height=10,
                )

def to_screen_coordinates(x, y, screen_width, screen_height):
    """Convert world coordinates to screen coordinates."""
    sx = screen_width / 2 + x
    sy = screen_height / 2 - y
    return int(sx), int(sy)
