import pygame
from multiprocessing import Process

# Constantes usadas
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
SCROLL_SPEED = 20

# Função para executar a simulação em um processo separado
def run_simulation(charges=None):
    from main import main as main_simulation
    main_simulation(charges)

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Menu - Simulação de Campos Elétricos")
        self.clock = pygame.time.Clock()
        self.running = True

        # Carrega os recursos gráficos
        self.background_image = pygame.image.load("fundo.png")
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.title_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 32)

        # Configura o texto do título
        self.title_text = self.title_font.render("Simulação de Campos Elétricos", True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.buttons = self.create_buttons()

        # Propriedades do scroll
        self.scroll_y = 0
        self.total_height = len(self.buttons) * 60 + 150

    # Função para criar os botões com seus textos e ações
    def create_buttons(self):
        return [
            {"text": "Projeto em Branco", "action": self.projeto_em_branco},
            {"text": "Exemplo: Dipolo", "action": self.exemplo_dipolo},
            {"text": "Exemplo: Monopolo Falso", "action": self.exemplo_monopolo_falso},
            {"text": "Exemplo: Linha e Ponto", "action": self.exemplo_linha_ponto},
            {"text": "Exemplo: Duas Linhas", "action": self.exemplo_duas_linhas},
            {"text": "Exemplo: Quadrupolo", "action": self.exemplo_quadrupolo},
            {"text": "Sair", "action": self.exit_program}
        ]

    # Função para desenhar os botões na tela
    def draw_buttons(self):
        for i, button in enumerate(self.buttons):
            button_rect = pygame.Rect(200, 150 + i * 60 - self.scroll_y, 400, 50)
            pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect)
            button_text = self.button_font.render(button["text"], True, BUTTON_TEXT_COLOR)
            self.screen.blit(button_text, (button_rect.x + 20, button_rect.y + 10))
            button["rect"] = button_rect

    # Função para lidar com as ações do usuario
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Evento para fechar a janela
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN: # Evento de clique do mouse
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_y) # Ajusta a posição do mouse com base no scroll
                    if button["rect"].collidepoint(adjusted_mouse_pos):
                        button["action"]()

            elif event.type == pygame.MOUSEWHEEL: # Evento de scroll do mouse
                self.scroll_y -= event.y * SCROLL_SPEED
                self.scroll_y = max(0, min(self.scroll_y, self.total_height - SCREEN_HEIGHT))

    # Funções de exemplo e ações associadas aos botões
    def projeto_em_branco(self):
        print("Abrindo projeto em branco...")
        Process(target=run_simulation).start()

    def exemplo_dipolo(self):
        print("Abrindo exemplo: Dipolo...")
        charges = [
            {"type": "point", "x": -80, "y": 0, "q": 1e-6},
            {"type": "point", "x": 80, "y": 0, "q": -1e-6}
        ]
        Process(target=run_simulation, args=(charges,)).start()

    def exemplo_monopolo_falso(self):
        print("Abrindo exemplo: Monopolo Falso...")
        charges = [
            {"type": "point", "x": -160, "y": 0, "q": 1e-6},
            {"type": "point", "x": 160, "y": 0, "q": 1e-6},
            {"type": "point", "x": 0, "y": -160, "q": 1e-6},
            {"type": "point", "x": 0, "y": 160, "q": 1e-6},
            {"type": "point", "x": 0, "y": 0, "q": -4e-6}
        ]
        Process(target=run_simulation, args=(charges,)).start()

    def exemplo_linha_ponto(self):
        print("Abrindo exemplo: Linha e Ponto...")
        charges = [
            {"type": "line", "q": 1e-6, "start": [-80, -160], "end": [-80, 160]},
            {"type": "point", "x": 80, "y": 0, "q": -1e-6}
        ]
        Process(target=run_simulation, args=(charges,)).start()

    def exemplo_duas_linhas(self):
        print("Abrindo exemplo: Duas Linhas...")
        charges = [
            {"type": "line", "q": 1e-6, "start": [-40, -120], "end": [-40, 120]},
            {"type": "line", "q": -1e-6, "start": [40, -120], "end": [40, 120]}
        ]
        Process(target=run_simulation, args=(charges,)).start()

    def exemplo_quadrupolo(self):
        print("Abrindo exemplo: Quadrupolo...")
        charges = [
            {"type": "point", "x": -160, "y": 0, "q": 1e-6},
            {"type": "point", "x": 160, "y": 0, "q": 1e-6},
            {"type": "point", "x": 0, "y": -160, "q": -1e-6},
            {"type": "point", "x": 0, "y": 160, "q": -1e-6}
        ]
        Process(target=run_simulation, args=(charges,)).start()

    def exit_program(self):
        print("Saindo...")
        self.running = False

    # Função principal para executar o menu
    def run(self):
        while self.running:
            self.handle_events()
            self.screen.fill(WHITE)
            self.screen.blit(self.background_image, (0, 0))
            self.screen.blit(self.title_text, (self.title_rect.x, self.title_rect.y - self.scroll_y))
            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    menu = Menu()
    menu.run()
