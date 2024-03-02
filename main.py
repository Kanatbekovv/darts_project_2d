import pygame
from pygame.locals import *
import math
import time
from menu import main_menu

pygame.init()
scr = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Darts')
pygame.mouse.set_visible(1)


font = pygame.font.SysFont(None, 36)


bg = pygame.image.load('1688567112_bogatyr-club-p-chernaya-stena-tekstura-foni-pinterest-22.jpg').convert()
scr.blit(bg, (0, 0))
pygame.display.flip()


clock = pygame.time.Clock()

OB = 0
SINGLE = 1
DOUBLE = 2
TRIPLE = 3
BULL = 4
DBULL = 5

class Room:
    wall_distance = 237


class Bullet:
    g = 10
    r = 10
    fgcolor = pygame.color.Color('yellow')
    bgcolor = pygame.color.Color('white')
    speedrate = 0.01
    vrate = 0.01
    angle_base_len = 150.0
    angle_range = 20.0
    angle_positive_max = 30.0

    def __init__(self, start_pos, end_pos, start_t, end_t):
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        takentime = end_t - start_t
        self.discharge_t = end_t
        self.ini_pos = start_pos

        length = math.sqrt((start_x-end_x)**2+(start_y-end_y)**2)
        if length > self.angle_base_len:
            yz_angle = self.angle_range - self.angle_positive_max
        else:
            yz_angle = self.angle_range / self.angle_base_len * length - \
              (self.angle_range - self.angle_positive_max)
        yz_angle *= math.pi / 180
        xy_angle = math.atan2(end_y - start_y, end_x - start_x)

        if length <= 0:
            self.velocity = 0
        else:
            self.velocity = length / takentime * self.speedrate
        self.x_move = math.cos(xy_angle) * self.velocity
        self.y_move = math.sin(-1*math.pi/180) * self.velocity
        self.z = 0
        self.z_move = abs(math.cos(yz_angle) * self.velocity)
        self.sizerate = 1
        self.sizerate_change = self.velocity * self.vrate

        # calculate center position of bullet.
        self.center = start_x, start_y
        self.pos = start_x - self.r, start_y - self.r

        # create and draw surface.
        self.surface = pygame.Surface((self.r * 2, self.r * 2)).convert()
        self.surface.fill(self.bgcolor)
        self.surface.set_colorkey(self.bgcolor)
        self.rect = pygame.draw.circle(self.surface, self.fgcolor, (self.r, self.r), self.r)



    def __move_x(self):
        return self.x_move

    def __move_y(self):
        return (self.g*(time.time() - self.discharge_t)**2) / 2 + self.y_move

    def __move_z(self):
        return self.z_move

    def __move_size(self):
        return self.sizerate / (1 + self.sizerate_change)

    def move(self):
        self.sizerate = self.__move_size()
        self.pos = (self.pos[0] + self.__move_x(), self.pos[1] + self.__move_y())
        self.center = (self.center[0] + self.__move_x(), self.center[1] + self.__move_y())
        self.z += self.__move_z()
        self.surface.fill(self.bgcolor)
        r = int(round(self.r * self.sizerate))
        if r < 0:
            return None
        return pygame.draw.circle(self.surface, self.fgcolor, (self.r, self.r), r)

    def get_rect(self):
        return self.surface.get_rect()


class BoardShadow(pygame.sprite.Sprite):
    image_fn = './dartsboard-shadow.png'
    def __init__(self, pos=(0, 0)):
        self.image = pygame.image.load(self.image_fn).convert_alpha()
        self.rect = self.image.get_rect()
        self.height, self.width = self.image.get_size()
        self.center_x = self.width / 2.0
        self.center_y = self.height / 2.0
        self.move(pos)

    def move(self, pos):
        x, y = pos
        self.center_x = self.width / 2.0 + x
        self.center_y = self.height / 2.0 + y
        self.rect = self.rect.move(pos)


