
import pygame
from numpy import arctan2, cos, sin, pi

def draw_arrow(surface, start, end, color, body_width=2, head_width=6, head_height=10):
    """
    Draws an arrow on the given surface.

    Args:
        surface: The pygame surface to draw on.
        start: The starting position of the arrow (x, y).
        end: The ending position of the arrow (x, y).
        color: The color of the arrow.
        body_width: The width of the arrow's body.
        head_width: The width of the arrow's head.
        head_height: The height of the arrow's head.
    """
    # Calculate the direction of the arrow
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = arctan2(dy, dx)

    # Draw the body of the arrow
    pygame.draw.line(surface, color, start, end, body_width)

    # Calculate the positions for the arrowhead
    arrowhead_left = (
        end[0] - head_height * cos(angle + pi / 6),
        end[1] - head_height * sin(angle + pi / 6)
    )
    arrowhead_right = (
        end[0] - head_height * cos(angle - pi / 6),
        end[1] - head_height * sin(angle - pi / 6)
    )

    # Draw the arrowhead
    pygame.draw.polygon(surface, color, [end, arrowhead_left, arrowhead_right])
