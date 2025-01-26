import pygame
from multiprocessing import Process

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 255)  # Button color (blue)
BUTTON_TEXT_COLOR = (255, 255, 255)  # Button text color (white)

def run_simulation(charges=None):
    """Função para executar a simulação em um processo separado."""
    from main import main as main_simulation
    main_simulation(charges)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Menu - Simulação de Campos Elétricos")
    clock = pygame.time.Clock()
    running = True

    # Carregar a imagem de fundo
    background_image = pygame.image.load("fundo.png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Redimensionar para o tamanho da tela

    # Fonts
    title_font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 32)

    # Title text
    title_text = title_font.render("Simulação de Campos Elétricos", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))

    # Buttons
    buttons = [
        {"text": "Projeto em Branco", "action": "projeto_em_branco"},
        {"text": "Exemplo: Dipolo", "action": "dipolo"},
        {"text": "Exemplo: Monopolo Falso", "action": "monopolo_falso"},
        {"text": "Exemplo: Linha e Ponto", "action": "linha_ponto"},
        {"text": "Exemplo: Duas Linhas", "action": "duas_linhas"},
        {"text": "Exemplo: Quadrupolo", "action": "quadrupolo"},
        {"text": "Sair", "action": "sair"}
    ]

    # Scroll properties
    scroll_y = 0  # Initial scroll position
    scroll_speed = 20  # Scroll speed in pixels
    total_height = len(buttons) * 60 + 150  # Total height of the content

    # Function to draw buttons
    def draw_buttons():
        for i, button in enumerate(buttons):
            button_rect = pygame.Rect(200, 150 + i * 60 - scroll_y, 400, 50)
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
            button_text = button_font.render(button["text"], True, BUTTON_TEXT_COLOR)
            screen.blit(button_text, (button_rect.x + 20, button_rect.y + 10))
            button["rect"] = button_rect  # Store the button's rectangle

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    # Adjust mouse position for scroll
                    adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)
                    if button["rect"].collidepoint(adjusted_mouse_pos):
                        if button["action"] == "projeto_em_branco":
                            print("Abrindo projeto em branco...")
                            # Inicia a simulação em um processo separado
                            process = Process(target=run_simulation)
                            process.start()

                        elif button["action"] == "dipolo":
                            print("Abrindo exemplo: Dipolo...")
                            # Define as cargas do exemplo do dipolo
                            charges = [
                                {"type": "point", "x": -80, "y": 0, "q": 1e-6},  # Carga positiva
                                {"type": "point", "x": 80, "y": 0, "q": -1e-6}   # Carga negativa
                            ]
                            # Inicia a simulação em um processo separado
                            process = Process(target=run_simulation, args=(charges,))
                            process.start()

                        elif button["action"] == "monopolo_falso":
                            print("Abrindo exemplo: Monopolo Falso...")
                            # Define as cargas do exemplo do monopolo falso
                            charges = [
                                {"type": "point", "x": -160, "y": 0, "q": 1e-6},  # Carga positiva
                                {"type": "point", "x": 160, "y": 0, "q": 1e-6},   # Carga positiva
                                {"type": "point", "x": 0, "y": -160, "q": 1e-6},  # Carga positiva
                                {"type": "point", "x": 0, "y": 160, "q": 1e-6},   # Carga positiva
                                {"type": "point", "x": 0, "y": 0, "q": -4e-6}     # Carga negativa
                            ]
                            # Inicia a simulação em um processo separado
                            process = Process(target=run_simulation, args=(charges,))
                            process.start()

                        elif button["action"] == "linha_ponto":
                            print("Abrindo exemplo: Linha e Ponto...")
                            # Define as cargas do exemplo de linha e ponto
                            charges = [
                                {"type": "line", "q": 1e-6, "start": [-80, -160], "end": [-80, 160]},  # Linha carregada
                                {"type": "point", "x": 80, "y": 0, "q": -1e-6}  # Carga pontual negativa
                            ]
                            # Inicia a simulação em um processo separado
                            process = Process(target=run_simulation, args=(charges,))
                            process.start()

                        elif button["action"] == "duas_linhas":
                            print("Abrindo exemplo: Duas Linhas...")
                            # Define as cargas do exemplo de duas linhas
                            charges = [
                                {"type": "line", "q": 1e-6, "start": [-40, -120], "end": [-40, 120]},  # Linha positiva
                                {"type": "line", "q": -1e-6, "start": [40, -120], "end": [40, 120]}    # Linha negativa
                            ]
                            # Inicia a simulação em um processo separado
                            process = Process(target=run_simulation, args=(charges,))
                            process.start()

                        elif button["action"] == "quadrupolo":
                            print("Abrindo exemplo: Quadrupolo...")
                            # Define as cargas do exemplo de quadrupolo
                            charges = [
                                {"type": "point", "x": -160, "y": 0, "q": 1e-6},  # Carga positiva
                                {"type": "point", "x": 160, "y": 0, "q": 1e-6},   # Carga positiva
                                {"type": "point", "x": 0, "y": -160, "q": -1e-6}, # Carga negativa
                                {"type": "point", "x": 0, "y": 160, "q": -1e-6},  # Carga negativa
                                {"type": "point", "x": 0, "y": 0, "q": 0}         # Ponto de terminação
                            ]
                            # Inicia a simulação em um processo separado
                            process = Process(target=run_simulation, args=(charges,))
                            process.start()

                        elif button["action"] == "sair":
                            running = False

            # Handle scrolling
            if event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * scroll_speed  # Adjust scroll position
                scroll_y = max(0, min(scroll_y, total_height - SCREEN_HEIGHT))  # Clamp scroll position

        # Clear the screen
        screen.fill(WHITE)

        # Desenhar a imagem de fundo
        screen.blit(background_image, (0, 0))

        # Draw title
        screen.blit(title_text, (title_rect.x, title_rect.y - scroll_y))

        # Draw buttons
        draw_buttons()

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
