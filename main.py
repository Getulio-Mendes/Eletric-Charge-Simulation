import pygame
from numpy import array
from electrostatics import PointCharge, LineCharge, ElectricField, Potential, init

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 255)  # Button color (blue)
BUTTON_TEXT_COLOR = (255, 255, 255)  # Button text color (white)
SIDEBAR_COLOR = (200, 200, 200)  # Sidebar color (gray)

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

    dragging_charge = None  # To store the charge that is being dragged
    dragging_line_point = None  # To store which point of the line is being dragged (start or end)
    offset_x, offset_y = 0, 0  # Offsets for dragging

    # Button properties
    button_font = pygame.font.Font(None, 24)
    button_text = button_font.render("+ Carga", True, BUTTON_TEXT_COLOR)
    button_rect = pygame.Rect(10, 10, 80, 30)  # Smaller button in the top-left corner

    # Sidebar properties
    sidebar_width = 200  # Sidebar width
    sidebar_visible = False  # Sidebar state (initially hidden)
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, SCREEN_HEIGHT)  # Sidebar rectangle

    # Menu icon properties
    menu_icon_font = pygame.font.Font(None, 36)
    menu_icon_text = menu_icon_font.render("=", True, BLACK)
    menu_icon_rect = pygame.Rect(10, 10, 30, 30)  # Three-line icon in the top-left corner

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Check if the menu icon is clicked
                if menu_icon_rect.collidepoint(mouse_x, mouse_y):
                    sidebar_visible = not sidebar_visible  # Toggle sidebar visibility

                # Check if the button is clicked (only if the sidebar is visible)
                if sidebar_visible and button_rect.collidepoint(mouse_x, mouse_y):
                    # Add a positive charge at the center of the screen
                    charges.append(PointCharge(0, 0, 1e-6))  # Positive charge at the center
                else:
                    # Convert Pygame coordinates to mathematical coordinates
                    math_x = mouse_x - SCREEN_WIDTH // 2
                    math_y = -(mouse_y - SCREEN_HEIGHT // 2)  # Invert Y axis

                    for charge in charges:
                        if isinstance(charge, PointCharge):
                            charge_x, charge_y = charge.x, charge.y
                            # Check if the mouse is near the charge
                            if (charge_x - 10 <= math_x <= charge_x + 10 and
                                charge_y - 10 <= math_y <= charge_y + 10):
                                # Start dragging the charge
                                dragging_charge = charge
                                offset_x = math_x - charge_x
                                offset_y = math_y - charge_y
                                break  # Exit the loop after finding the clicked charge
                        
                        elif isinstance(charge, LineCharge):
                            start_x, start_y = charge.x1  # Use x1 for the start point
                            end_x, end_y = charge.x2  # Use x2 for the end point
                            # Check if the mouse is near the start or end point of the line
                            if (start_x - 10 <= math_x <= start_x + 10 and
                                start_y - 10 <= math_y <= start_y + 10):
                                dragging_charge = charge
                                dragging_line_point = "start"
                                offset_x = math_x - start_x
                                offset_y = math_y - start_y
                                break
                            elif (end_x - 10 <= math_x <= end_x + 10 and
                                  end_y - 10 <= math_y <= end_y + 10):
                                dragging_charge = charge
                                dragging_line_point = "end"
                                offset_x = math_x - end_x
                                offset_y = math_y - end_y
                                break
            elif event.type == pygame.MOUSEMOTION:
                if dragging_charge:
                    mouse_x, mouse_y = event.pos
                    # Convert Pygame coordinates to mathematical coordinates
                    math_x = mouse_x - SCREEN_WIDTH // 2
                    math_y = -(mouse_y - SCREEN_HEIGHT // 2)  # Invert Y axis

                    if isinstance(dragging_charge, PointCharge):
                        # Move the point charge with the mouse position
                        dragging_charge.x = math_x - offset_x
                        dragging_charge.y = math_y - offset_y
                   
                    elif isinstance(dragging_charge, LineCharge):
                        # Move the start or end point of the line charge
                        if dragging_line_point == "start":
                            dragging_charge.x1 = array([math_x - offset_x, math_y - offset_y])
                        elif dragging_line_point == "end":
                            dragging_charge.x2 = array([math_x - offset_x, math_y - offset_y])
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_charge = None  # Stop dragging the charge
                dragging_line_point = None  # Reset the line point being dragged

        # Clear the screen
        screen.fill(WHITE)

        # Draw the sidebar if visible
        if sidebar_visible:
            pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)  # Sidebar
            screen.blit(button_text, (button_rect.x, button_rect.y))  # Button inside the sidebar

        # Draw the menu icon
        screen.blit(menu_icon_text, (menu_icon_rect.x, menu_icon_rect.y))

        # Draw charges
        for charge in charges:
            charge.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Plot electric field
        field.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
