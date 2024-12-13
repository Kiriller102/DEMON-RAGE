import sys
from collections import deque
from random import randrange
import pygame
from numba.core.cgutils import false_bit

from settings import *


class Drawing:
    def __init__(self, sc, sc_map, player, clock):
        self.sc = sc
        self.sc_map = sc_map
        self.player = player
        self.clock = clock
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_win = pygame.font.Font('font/main_font.ttf', 144)
        self.textures = {1: pygame.image.load('img/wall/wall1.png').convert(),
                         2: pygame.image.load('img/wall/wall2.png').convert(),
                         3: pygame.image.load('img/wall/wall3.png').convert(),
                         4: pygame.image.load('img/wall/wall4.png').convert(),
                         5: pygame.image.load('img/wall/wall5.png').convert(),
                         6: pygame.image.load('img/wall/wall6.png').convert(),
                         7: pygame.image.load('img/wall/wall7.png').convert(),
                         'S': pygame.image.load('img/sky2.png').convert()
                         }

        # menu
        self.menu_trigger = True
        self.menu_picture = pygame.image.load('img/bg.jpg').convert()
        self.retry_trigger = True

        # weapon parameters
        self.weapon_base_sprite = pygame.image.load('sprites/weapons/shotgun/base/0.png').convert_alpha()
        self.weapon_shot_animation = deque([pygame.image.load(f'sprites/weapons/shotgun/shot/{i}.png').convert_alpha()
                                            for i in range(20)])
        self.weapon_rect = self.weapon_base_sprite.get_rect()
        self.weapon_pos = (HALF_WIDTH - self.weapon_rect.width // 2, HEIGHT - self.weapon_rect.height)
        self.shot_projection = 1
        self.shot_length = len(self.weapon_shot_animation)
        self.shot_length_count = 0
        self.shot_animation_speed = 3
        self.shot_animation_count = 0
        self.shot_animation_trigger = True
        self.shot_sound = pygame.mixer.Sound('sound/shotgun.wav')

        # sfx parameters
        self.sfx = deque([pygame.image.load(f'sprites/weapons/sfx/{i}.png').convert_alpha() for i in range(9)])
        self.sfx_length_count = 0
        self.sfx_length = len(self.sfx)

    def background(self, angle):
        sky_offset = -10 * math.degrees(angle) % WIDTH
        self.sc.blit(self.textures['S'], (sky_offset, 0))
        self.sc.blit(self.textures['S'], (sky_offset - WIDTH, 0))
        self.sc.blit(self.textures['S'], (sky_offset + WIDTH, 0))
        pygame.draw.rect(self.sc, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def world(self, world_objects):
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.sc.blit(object, object_pos)

    def fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.font.render(display_fps, 0, DARKORANGE)
        self.sc.blit(render, FPS_POS)

    # def mini_map(self, player):
    #     self.sc_map.fill(BLACK)
    #     map_x, map_y = player.x // MAP_SCALE, player.y // MAP_SCALE
    #     pygame.draw.line(self.sc_map, YELLOW, (map_x, map_y), (map_x + 12 * math.cos(player.angle),
    #                                              map_y + 12 * math.sin(player.angle)), 2)
    #     pygame.draw.circle(self.sc_map, RED, (int(map_x), int(map_y)), 5)
    #     for x, y in mini_map:
    #         pygame.draw.rect(self.sc_map, DARKBROWN, (x, y, MAP_TILE, MAP_TILE))
    #     self.sc.blit(self.sc_map, MAP_POS)

    def player_weapon(self, shots):
        if self.player.shot:
            if not self.shot_length_count:
                self.shot_sound.play()
            self.bullet_sfx()
            self.shot_projection = min(shots)[1]
            shot_sprite = self.weapon_shot_animation[0]
            self.sc.blit(shot_sprite, self.weapon_pos)
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.weapon_shot_animation.rotate(-1)
                self.shot_animation_count = 0
                self.shot_length_count += 1
                self.shot_animation_trigger = False
            if self.shot_length_count == self.shot_length:
                self.player.shot = False
                self.shot_length_count = 0
                self.sfx_length_count = 0
                self.shot_animation_trigger = True
        else:
            self.sc.blit(self.weapon_base_sprite, self.weapon_pos)

    def player_life(self, player):
        life_font = pygame.font.Font('font/label.ttf', 36)
        life = life_font.render(f'{player.life}', True, RED)
        life_rect = life.get_rect()
        life_rect.x = 10
        life_rect.y = HEIGHT - life_rect.height - 10
        self.sc.blit(life, life_rect)

    def bullet_sfx(self):
        if self.sfx_length_count < self.sfx_length:
            sfx = pygame.transform.scale(self.sfx[0], (self.shot_projection, self.shot_projection))
            sfx_rect = sfx.get_rect()
            self.sc.blit(sfx, (HALF_WIDTH - sfx_rect.w // 2, HALF_HEIGHT - sfx_rect.h // 2))
            self.sfx_length_count += 1
            self.sfx.rotate(-1)

    def win(self):
        render = self.font_win.render('YOU WIN!!!', True, (randrange(40, 120), 0, 0))
        text_rect = render.get_rect()
        text_rect.center = (HALF_WIDTH, HALF_HEIGHT)
        bord_rect = pygame.Rect(0, 0, text_rect.width + 50, text_rect.height + 20)
        bord_rect.center = HALF_WIDTH, HALF_HEIGHT
        pygame.draw.rect(self.sc, BLACK, bord_rect, border_radius=50)
        self.sc.blit(render, text_rect)
        pygame.display.flip()
        self.clock.tick(15)

    def lose(self):
        self.player_life(self.player)
        render = self.font_win.render('YOU LOSE!!',
                                      True,
                                      (randrange(40, 120), 0, 0))
        lose_rect = render.get_rect()
        lose_rect.center = (HALF_WIDTH, HALF_HEIGHT - 5 - lose_rect.height // 2)

        retry_label = self.font_win.render('Retry?', True, DARKRED)
        retry_rect = retry_label.get_rect()
        retry_rect.center = (HALF_WIDTH, HALF_HEIGHT + 5 + retry_rect.height // 2)
        retry_button = pygame.Rect(0, 0, retry_rect.width + 30, retry_rect.height + 10)
        retry_button.center = retry_rect.center

        bord_rect = pygame.Rect(0, 0,
                                max(lose_rect.width, retry_rect.width) + 50,
                                retry_rect.height + lose_rect.height + 30)
        bord_rect.center = HALF_WIDTH, HALF_HEIGHT

        pygame.draw.rect(self.sc, BLACK, bord_rect, border_radius=50)
        self.sc.blit(render, lose_rect)
        pygame.draw.rect(self.sc, DARKGRAY, retry_button, border_radius=50)
        self.sc.blit(retry_label, retry_rect)
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        if retry_button.collidepoint(pygame.mouse.get_pos()):
            retry_label = self.font_win.render('Retry?', True, RED)
            pygame.draw.rect(self.sc, LIGHTGRAY, retry_button, border_radius=50)
            self.sc.blit(retry_label, retry_rect)
            if pygame.mouse.get_pressed()[0]:
                return False
        pygame.display.flip()
        self.clock.tick(15)
        return True



    def menu(self):
        x = 0
        button_font = pygame.font.Font('font/main_font.ttf', 72)
        label_font = pygame.font.Font('font/label.ttf', 70)

        start = button_font.render('START', True, pygame.Color('lightgray'))
        button_start = pygame.Rect(0, 0, WIDTH // 3, HEIGHT // 6)
        button_start.center = HALF_WIDTH, HEIGHT // 3 + HEIGHT // 6
        start_rect = start.get_rect()
        start_rect.center = HALF_WIDTH, HEIGHT // 3 + HEIGHT // 6

        exit_label = button_font.render('EXIT', True, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, WIDTH // 3, HEIGHT // 6)
        button_exit.center = HALF_WIDTH, start_rect.centery + button_start.h + 20
        exit_rect = exit_label.get_rect()
        exit_rect.center = HALF_WIDTH, start_rect.centery + button_start.h + 20

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.sc.blit(self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            pygame.draw.rect(self.sc, BLACK, button_start, border_radius=25, width=10)
            self.sc.blit(start, start_rect)

            pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25, width=10)
            self.sc.blit(exit_label, exit_rect)

            color = randrange(20, 70)
            label = label_font.render('DEMON RAGE', True, (color + 30, color, color))
            rect_label = label.get_rect()
            rect_label.center = HALF_WIDTH, HEIGHT // 6
            self.sc.blit(label, rect_label)

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if button_start.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_start, border_radius=25)
                start_red = button_font.render('START', True, pygame.Color('red'))
                self.sc.blit(start_red, start_rect)
                if mouse_click[0]:
                    self.menu_trigger = False
            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25)
                exit_red = button_font.render('EXIT', True, pygame.Color('red'))
                self.sc.blit(exit_red, exit_rect)
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(20)
