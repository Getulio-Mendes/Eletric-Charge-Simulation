import pygame
from electrostatics import PointCharge, LineCharge, ElectricField, Potential, init

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 255)  # Cor do botão (azul)
BUTTON_TEXT_COLOR = (255, 255, 255)  # Cor do texto do botão (branco)
SIDEBAR_COLOR = (200, 200, 200)  # Cor da barra lateral (cinza)

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
    offset_x, offset_y = 0, 0  # Offsets for dragging

    # Button properties
    button_font = pygame.font.Font(None, 24)
    button_text_positive = button_font.render("+ Carga", True, BUTTON_TEXT_COLOR)
    button_text_negative = button_font.render("- Carga", True, BUTTON_TEXT_COLOR)
    button_text_remove = button_font.render("Remover", True, BUTTON_TEXT_COLOR)
    button_rect_positive = pygame.Rect(20, 50, 80, 30)  # Botão para carga positiva
    button_rect_negative = pygame.Rect(20, 100, 80, 30)  # Botão para carga negativa
    button_rect_remove = pygame.Rect(20, 150, 80, 30)  # Botão para remover carga

    # Sidebar properties
    sidebar_width = 150  # Largura da barra lateral reduzida
    sidebar_visible = False  # Estado da barra lateral (inicialmente escondida)
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, SCREEN_HEIGHT)  # Retângulo da barra lateral

    # Menu icon properties
    menu_icon_font = pygame.font.Font(None, 36)
    menu_icon_text = menu_icon_font.render("=", True, BLACK)
    menu_icon_rect = pygame.Rect(10, 10, 30, 30)  # Ícone de três linhas no canto superior esquerdo

    # Remove mode
    remove_mode = False  # Estado do modo de remoção

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Check if the menu icon is clicked
                if menu_icon_rect.collidepoint(mouse_x, mouse_y):
                    sidebar_visible = not sidebar_visible  # Alternar visibilidade da barra lateral

                # Check if the buttons are clicked (only if the sidebar is visible)
                if sidebar_visible:
                    if button_rect_positive.collidepoint(mouse_x, mouse_y):
                        # Add a positive charge at the center of the screen
                        charges.append(PointCharge(0, 0, 1e-6))  # Carga positiva no centro
                        remove_mode = False  # Desativa o modo de remoção
                    elif button_rect_negative.collidepoint(mouse_x, mouse_y):
                        # Add a negative charge at the center of the screen
                        charges.append(PointCharge(0, 0, -1e-6))  # Carga negativa no centro
                        remove_mode = False  # Desativa o modo de remoção
                    elif button_rect_remove.collidepoint(mouse_x, mouse_y):
                        # Toggle remove mode
                        remove_mode = not remove_mode  # Alternar o modo de remoção

                # Check if a charge is clicked (independent of sidebar visibility)
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

            elif event.type == pygame.MOUSEMOTION:
                if dragging_charge:
                    mouse_x, mouse_y = event.pos
                    # Convert Pygame coordinates to mathematical coordinates
                    math_x = mouse_x - SCREEN_WIDTH // 2
                    math_y = -(mouse_y - SCREEN_HEIGHT // 2)  # Invert Y axis

                    # Move the charge with the mouse position
                    dragging_charge.x = math_x - offset_x
                    dragging_charge.y = math_y - offset_y

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_charge = None  # Stop dragging the charge

        # Clear the screen
        screen.fill(WHITE)

        # Draw charges
        for charge in charges:
            charge.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Plot electric field
        field.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Draw the sidebar if visible (drawn last to cover everything behind it)
        if sidebar_visible:
            pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)  # Barra lateral
            screen.blit(button_text_positive, (button_rect_positive.x, button_rect_positive.y))  # Botão para carga positiva
            screen.blit(button_text_negative, (button_rect_negative.x, button_rect_negative.y))  # Botão para carga negativa
            screen.blit(button_text_remove, (button_rect_remove.x, button_rect_remove.y))  # Botão para remover carga

            # Highlight the remove button if in remove mode
            if remove_mode:
                pygame.draw.rect(screen, (255, 0, 0), button_rect_remove, 3)  # Borda vermelha no botão de remover

        # Draw the menu icon (drawn last to ensure it's always visible)
        screen.blit(menu_icon_text, (menu_icon_rect.x, menu_icon_rect.y))

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
