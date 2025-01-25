import pygame
from electrostatics import PointCharge, LineCharge, ElectricField, Potential, init

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Electric Field and Potential Simulation")
    clock = pygame.time.Clock()
    running = True

    # Initialize the domain based on the screen size
    init(SCREEN_WIDTH, SCREEN_HEIGHT, zoom=1, xoffset=0)

    # Define charges
    charges = [
        PointCharge(-50, 0, 1e-6),  # Positive point charge
        PointCharge(50, 0, -1e-6),  # Negative point charge
        LineCharge(1e-6, [-200, -100], [200, 100]),  # Positive line charge
        LineCharge(-1e-6, [-200, 100], [200, -100])  # Negative line charge
    ]

    # Create electric field and potential objects
    field = ElectricField(charges)
    potential = Potential(charges)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(WHITE)

        # Draw charges
        for charge in charges:
            charge.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Plot electric field
        field.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Plot potential
        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