class Board(pygame.sprite.Sprite):
    image_fn = 'dartsboard.png'
    inbull = 12.7/4.0
    outbull = 31.8/4.0
    triple_inside = 99/2.0
    triple_outside = 107/2.0
    double_inside = 162/2.0
    double_outside = 170/2.0
    points = 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5, 20, 1, 18, 4, 13, 6
    def __init__(self, pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(self.image_fn).convert_alpha()
        self.rect = self.image.get_rect()
        self.height, self.width = self.image.get_size()
        self.center_x = self.width / 2.0
        self.center_y = self.height / 2.0
        self.move(pos)

    def move(self, pos):
        x, y = pos
        self.center_x = self.width / 2.0 + x
        self.center_y = self.height / 2.0 + y
        self.rect = self.rect.move(pos)

    def getpoint(self, pos):
        angle_p = 2 * math.pi / 20
        x, y = pos
        x_distance = self.center_x - x
        y_distance = self.center_y - y
        angle = math.atan2(y_distance, x_distance)
        distance = math.sqrt(x_distance**2 + y_distance**2)
        # OutBoard
        if distance > self.double_outside:
            return 0, OB
        # Inner BULL
        if distance < self.inbull:
            return 50, DBULL
        # Outer BULL
        if distance < self.outbull:
            return 25, BULL
        point = self.points[int(angle / angle_p + 10.5)]
        # Triple ring
        if self.triple_inside <= distance <= self.triple_outside:
            return point, TRIPLE
        # Double ring
        if self.double_inside <= distance <= self.double_outside:
            return point, DOUBLE
        return point, SINGLE


class ScorePanel:
    color = (0, 0, 0, 150)
    fontname = 'GDhighwayJapan-026b1.otf'
    def __init__(self, pos, size):
        self.surface = pygame.Surface(size).convert_alpha()
        self.surface.fill(self.color)
        self.pos = pos=(0,0)
        self.size = size = (200, 200)
    def update(self):
        pass


class ThrowScorePanel(ScorePanel):
    def __init__(self, pos, size):
        ScorePanel.__init__(self, pos, size)
        self.playerfont = pygame.font.Font(self.fontname, 15)
        self.playerfont.set_bold(True)
        self.rfont = pygame.font.Font(self.fontname, 15)
        self.pfont = pygame.font.Font(self.fontname, 15)
        self.set_player('')
        self.set_round(1)
        self.points = []

    def set_player(self, player):
        self.player = player

    def set_round(self, r):
        self.round = r

    def add_point(self, throw, ring, point):
        if len(self.points) >= 3:
            self.points = []
        self.points.append((throw, ring, point))

    def ringpttostr(self, ring, point):
        if point <= 0:
            return ' 0 OutBoard'
        if ring == SINGLE:
            return '%2d Single%d' % (point, point)
        if ring == DOUBLE:
            return '%2d Double%d' % (point*2, point)
        if ring == TRIPLE:
            return '%2d Triple%d' % (point*3, point)
        if ring == BULL:
            return '25 BULL'
        if ring == DBULL:
            return '50 D-BULL'

    def update(self):
        self.surface.fill(self.color)
        x, y = self.surface.get_size()
        pygame.draw.rect(self.surface, (204, 0, 51), ((5, 5), (x-10, 30)))
        self.surface.blit(self.playerfont.render(self.player, True, pygame.color.Color('White')), (10, 10))
        self.surface.blit(self.rfont.render('Adlet %s' % str(self.round), True, pygame.color.Color('White')), (10, 40))

        ypos = 60
        for throw, ring, point in self.points:
            self.surface.blit(self.pfont.render(self.ringpttostr(ring, point), True, pygame.color.Color('White')), (10, ypos))
            ypos += 20


class SoundEffect:
    hit_se = pygame.mixer.Sound('hit.wav')
    hit_se_single = pygame.mixer.Sound('single.wav')
    hit_se_double = pygame.mixer.Sound('double.wav')
    hit_se_triple = pygame.mixer.Sound('triple.wav')
    hit_se_bull = pygame.mixer.Sound('bull.wav')
    hit_se_dbull = pygame.mixer.Sound('dbull.wav')
    def effect(self, ring):
        SoundEffect.hit_se.play()
        if ring == SINGLE:
            SoundEffect.hit_se_single.play()
        if ring == DOUBLE:
            SoundEffect.hit_se_double.play()
        if ring == TRIPLE:
            SoundEffect.hit_se_triple.play()
        if ring == BULL:
            SoundEffect.hit_se_bull.play()
        if ring == DBULL:
            SoundEffect.hit_se_dbull.play()

def outofrect(pos, rect):
    x, y = pos
    if rect.left > x:
        return True
    if rect.right < x:
        return True
    if rect.top > y:
        return True
    if rect.bottom < y:
        return True
    return False

def draw_level_progress(screen, current_level):
    # Определяем размеры и цвета для окна с информацией о прохождении уровня
    width = 200
    height = 100
    bg_color = (255, 255, 255)
    border_color = (0, 0, 0)
    font_color = (0, 0, 0)
    font_size = 20

    # Создаем поверхность для окна и рисуем его
    progress_surf = pygame.Surface((width, height))
    progress_surf.fill(bg_color)
    pygame.draw.rect(progress_surf, border_color, (0, 0, width, height), 100)

    # Создаем текст о текущем уровне
    font = pygame.font.Font(None, font_size)
    text = font.render(f"Level: {current_level}", True, font_color)
    text_rect = text.get_rect(center=(width//2, height//2))

    # Выводим текст на поверхность окна
    progress_surf.blit(text, text_rect)

    # Отображаем окно на главном экране
    screen.blit(progress_surf, (10, 10))

    # Обновляем экран
    pygame.display.flip()

def display_victory_screen(screen):
    screen.fill((0, 0, 0))  # Заливка экрана черным цветом
    font = pygame.font.Font(None, 36)
    text = font.render("Поздравляем! Вы победили!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(text, text_rect)

    play_again_text = font.render("Нажмите любую клавишу, чтобы начать заново", True, (255, 255, 255))
    play_again_rect = play_again_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(play_again_text, play_again_rect)

    pygame.display.flip()

    # Ждем нажатия любой клавиши
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                main()

def update_score_panel(score_panel, current_level, score):
    score_panel.set_round(current_level)
    score_panel.update()


def display_level_completion_screen(screen, current_level):
    screen.fill((0, 0, 0))  # Заливка экрана черным цветом
    font = pygame.font.Font(None, 36)
    text = font.render(f"Поздравляем! Вы прошли уровень {current_level}!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(text, text_rect)

    next_level_text = font.render("Нажмите любую клавишу, чтобы перейти к следующему уровню", True, (255, 255, 255))
    next_level_rect = next_level_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(next_level_text, next_level_rect)

    pygame.display.flip()

    # Ждем нажатия любой клавиши
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False

def main(start_pos=None, start_t=None):
    width = 1280
    height = 720
    screct = scr.get_rect()
    room = Room()
    tpanel = ThrowScorePanel((10, 350), (250, 150))
    tpanel.update()
    scr.blit(tpanel.surface, (10, 10))
    scr_x, scr_y = scr.get_size()
    boardshadow = BoardShadow()
    board = Board()
    board_x, board_y = board.image.get_size()
    board.move((scr_x/2 - board_x/2, scr_y/2 - board_y/2 - 20))
    bullets = []
    se = SoundEffect()
    allsprites = pygame.sprite.RenderPlain(board)

    # Уровни патронов
    bullet_levels = {1: 3, 2: 2, 3: 1}
    current_level = 1
    bullets_left = bullet_levels[current_level]
    score = 0


    bullets = []

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == MOUSEBUTTONDOWN:
                if bullets_left > 0:
                    start_pos = pygame.mouse.get_pos()
                    start_t = time.time()

            if event.type == MOUSEBUTTONUP:
                if bullets_left > 0:
                    end_pos = pygame.mouse.get_pos()
                    end_t = time.time()
                    bullets.append(Bullet(start_pos, end_pos, start_t, end_t))
                    bullets_left -= 1

            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    main()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    main_menu()

        scr.blit(bg, (0, 0))
        scr.blit(tpanel.surface, tpanel.pos)
        allsprites.draw(scr)
        for i, bullet in enumerate(bullets):
            bullet.move()
            if outofrect(bullet.center, screct):
                pt, ring = (0, OB)
                tpanel.add_point(1, ring, pt)
                tpanel.update()
                del bullets[i]
                continue
            if bullet.z >= room.wall_distance:
                pt, ring = board.getpoint(bullet.center)
                tpanel.add_point(1, ring, pt)
                tpanel.update()
                se.effect(ring)
                score += pt
                del bullets[i]
                bullets_left = bullet_levels[current_level]
                if score >= 30:
                    display_level_completion_screen(scr, current_level)
                    current_level += 1
                    if current_level > 3:
                        display_victory_screen(scr)  # Отображение экрана победы
                        return
                    else:
                        draw_level_progress(scr, current_level)  # Отображаем окно о прохождении уровня
                        print("Уровень", current_level)
                    score = 0
                continue
            scr.blit(bullet.surface, bullet.pos)

        # Отображение информации о прохождении уровня
        text = font.render(f"Level: {current_level}", True, (255, 255, 255))
        scr.blit(text, (10, 10))

        pygame.display.flip()
        time.sleep(0.01)

def restart_game(bullets_list, score_panel):
    print("Игра перезапущена")  # Добавляем вывод в консоль для отладки
    bullets_list.clear()
    current_level = 1
    score = 0
    update_score_panel(score_panel, current_level, score)  # Обновляем панель счета
    print("Уровень", current_level)
    pygame.display.flip()  # Update the display


if __name__ == '__main__':
    pygame.init()
    scr = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('darts')
    pygame.mouse.set_visible(1)
    bg = pygame.image.load('1688567112_bogatyr-club-p-chernaya-stena-tekstura-foni-pinterest-22.jpg').convert()
    scr.blit(bg, (0, 0))
    pygame.display.flip()
    draw_level_progress(scr, 1)  # Начальный уровень
    main()

