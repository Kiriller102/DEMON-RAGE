import math
import pygame
from settings import *
from map import collision_walls


class Player:
    def __init__(self, sprites):
        self.x, self.y = player_pos
        self.life = 20
        self.sprites = sprites
        self.angle = player_angle
        self.sensitivity = 0.004
        self.speed = player_speed
        self.side = 50  # Player's hitbox size
        self.rect = pygame.Rect(*player_pos, self.side, self.side)
        self.shot = False  # Weapon state
        self.last_damage_time = 0
        self.damage_cooldown = 2

    @property
    def pos(self):
        return self.x, self.y

    @property
    def collision_list(self):
        """Combine static walls and blocked sprite objects into one collision list."""
        return collision_walls + [
            pygame.Rect(*obj.pos, obj.side, obj.side)
            for obj in self.sprites.list_of_objects
            if obj.blocked
        ]

    def damage(self, hit):
        """ """
        if self.life > hit:
            self.life -= hit
        elif self.life <= hit:
            self.life = 0


    def detect_collision(self, dx, dy):
        """Check and handle collisions for given movement deltas."""
        next_rect = self.rect.move(dx, dy)
        collisions = next_rect.collidelistall(self.collision_list)

        if collisions:
            delta_x, delta_y = 0, 0
            for index in collisions:
                hit_rect = self.collision_list[index]
                if dx > 0:  # Moving right
                    delta_x += next_rect.right - hit_rect.left
                elif dx < 0:  # Moving left
                    delta_x += hit_rect.right - next_rect.left
                if dy > 0:  # Moving down
                    delta_y += next_rect.bottom - hit_rect.top
                elif dy < 0:  # Moving up
                    delta_y += hit_rect.bottom - next_rect.top

            # Resolve collision priority
            if abs(delta_x - delta_y) < 10:
                dx, dy = 0, 0
            elif delta_x > delta_y:
                dy = 0
            else:
                dx = 0

        # Update position after collision resolution
        self.x += dx
        self.y += dy

    def movement(self):
        """Handle all player movement logic."""
        self.process_inputs()
        self.rect.center = self.x, self.y
        self.angle %= DOUBLE_PI

    def process_inputs(self):
        """Process keyboard and mouse inputs."""
        keys = pygame.key.get_pressed()
        sin_a, cos_a = math.sin(self.angle), math.cos(self.angle)

        # Handle keyboard inputs for movement
        dx = dy = 0
        if keys[pygame.K_w]:  # Move forward
            dx += self.speed * cos_a
            dy += self.speed * sin_a
        if keys[pygame.K_s]:  # Move backward
            dx -= self.speed * cos_a
            dy -= self.speed * sin_a
        if keys[pygame.K_a]:  # Strafe left
            dx += self.speed * sin_a
            dy -= self.speed * cos_a
        if keys[pygame.K_d]:  # Strafe right
            dx -= self.speed * sin_a
            dy += self.speed * cos_a
        self.detect_collision(dx, dy)

        # Handle mouse input
        self.handle_mouse()

        # Handle additional events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.shot = True

    def handle_mouse(self):
        """Handle mouse movement for changing the player's angle."""
        if pygame.mouse.get_focused():
            mouse_x = pygame.mouse.get_pos()[0]
            difference = mouse_x - HALF_WIDTH
            pygame.mouse.set_pos((HALF_WIDTH, HALF_HEIGHT))
            self.angle += difference * self.sensitivity
