from settings import *
import pygame
from numba.core import types
from numba.typed import Dict
from numba import int64

_ = False
matrix_map = [
    [1, 1, 1, 1, 4, 1, 1, 2, 1, 4, 1, 1, 5, 1, 1, 1, 2, 1, 1, 1, 5, 1, 1, 1],
    [1, _, _, _, _, _, 1, _, _, _, _, _, _, _, _, _, _, 4, _, _, _, _, _, 1],
    [1, _, 2, 2, _, _, _, _, _, 7, 7, 7, _, _, _, 2, _, _, _, _, 4, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, _, 7, 7, _, _, _, 2, _, _, _, _, _, _, 1],
    [1, _, 2, 2, _, _, _, _, _, _, _, _, 7, _, 4, _, 3, 2, _, _, _, 4, _, 1],
    [1, _, _, _, _, _, 4, _, _, 7, 2, _, 7, _, _, _, 2, _, _, 4, _, _, _, 1],
    [3, _, 2, _, _, _, 2, _, _, 2, _, _, 7, _, _, _, 4, _, _, _, _, 4, _, 2],
    [1, _, _, 2, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, 2, _, _, _, _, _, _, _, 2, _, _, _, 2, _, _, _, _, 1, 1, _, _, 3],
    [1, _, 2, _, _, _, 7, 1, _, 1, _, _, _, 2, 1, _, _, _, _, 1, 1, _, _, 1],
    [4, _, _, _, _, 3, _, 1, _, _, 1, _, _, _, _, _, _, _, _, _, _, _, _, 4],
    [2, _, 2, _, 1, _, _, _, _, 2, _, _, 2, _, _, _, _, _, _, _, _, 2, _, 1],
    [1, _, _, _, _, _, 2, _, _, _, _, _, 2, 2, _, _, _, _, _, _, 2, 2, _, 1],
    [1, _, _, 2, _, _, _, _, 2, _, _, _, _, 2, 3, 2, _, _, 2, 2, 2, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, 3, 2, 1, 1, 6, 1, 1, 2, 3, 1, 1, 1, 4, 1, 1, 1, 5, 1, 1, 1, 1, 1, 1]
]

WORLD_WIDTH = len(matrix_map[0]) * TILE
WORLD_HEIGHT = len(matrix_map) * TILE

world_map = Dict.empty(key_type=types.UniTuple(int64, 2), value_type=int64)
collision_walls = []

for y, row in enumerate(matrix_map):
    for x, value in enumerate(row):
        if value:
            collision_walls.append(pygame.Rect(x * TILE, y * TILE, TILE, TILE))
            world_map[(x * TILE, y * TILE)] = value

print(f"World map loaded with {len(world_map)} elements.")
