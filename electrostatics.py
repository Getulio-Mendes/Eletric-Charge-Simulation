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
import matplotlib.pyplot as plt

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
        dx = x - self.x
        dy = y - self.y
        r_squared = dx**2 + dy**2
        if r_squared == 0:
            return 0, 0  # Avoid division by zero
        r = sqrt(r_squared)
        field_magnitude = self.q / r_squared
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
class Potential:
    """The potential owing to a collection of charges."""

    def __init__(self, charges):
        """Initializes the field given 'charges'."""
        self.charges = charges

    def magnitude(self, x, y):
        """Returns the magnitude of the potential at point (x, y)."""
        return sum(charge.V(x, y) for charge in self.charges)
    
    
    def plot(self, screen, screen_width, screen_height, zmin=-1.5, zmax=1.5, step=0.25, linewidth=1):
        """Plots the field magnitude using pygame."""
        x, y = meshgrid(
            linspace(XMIN / ZOOM + XOFFSET, XMAX / ZOOM + XOFFSET, 200),
            linspace(YMIN / ZOOM, YMAX / ZOOM, 200))
        z = zeros_like(x)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                z[i, j] = self.magnitude([x[i, j], y[i, j]])

        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if zmin <= z[i, j] <= zmax:
                    pos = to_screen_coordinates(x[i, j], y[i, j], screen_width, screen_height)
                    pygame.draw.circle(screen, (0, 0, 0), pos, linewidth)   
   
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
