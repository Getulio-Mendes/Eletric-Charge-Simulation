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

# Initialization Functions
def initialize_screen():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Electric Field and Potential Simulation")
    return screen

def initialize_sidebar():
    sidebar_width = 250  # Sidebar width
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, SCREEN_HEIGHT)
    return sidebar_rect

def initialize_buttons():
    button_font = pygame.font.Font(None, 24)
    buttons = {
        "positive": {
            "text": button_font.render("Carga pontual +", True, BUTTON_TEXT_COLOR),
            "rect": pygame.Rect(10, 50, 230, 30)
        },
        "negative": {
            "text": button_font.render("Carga pontual -", True, BUTTON_TEXT_COLOR),
            "rect": pygame.Rect(10, 100, 230, 30)
        },
        "line_positive": {
            "text": button_font.render("Carga linha +", True, BUTTON_TEXT_COLOR),
            "rect": pygame.Rect(10, 150, 230, 30)
        },
        "line_negative": {
            "text": button_font.render("Carga linha -", True, BUTTON_TEXT_COLOR),
            "rect": pygame.Rect(10, 200, 230, 30)
        },
        "remove": {
            "text": button_font.render("Remover Cargas", True, BUTTON_TEXT_COLOR),
            "rect": pygame.Rect(10, 250, 230, 30)
        },
        "plot": {
            "text": button_font.render("Mostrar Potencial", True, BUTTON_TEXT_COLOR),
            "rect": pygame.Rect(10, 300, 230, 30)
        }
    }
    return buttons

def initialize_menu_icon():
    menu_icon_font = pygame.font.Font(None, 36)
    menu_icon_text = menu_icon_font.render("=", True, BLACK)
    menu_icon_rect = pygame.Rect(10, 10, 40, 40)
    return menu_icon_text, menu_icon_rect


def handle_mouse_down(event, charges, buttons, menu_icon_rect, sidebar_visible, remove_mode, plot_mode, offset_x, offset_y):
    mouse_x, mouse_y = event.pos
    dragging_charge = None
    dragging_line_point = None

    if menu_icon_rect.collidepoint(mouse_x, mouse_y):
        sidebar_visible = not sidebar_visible
        remove_mode = False

    if sidebar_visible:
        if buttons["positive"]["rect"].collidepoint(mouse_x, mouse_y):
            charges.append(PointCharge(0, 0, 1e-6))
            remove_mode = False
        elif buttons["negative"]["rect"].collidepoint(mouse_x, mouse_y):
            charges.append(PointCharge(0, 0, -1e-6))
            remove_mode = False
        elif buttons["line_positive"]["rect"].collidepoint(mouse_x, mouse_y):
            charges.append(LineCharge(1e-6, array([-100, -50]), array([100, 50])))
            remove_mode = False
        elif buttons["line_negative"]["rect"].collidepoint(mouse_x, mouse_y):
            charges.append(LineCharge(-1e-6, array([-100, 50]), array([100, -50])))
            remove_mode = False
        elif buttons["remove"]["rect"].collidepoint(mouse_x, mouse_y):
            remove_mode = not remove_mode
        elif buttons["plot"]["rect"].collidepoint(mouse_x, mouse_y):
            plot_mode = not plot_mode

    for charge in charges:
        if isinstance(charge, PointCharge):
            charge_screen_x = charge.x + SCREEN_WIDTH // 2
            charge_screen_y = -charge.y + SCREEN_HEIGHT // 2
            if (mouse_x - charge_screen_x)**2 + (mouse_y - charge_screen_y)**2 < 25**2:  # Check if click is near charge
                dragging_charge = charge
                offset_x = mouse_x - charge_screen_x
                offset_y = mouse_y - charge_screen_y
                break
        elif isinstance(charge, LineCharge):
            start_screen_x, start_screen_y = charge.x1[0] + SCREEN_WIDTH // 2, -charge.x1[1] + SCREEN_HEIGHT // 2
            end_screen_x, end_screen_y = charge.x2[0] + SCREEN_WIDTH // 2, -charge.x2[1] + SCREEN_HEIGHT // 2

            if (mouse_x - start_screen_x)**2 + (mouse_y - start_screen_y)**2 < 25**2:
                dragging_charge = charge
                dragging_line_point = "start"
                offset_x = mouse_x - start_screen_x
                offset_y = mouse_y - start_screen_y
                break
            elif (mouse_x - end_screen_x)**2 + (mouse_y - end_screen_y)**2 < 25**2:
                dragging_charge = charge
                dragging_line_point = "end"
                offset_x = mouse_x - end_screen_x
                offset_y = mouse_y - end_screen_y
                break

    return sidebar_visible, remove_mode, plot_mode, dragging_charge, dragging_line_point, offset_x, offset_y

def handle_mouse_motion(event, dragging_charge, dragging_line_point, offset_x, offset_y):
    if dragging_charge:
        mouse_x, mouse_y = event.pos
        math_x = mouse_x - SCREEN_WIDTH // 2
        math_y = -(mouse_y - SCREEN_HEIGHT // 2)

        if isinstance(dragging_charge, PointCharge):
            dragging_charge.x = math_x - offset_x
            dragging_charge.y = math_y - offset_y
        elif isinstance(dragging_charge, LineCharge):
            if dragging_line_point == "start":
                dragging_charge.x1 = array([math_x - offset_x, math_y - offset_y])
            elif dragging_line_point == "end":
                dragging_charge.x2 = array([math_x - offset_x, math_y - offset_y])
                
def render_sidebar(screen, sidebar_rect, buttons, remove_mode):
    pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)
    for button in buttons.values():
        screen.blit(button["text"], (button["rect"].x, button["rect"].y))
    if remove_mode:
        pygame.draw.rect(screen, (255, 0, 0), buttons["remove"]["rect"], 2)

# Main Function
def main(initial_charges=None):
    screen = initialize_screen()
    clock = pygame.time.Clock()
    init(SCREEN_WIDTH, SCREEN_HEIGHT, zoom=1, xoffset=0)

    charges = []
    if initial_charges:
        for charge_data in initial_charges:
            if charge_data["type"] == "point":
                charges.append(PointCharge(charge_data["x"], charge_data["y"], charge_data["q"]))
            elif charge_data["type"] == "line":
                charges.append(LineCharge(charge_data["q"], charge_data["start"], charge_data["end"]))

    field = ElectricField(charges)
    potential = Potential(charges)
    sidebar_rect = initialize_sidebar()
    buttons = initialize_buttons()
    menu_icon_text, menu_icon_rect = initialize_menu_icon()

    dragging_charge = None
    dragging_line_point = None
    offset_x, offset_y = 0, 0
    sidebar_visible = True
    remove_mode = False
    plot_mode = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                sidebar_visible, remove_mode, plot_mode, dragging_charge, dragging_line_point, offset_x, offset_y = handle_mouse_down(
                    event, charges, buttons, menu_icon_rect, sidebar_visible, remove_mode, plot_mode, offset_x, offset_y
                )

            if event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event, dragging_charge, dragging_line_point, offset_x, offset_y)

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_charge = None
                dragging_line_point = None

        screen.fill(WHITE)

        if plot_mode:
            potential.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            field.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        for charge in charges:
            charge.plot(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        if sidebar_visible:
            render_sidebar(screen, sidebar_rect, buttons, remove_mode)

        screen.blit(menu_icon_text, (menu_icon_rect.x, menu_icon_rect.y))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
