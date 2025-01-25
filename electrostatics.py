import functools
import numpy
from numpy import array, arange, linspace, meshgrid, zeros_like, ones_like
from numpy import log10, sin, cos, arctan2, arccos, sqrt, fabs, cumsum
from numpy import radians, pi, inf  # Updated here: infty -> inf
from numpy import dot, cross
from numpy import all as alltrue, isclose  # Updated here: alltrue -> numpy.all
from numpy import where, insert
from numpy import newaxis
from numpy.linalg import det
from scipy.integrate import ode
from scipy.interpolate import splrep, splev
import pygame
import matplotlib.cm as cm

from arrow import draw_arrow

# The area of interest
XMIN, XMAX = None, None
YMIN, YMAX = None, None
ZOOM = None
XOFFSET = None

#-----------------------------------------------------------------------------
# Decorators

def arrayargs(func):
    """Ensures all args are arrays."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Ensures all args are arrays."""
        return func(*[array(a) for a in args], **kwargs)
    return wrapper

#-----------------------------------------------------------------------------
# Functions


def init(screen_width, screen_height, zoom=1, xoffset=0):
    """Initializes the domain based on the screen size."""
    global XMIN, XMAX, YMIN, YMAX, ZOOM, XOFFSET
    # Set the domain to match the screen size
    XMIN, XMAX = -screen_width // 2, screen_width // 2
    YMIN, YMAX = -screen_height // 2, screen_height // 2
    ZOOM = zoom
    XOFFSET = xoffset
    
def norm(x):
    """Returns the magnitude of the vector x."""
    return sqrt(numpy.sum(array(x)**2, axis=-1))

@arrayargs
def point_line_distance(x0, x1, x2):
    """Finds the shortest distance between the point x0 and the line x1 to x2."""
    assert x1.shape == x2.shape == (2,)
    return fabs(cross(x0-x1, x0-x2))/norm(x2-x1)

@arrayargs
def angle(x0, x1, x2):
    """Returns angle between three points."""
    assert x1.shape == x2.shape == (2,)
    a, b = x1 - x0, x1 - x2
    return arccos(dot(a, b)/(norm(a)*norm(b)))

@arrayargs
def is_left(x0, x1, x2):
    """Returns True if x0 is left of the line between x1 and x2, False otherwise."""
    assert x1.shape == x2.shape == (2,)
    matrix = array([x1-x0, x2-x0])
    if len(x0.shape) == 2:
        matrix = matrix.transpose((1, 2, 0))
    return det(matrix) > 0

def lininterp2(x1, y1, x):
    """Linear interpolation at points x between numpy arrays (x1, y1)."""
    return splev(x, splrep(x1, y1, s=0, k=1))

def to_screen_coordinates(x, y, screen_width, screen_height):
    """Convert world coordinates to screen coordinates."""
    sx = screen_width / 2 + x
    sy = screen_height / 2 - y
    return int(sx), int(sy)

#-----------------------------------------------------------------------------
# Classes

class PointCharge:
    """A point charge."""

    R = 0.01  # The effective radius of the charge

    def __init__(self, x, y, q):
        """Initializes the position (x, y) and quantity of charge 'q'."""
        self.x = x
        self.y = y
        self.q = q

    
    def E(self, x, y):  # pylint: disable=invalid-name
        """Electric field vector at point (x, y)."""
        if self.q == 0:
            return 0, 0

        # Convert inputs to numpy arrays if they aren't already
        x = numpy.array(x)
        y = numpy.array(y)

        dx = x - self.x
        dy = y - self.y
        r_squared = dx**2 + dy**2

        # Handle division by zero for points exactly at the charge location
        r_squared = numpy.where(r_squared == 0, numpy.inf, r_squared)

        r = numpy.sqrt(r_squared)
        field_magnitude = self.q / r_squared

        # Calculate field components
        Ex = field_magnitude * (dx / r)
        Ey = field_magnitude * (dy / r)

        return Ex, Ey    
    
    def V(self, x, y):  # pylint: disable=invalid-name
        """Potential at point (x, y)."""
        r = sqrt((x - self.x)**2 + (y - self.y)**2)
        return self.q / r if r != 0 else 0

    def is_close(self, x, y):
        """Returns True if (x, y) is close to the charge; False otherwise."""
        return sqrt((x - self.x)**2 + (y - self.y)**2) < self.R

    def plot(self, screen, screen_width, screen_height):
        """Plots the charge using pygame."""
        color = (0, 0, 255) if self.q < 0 else (255, 0, 0) if self.q > 0 else (0, 0, 0)
        r = 10  # Increase the radius to make the charge more visible
        pos = to_screen_coordinates(self.x, self.y, screen_width, screen_height)
        pygame.draw.circle(screen, color, pos, r)       
        
