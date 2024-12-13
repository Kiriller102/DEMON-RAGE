import time

from player import Player
from sprite_objects import *
from ray_casting import ray_casting_walls
from drawing import Drawing
from interaction import Interaction

fps = FPS
newGame = True

pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
sc_map = pygame.Surface(MINIMAP_RES)
sprites = Sprites()
clock = pygame.time.Clock()
player = Player(sprites)
drawing = Drawing(sc, sc_map, player, clock)
interaction = Interaction(player, sprites, drawing)
# drawing.menu()
# pygame.mouse.set_visible(False)

while True:
    if interaction.new_game:
        sprites.__init__()
        clock = pygame.time.Clock()
        player = Player(sprites)
        drawing = Drawing(sc, sc_map, player, clock)
        interaction = Interaction(player, sprites, drawing)
        drawing.menu()
        interaction.play_music()
        time.sleep(0.5)
        pygame.mouse.set_visible(False)
        interaction.new_game = False

    player.movement()
    drawing.background(player.angle)
    walls, wall_shot = ray_casting_walls(player, drawing.textures)
    drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
    drawing.fps(clock)

    # drawing.mini_map(player)
    drawing.player_weapon([wall_shot, sprites.sprite_shot])
    drawing.player_life()
    interaction.interaction_objects()
    interaction.npc_action()
    interaction.clear_world()
    interaction.check_win()
    interaction.check_die()
    pygame.display.flip()
    clock.tick(fps)

