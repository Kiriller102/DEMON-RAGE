import time

import pygame
from numba import njit
from settings import *
from map import world_map
from ray_casting import mapping


@njit(fastmath=True, cache=True)
def ray_casting_npc_player(npc_x, npc_y, blocked_doors, world_map, player_pos):
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    delta_x, delta_y = ox - npc_x, oy - npc_y
    cur_angle = math.atan2(delta_y, delta_x) + math.pi

    sin_a, cos_a = math.sin(cur_angle), math.cos(cur_angle)
    sin_a = sin_a if sin_a else 1e-6
    cos_a = cos_a if cos_a else 1e-6

    # Vertical raycasting
    x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
    for _ in range(0, int(abs(delta_x)) // TILE):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = mapping(x + dx, yv)
        if tile_v in world_map or tile_v in blocked_doors:
            return False
        x += dx * TILE

    # Horizontal raycasting
    y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
    for _ in range(0, int(abs(delta_y)) // TILE):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = mapping(xh, y + dy)
        if tile_h in world_map or tile_h in blocked_doors:
            return False
        y += dy * TILE

    return True


class Interaction:
    def __init__(self, player, sprites, drawing):
        self.player = player
        self.sprites = sprites
        self.drawing = drawing
        self.new_game = True
        self.pain_sound = pygame.mixer.Sound('sound/pain.wav')
        self.damage_sound = pygame.mixer.Sound('sound/player_hit.wav')

    def interaction_objects(self):
        if self.player.shot and self.drawing.shot_animation_trigger:
            for obj in sorted(self.sprites.list_of_objects, key=lambda obj: obj.distance_to_sprite):
                if obj.is_on_fire[1] and obj.is_dead != 'immortal' and not obj.is_dead:
                    if ray_casting_npc_player(obj.x, obj.y, self.sprites.blocked_doors, world_map, self.player.pos):
                        if obj.flag == 'npc':
                            self.pain_sound.play()
                        obj.is_dead = True
                        obj.blocked = None
                        self.drawing.shot_animation_trigger = False
                    elif obj.flag in {'door_h', 'door_v'} and obj.distance_to_sprite < TILE:
                        obj.door_open_trigger = True
                        obj.blocked = None
                    break

    def npc_action(self):
        for obj in self.sprites.list_of_objects:
            if obj.flag == 'npc' and not obj.is_dead:
                if ray_casting_npc_player(obj.x, obj.y, self.sprites.blocked_doors, world_map, self.player.pos):
                    obj.npc_action_trigger = True
                    self.npc_move(obj)
                    self.nps_damage(obj)
                else:
                    obj.npc_action_trigger = False

    def npc_move(self, obj):
        if abs(obj.distance_to_sprite) > TILE:
            dx, dy = obj.x - self.player.pos[0], obj.y - self.player.pos[1]
            obj.x += 1 if dx < 0 else -1
            obj.y += 1 if dy < 0 else -1

    def nps_damage(self, obj):
        if time.time() - self.player.last_damage_time > 2:
            dx = self.player.pos[0] - obj.pos[0]
            dy = self.player.pos[1] - obj.pos[1]
            d = dx * dx + dy * dy
            if d < (TILE * 2) ** 2:
                self.player.damage(15)
                self.player.last_damage_time = time.time()
                self.damage_sound.play()


    def clear_world(self):
        # Remove objects marked for deletion
        self.sprites.list_of_objects = [obj for obj in self.sprites.list_of_objects if not obj.delete]

    @staticmethod
    def play_music():
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.mixer.music.load('sound/theme.mp3')
        pygame.mixer.music.play(10)

    def check_die(self):
        if self.player.life == 0:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('sound/lose.mp3')
            pygame.mixer.music.play()
            show_retry_menu_loop = True
            while show_retry_menu_loop:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        exit()
                show_retry_menu_loop = self.drawing.lose()
            self.new_game = True
        else:
            self.new_game = False



    def check_win(self):
        if not any(obj.flag == 'npc' and not obj.is_dead for obj in self.sprites.list_of_objects):
            pygame.mixer.music.stop()
            pygame.mixer.music.load('sound/win.mp3')
            pygame.mixer.music.play()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        exit()
                self.drawing.win()