class LineCharge:
    """A line charge."""

    R = 0.01  # The effective radius of the charge

    def __init__(self, q, x1, x2):
        """Initializes the quantity of charge 'q' and end point vectors 'x1' and 'x2'."""
        self.q, self.x1, self.x2 = q, array(x1), array(x2)

    def get_lam(self):
        """Returns the total charge on the line."""
        return self.q / norm(self.x2 - self.x1)
    lam = property(get_lam)

   
    def E(self, x, y):  # pylint: disable=invalid-name
        """Electric field vector at point (x, y)."""
        x = array([x, y])  # Convert (x, y) to a numpy array
        x1, x2, lam = self.x1, self.x2, self.lam

        theta1, theta2 = angle(x, x1, x2), pi - angle(x, x2, x1)
        a = point_line_distance(x, x1, x2)
        r1, r2 = norm(x - x1), norm(x - x2)

        sign = where(is_left(x, x1, x2), 1, -1)

        Epara = lam * (1 / r2 - 1 / r1)
        Eperp = -sign * lam * (cos(theta2) - cos(theta1)) / where(a == 0, inf, a)

        dx = x2 - x1

        if len(x.shape) == 2:
            Epara = Epara[::, newaxis]
            Eperp = Eperp[::, newaxis]

        # Calculate the electric field components
        Ex = Eperp * (-dx[1] / norm(dx)) + Epara * (dx[0] / norm(dx))
        Ey = Eperp * (dx[0] / norm(dx)) + Epara * (dx[1] / norm(dx))

        return Ex, Ey    
    
    def is_close(self, x):
        """Returns True if x is close to the charge."""
        theta1 = angle(x, self.x1, self.x2)
        theta2 = angle(x, self.x2, self.x1)

        if theta1 < radians(90) and theta2 < radians(90):
            return point_line_distance(x, self.x1, self.x2) < self.R
        return numpy.min([norm(self.x1-x), norm(self.x2-x)], axis=0) < self.R

   
    def V(self, x, y):  # pylint: disable=invalid-name
        """Potential at point (x, y)."""
        x = array([x, y])  # Convert (x, y) to a numpy array
        r1 = norm(x - self.x1)
        r2 = norm(x - self.x2)
        L = norm(self.x2 - self.x1)  # pylint: disable=invalid-name
        return self.lam * numpy.log((r1 + r2 + L) / (r1 + r2 - L))
    
    def plot(self, screen, screen_width, screen_height):
        """Plots the charge using pygame."""
        color = (0, 0, 255) if self.q < 0 else (255, 0, 0) if self.q > 0 else (0, 0, 0)
        width = int(5 * (sqrt(fabs(self.lam)) / 2 + 1))
        start_pos = to_screen_coordinates(self.x1[0], self.x1[1], screen_width, screen_height)
        end_pos = to_screen_coordinates(self.x2[0], self.x2[1], screen_width, screen_height)
        pygame.draw.line(screen, color, start_pos, end_pos, width)

