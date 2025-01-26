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
SIDEBAR_COLOR = (100, 100, 100)  # Sidebar color (gray)

def main(initial_charges=None):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Electric Field and Potential Simulation")
    clock = pygame.time.Clock()
    running = True

    # Initialize the domain based on the screen size
    init(SCREEN_WIDTH, SCREEN_HEIGHT, zoom=1, xoffset=0)

    # Define charges (empty list to start, or use initial_charges if provided)
    charges = []
    if initial_charges:
        for charge_data in initial_charges:
            if charge_data["type"] == "point":
                charges.append(PointCharge(charge_data["x"], charge_data["y"], charge_data["q"]))
            elif charge_data["type"] == "line":
                charges.append(LineCharge(charge_data["q"], charge_data["start"], charge_data["end"]))

    # Create electric field and potential objects
    field = ElectricField(charges)
    potential = Potential(charges)
    
    dragging_charge = None  # To store the charge that is being dragged
    dragging_line_point = None  # To store which point of the line is being dragged (start or end)
    offset_x, offset_y = 0, 0  # Offsets for dragging

    # Sidebar properties
    sidebar_width = 250  # Sidebar width
    sidebar_visible = True  # Sidebar visibility
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, SCREEN_HEIGHT)

    # Button properties
    button_font = pygame.font.Font(None, 24)
    button_text_positive = button_font.render("Carga pontual +", True, BUTTON_TEXT_COLOR)
    button_text_negative = button_font.render("Carga pontual -", True, BUTTON_TEXT_COLOR)
    button_text_line_positive = button_font.render("Carga linha +", True, BUTTON_TEXT_COLOR)
    button_text_line_negative = button_font.render("Carga linha -", True, BUTTON_TEXT_COLOR)
    button_text_remove = button_font.render("Remover Cargas", True, BUTTON_TEXT_COLOR)

    button_rect_positive = pygame.Rect(10, 50, sidebar_width - 20, 30)  # Positive point charge button
    button_rect_negative = pygame.Rect(10, 100, sidebar_width - 20, 30)  # Negative point charge button
    button_rect_line_positive = pygame.Rect(10, 150, sidebar_width - 20, 30)  # Positive line charge button
    button_rect_line_negative = pygame.Rect(10, 200, sidebar_width - 20, 30)  # Negative line charge button
    button_rect_remove = pygame.Rect(10, 250, sidebar_width - 20, 30)  # Remove charges button

    # Menu icon properties
    menu_icon_font = pygame.font.Font(None, 36)
    menu_icon_text = menu_icon_font.render("=", True, BLACK)
    menu_icon_rect = pygame.Rect(10, 10, 40, 40)  # Menu icon in the top-left corner

    remove_mode = False  # Estado do modo de remoção

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Check if the menu icon is clicked
                if menu_icon_rect.collidepoint(mouse_x, mouse_y):
                    sidebar_visible = not sidebar_visible  # Toggle sidebar visibility
                    remove_mode = False  # Desativa o modo de remoção ao alternar a barra lateral

                # Check if the buttons are clicked (only if the sidebar is visible)
                if sidebar_visible:
                    if button_rect_positive.collidepoint(mouse_x, mouse_y):
                        # Add a positive point charge at the center of the screen
                        charges.append(PointCharge(0, 0, 1e-6))  # Positive charge at the center
                        remove_mode = False  # Desativa o modo de remoção
                    elif button_rect_negative.collidepoint(mouse_x, mouse_y):
                        # Add a negative point charge at the center of the screen
                        charges.append(PointCharge(0, 0, -1e-6))  # Negative charge at the center
                        remove_mode = False  # Desativa o modo de remoção
                    elif button_rect_line_positive.collidepoint(mouse_x, mouse_y):
                        # Add a positive line charge
                        charges.append(LineCharge(1e-6, array([-100, -50]), array([100, 50])))  # Positive line charge
                        remove_mode = False  # Desativa o modo de remoção
                    elif button_rect_line_negative.collidepoint(mouse_x, mouse_y):
                        # Add a negative line charge
                        charges.append(LineCharge(-1e-6, array([-100, 50]), array([100, -50])))  # Negative line charge
                        remove_mode = False  # Desativa o modo de remoção
                    elif button_rect_remove.collidepoint(mouse_x, mouse_y):
                        # Toggle remove mode
                        remove_mode = not remove_mode  # Alternar o modo de remoção

                # Convert Pygame coordinates to mathematical coordinates
                math_x = mouse_x - SCREEN_WIDTH // 2
                math_y = -(mouse_y - SCREEN_HEIGHT // 2)  # Invert Y axis

                if remove_mode:
                    # If in remove mode, check if a charge is clicked to remove it
                    for charge in charges[:]:  # Iterate over a copy of the list to avoid modification issues
                        if isinstance(charge, PointCharge):
                            charge_x, charge_y = charge.x, charge.y
                            # Check if the mouse is near the charge
                            if (charge_x - 10 <= math_x <= charge_x + 10 and
                                charge_y - 10 <= math_y <= charge_y + 10):
                                # Remove the charge
                                charges.remove(charge)
                                break  # Exit the loop after removing the charge
                        elif isinstance(charge, LineCharge):
                            start_x, start_y = charge.x1  # Use x1 for the start point
                            end_x, end_y = charge.x2  # Use x2 for the end point
                            # Check if the mouse is near the start or end point of the line
                            if (start_x - 10 <= math_x <= start_x + 10 and
                                start_y - 10 <= math_y <= start_y + 10):
                                charges.remove(charge)
                                break
                            elif (end_x - 10 <= math_x <= end_x + 10 and
                                  end_y - 10 <= math_y <= end_y + 10):
                                charges.remove(charge)
                                break
                else:
                    # If not in remove mode, check if a charge is clicked to drag it
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

        # Plot electric field
        #field.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        potential.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)        
        
                
        # Draw charges
        for charge in charges:
            charge.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)


        # Draw the sidebar if visible
        if sidebar_visible:
            pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)  # Sidebar
            screen.blit(button_text_positive, (button_rect_positive.x, button_rect_positive.y))  # Positive point charge button
            screen.blit(button_text_negative, (button_rect_negative.x, button_rect_negative.y))  # Negative point charge button
            screen.blit(button_text_line_positive, (button_rect_line_positive.x, button_rect_line_positive.y))  # Positive line charge button
            screen.blit(button_text_line_negative, (button_rect_line_negative.x, button_rect_line_negative.y))  # Negative line charge button
            screen.blit(button_text_remove, (button_rect_remove.x, button_rect_remove.y))  # Remove charges button

            # Highlight the remove button if in remove mode
            if remove_mode:
                pygame.draw.rect(screen, (255, 0, 0), button_rect_remove, 2)  # Borda vermelha no botão de remover

        # Draw the menu icon (always visible)
        screen.blit(menu_icon_text, (menu_icon_rect.x, menu_icon_rect.y))

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
