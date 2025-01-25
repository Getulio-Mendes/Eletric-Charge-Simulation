import pygame
from electrostatics import Charge, ElectricField, to_screen_coordinates

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Electric Field Simulation")
    clock = pygame.time.Clock()
    running = True

    # Define charges
    charges = [
        Charge(-100, 0, 1e-6),
        Charge(100, 0, -1e-6)
    ]

    field = ElectricField(screen, charges, SCREEN_WIDTH, SCREEN_HEIGHT)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        # Draw charges
        for charge in charges:
            color = (0, 0, 255) if charge.q > 0 else (255, 0, 0)
            pos = to_screen_coordinates(charge.x, charge.y, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.draw.circle(screen, color, pos, 10)

        # Plot electric field
        field.plot()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