class FieldLine:
    """A Field Line."""

    def __init__(self, x):
        """Initializes the field line points 'x'."""
        self.x = x

    def plot(self, screen, screen_width, screen_height, linewidth=1, startarrows=True, endarrows=True):
        """Plots the field line and arrows using pygame."""
        points = [to_screen_coordinates(point[0], point[1], screen_width, screen_height) for point in self.x]
        if len(points) > 1:
            pygame.draw.lines(screen, (0, 0, 0), False, points, linewidth)

        n = int(len(points) / 2) if len(points) < 225 else 75
        if startarrows and len(points) > n + 1:
            dx = points[n + 1][0] - points[n][0]
            dy = points[n + 1][1] - points[n][1]
            pygame.draw.line(screen, (0, 0, 0), points[n], (points[n][0] + dx / 10, points[n][1] + dy / 10), linewidth)

        if len(points) < 225 or not endarrows:
            return

        dx = points[-n + 1][0] - points[-n][0]
        dy = points[-n + 1][1] - points[-n][1]
        pygame.draw.line(screen, (0, 0, 0), points[-n], (points[-n][0] + dx / 10, points[-n][1] + dy / 10), linewidth)


class ElectricField:
    """The electric field owing to a collection of charges."""

    dt0 = 0.01  # The time step for integrations

    def __init__(self, charges):
        """Initializes the field given 'charges'."""
        self.charges = charges

    def vector(self, x, y):
        """Returns the field vector at point (x, y)."""
        Ex, Ey = 0, 0
        for charge in self.charges:
            charge_ex, charge_ey = charge.E(x, y)
            Ex += charge_ex
            Ey += charge_ey
        return Ex, Ey

    def magnitude(self, x, y):
        """Returns the magnitude of the field vector at point (x, y)."""
        Ex, Ey = self.vector(x, y)
        return sqrt(Ex**2 + Ey**2)
    
    def projection(self, x, a):
        """Returns the projection of the field onto the surface normal."""
        # Ensure x is a 2D array
        x = numpy.array(x)
        if x.ndim == 1:
            x = x[numpy.newaxis, :]

        # Calculate the electric field at each point
        Ex, Ey = self.vector(x[:, 0], x[:, 1])

        # Calculate the projection
        return Ex * numpy.cos(a) + Ey * numpy.sin(a)   

    
    def line(self, x0, max_steps=300, step_size=5):
        """
        Calculates the trajectory of a field line starting from point x0.
    
        Args:
            x0 (array-like): The starting point of the field line.
            max_steps (int): Maximum number of steps to trace the field line.
            step_size (float): Step size for tracing the field line.
    
        Returns:
            list: A list of points representing the field line.
        """
        x0 = numpy.array(x0)  # Ensure x0 is a numpy array
        points = [x0]  # Initialize the list of points with the starting point

        for _ in range(max_steps):
            # Calculate the electric field vector at the current point
            Ex, Ey = self.vector(x0[0], x0[1])

            # Normalize the field vector to get the direction
            field_magnitude = numpy.sqrt(Ex**2 + Ey**2)
            if field_magnitude == 0:
                break  # Stop if the field is zero

            dx = Ex / field_magnitude
            dy = Ey / field_magnitude

            # Calculate the next point
            x0 = x0 + step_size * numpy.array([dx, dy])

            # Stop if the point goes out of bounds
            if not (XMIN <= x0[0] <= XMAX and YMIN <= x0[1] <= YMAX):
                break

            # Add the new point to the list
            points.append(x0)

        return points    
    
    def plot(self, screen, screen_width, screen_height, spacing=40, scale=20):
        """Plots the electric field vectors as arrows, scaled by magnitude."""
       
        for x in range(int(XMIN), int(XMAX), spacing):
            for y in range(int(YMIN), int(YMAX), spacing):
                # Calculate the electric field vector at (x, y)
                Ex, Ey = self.vector(x, y)
                magnitude = sqrt(Ex**2 + Ey**2)

                # Skip invalid or zero-magnitude vectors
                if magnitude == 0 or numpy.isnan(magnitude):
                    continue

                # Normalize the vector for consistent arrow lengths
                Ex /= magnitude
                Ey /= magnitude

                # Calculate start and end positions for the arrow
                start_pos = to_screen_coordinates(x, y, screen_width, screen_height)
                end_x = x + Ex * scale
                end_y = y + Ey * scale
                end_pos = to_screen_coordinates(end_x, end_y, screen_width, screen_height)

                # Draw the arrow using the draw_arrow function
                draw_arrow(
                    surface=screen,
                    start=start_pos,
                    end=end_pos,
                    color=(0, 0, 255),  # Blue color for the arrows
                    )         


