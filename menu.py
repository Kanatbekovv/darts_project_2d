import pygame
import sys
from button import Button


pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")

BG = pygame.image.load("1688567112_bogatyr-club-p-chernaya-stena-tekstura-foni-pinterest-22.jpg")
GG = pygame.image.load("assets/2d-art.png")

def get_font(size):
    return pygame.font.Font("assets/KodeMono-VariableFont_wght.ttf", size)

def main_menu():
    from main import main
    # Загрузка и воспроизведение музыки
    pygame.mixer.music.load("sounds/f95d59c3e76296a.mp3")
    pygame.mixer.music.play(-1)  # -1 означает воспроизведение музыки в бесконечном цикле

    running = True
    while running:
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(BG, (0, 0))
        SCREEN.blit(GG, (600, 170))

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(300, 350),
                             text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="Red")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(300, 500),
                             text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="Red")

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    running = False
                elif QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

    # После выхода из цикла, останавливаем музыку
    pygame.mixer.music.stop()

    # После выхода из цикла, начинаем основную часть игры
    main((0, 0), pygame.time.get_ticks())

if __name__ == '__main__':
    main_menu()