def get_color(value, zmin=None, zmax=None, colormap=cm.viridis):
    """
    Maps a value to a color using a Matplotlib colormap.

    Args:
        value (float): The value to map to a color.
        zmin (float): The minimum value of the range (optional).
        zmax (float): The maximum value of the range (optional).
        colormap: A Matplotlib colormap (default is 'viridis').

    Returns:
        tuple: An RGB color tuple.
    """
    if zmin is not None and zmax is not None:
        # Normalize the value to the range [0, 1]
        normalized = (value - zmin) / (zmax - zmin)
        normalized = max(0, min(1, normalized))  # Clamp to [0, 1]
    else:
        # Use the value directly (no normalization)
        normalized = value

    # Get the color from the colormap
    rgba = colormap(normalized)  # Returns an RGBA tuple (values in [0, 1])
    rgb = (int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255))  # Convert to Pygame RGB format
    return rgb

class Potential:
    """The potential owing to a collection of charges."""

    def __init__(self, charges):
        """Initializes the field given 'charges'."""
        self.charges = charges

    def magnitude(self, x, y):
        """Returns the magnitude of the potential at point (x, y)."""
        
        return sum(charge.V(x, y) for charge in self.charges)
    
    
       
    def plot(self, screen, screen_width, screen_height, resolution=200):
        """
        Plots the potential as a heatmap using pygame and a Matplotlib colormap.
        """
        # Create a grid of points
        x, y = numpy.meshgrid(
            numpy.linspace(XMIN / ZOOM + XOFFSET, XMAX / ZOOM + XOFFSET, resolution),
            numpy.linspace(YMIN / ZOOM, YMAX / ZOOM, resolution)
        )
        z = numpy.zeros_like(x)

        # Calculate the potential at each point
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                z[i, j] = self.magnitude(x[i, j], y[i, j])

        # Apply logarithmic scaling to the potential values
        z_scaled = numpy.log10(numpy.abs(z) * 5e8 + 1e-10)  # Add a small offset to avoid log(0)
        z_scaled = numpy.nan_to_num(z_scaled, nan=0.0, posinf=0.0, neginf=0.0)  # Handle invalid values

        # Create a surface for the heatmap
        heatmap_surface = pygame.Surface((resolution, resolution))

        # Draw the heatmap on the surface (flip the y-axis)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                # Get the color for the current potential value (no normalization)
                color = get_color(z_scaled[i, j], zmin=None, zmax=None, colormap=cm.viridis)  # Use the 'viridis' colormap

                # Set the pixel color on the heatmap surface (flip the y-axis)
                heatmap_surface.set_at((j, resolution - 1 - i), color)  # Flip the y-axis

        # Scale the heatmap surface to fit the screen
        heatmap_surface = pygame.transform.scale(heatmap_surface, (screen_width, screen_height))

        # Blit the heatmap surface onto the screen
        screen.blit(heatmap_surface, (0, 0))       
        
class GaussianCircle:
    """A Gaussian circle with radius r."""

    def __init__(self, x, r, a0=0):
        """Initializes the Gaussian surface at position vector 'x' and given radius 'r'."""
        self.x = x
        self.r = r
        self.a0 = a0

    def fluxpoints(self, field, n, uniform=False):
        """Returns points where field lines should enter/exit the surface."""
        a = radians(linspace(0, 360, 1001)) + self.a0
        assert len(a) % 4 == 1
        x = self.r * array([cos(a), sin(a)]).T + self.x

        if uniform:
            flux = ones_like(a)
        else:
            flux = field.projection(x, a)
            if numpy.sum(flux) < 0:
                flux *= -1
            assert numpy.all(flux > 0)  # Updated here: alltrue -> numpy.all

        intflux = insert(cumsum((flux[:-1] + flux[1:]) / 2), 0, 0)
        assert isclose(intflux[-1], numpy.sum(flux[:-1]))

        v = linspace(0, intflux[-1], n + 1)
        a = lininterp2(intflux, a, v)[:-1]

        return self.r * array([cos(a), sin(a)]).T + self.x
