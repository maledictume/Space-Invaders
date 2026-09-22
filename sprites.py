import pygame
import random
from config import *
import audio

pygame.font.init()
easter_font = pygame.font.SysFont('Courier', 24, bold=True)
xml_img = easter_font.render('</>', True, (0, 255, 0))
excel_img = pygame.Surface((80, 40))
excel_img.fill((33, 115, 70))
excel_img.blit(easter_font.render('XLS', True, (255, 255, 255)), (15, 5))

def load_img(path, size, color):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf

player_image = load_img('space/player.png', (80, 40), (0, 255, 0))
bullet_image = load_img('space/player_bullet.png', (10, 20), (255, 255, 0))
death_image_orig = load_img('space/enemy_die.png', (60, 30), (255, 255, 255))
secret_enemy_img = load_img('space/secret_enemy.png', (80, 40), (255, 0, 255))

enemy_colors = [
    ((255, 0, 0), (200, 0, 0)),
    ((255, 255, 0), (200, 200, 0)),
    ((0, 255, 255), (0, 200, 200))
]

enemy_textures = []
for i in range(3):
    img1 = load_img(f'space/{i + 1}_1enemy.png', (60, 30), enemy_colors[i][0])
    img2 = load_img(f'space/{i + 1}_2enemy.png', (60, 30), enemy_colors[i][1])
    enemy_textures.append((img1, img2, i))

bunker_imgs = [load_img(f'space/def_{i}.png', (120, 80), (0, max(0, 255 - i * 30), 0)) for i in range(7)]

m = 5
death_image = pygame.transform.scale(death_image_orig, (16 * m, 8 * m))
enemy_bullet_image = pygame.Surface((4, 10))
enemy_bullet_image.fill((255, 50, 50))

enemy_move_direction = 'left'

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        m = 10
        self.original_image = pygame.transform.scale(player_image, (16 * m, 8 * m))
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 8
        self.shoot_cooldown = 0
        self.lives = 3
        self.invincible = 0
        self.fast_shoot_timer = 0

    def update(self, keys, bullets_group, all_sprites, excel_mode=False):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.fast_shoot_timer > 0:
            self.fast_shoot_timer -= 1

        player_bullet_exists = any(bullet.owner == "player" for bullet in bullets_group)
        can_shoot = self.shoot_cooldown == 0 and (self.fast_shoot_timer > 0 or not player_bullet_exists)

        if keys[pygame.K_SPACE] and can_shoot:
            is_piercing = self.fast_shoot_timer > 0
            bullet = Bullet(self.rect.centerx, self.rect.top, -15, "player", excel_mode, is_piercing)
            bullets_group.add(bullet)
            all_sprites.add(bullet)
            self.shoot_cooldown = 3 if is_piercing else 15
            audio.play_sound('shoot')

        if self.invincible > 0:
            self.invincible -= 1
            if self.invincible % 10 < 5:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    def take_damage(self):
        if self.invincible == 0:
            self.lives -= 1
            self.invincible = 120
            return True
        return False

    def to_dict(self):
        return {
            'x': self.rect.x, 'y': self.rect.y,
            'lives': self.lives, 'invincible': self.invincible,
            'shoot_cooldown': self.shoot_cooldown
        }

    def from_dict(self, data):
        self.rect.x = data.get('x', WIDTH // 2)
        self.rect.y = data.get('y', HEIGHT - 100)
        self.lives = data.get('lives', 3)
        self.invincible = data.get('invincible', 0)
        self.shoot_cooldown = data.get('shoot_cooldown', 0)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image1, image2, death_image, enemy_type):
        super().__init__()
        m = 5
        self.image1 = pygame.transform.scale(image1, (16 * m, 8 * m))
        self.image2 = pygame.transform.scale(image2, (16 * m, 8 * m))
        self.death_image = death_image
        self.image = self.image1
        self.rect = self.image.get_rect(topleft=(x, y))
        self.enemy_type = enemy_type
        self.speed = 1
        self.animation_counter = 0
        self.is_dying = False
        self.death_timer = 0
        self.score_value = [30, 20, 10][enemy_type]
        self.shoot_chance = [0.001, 0.0005, 0.0003][enemy_type]

    def start_death(self):
        self.is_dying = True
        self.death_timer = FPS / 4
        audio.play_sound('explosion')
        return self.score_value

    def update(self, excel_mode=False):
        global enemy_move_direction
        if self.is_dying:
            self.image = self.death_image
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.kill()
            return
        self.animation_counter += 1
        if self.animation_counter >= 30:
            self.animation_counter = 0

        if excel_mode:
            self.image = excel_img
        else:
            self.image = self.image1 if self.animation_counter < 15 else self.image2

        if enemy_move_direction == 'left':
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

    def move_down(self, pixels):
        self.rect.y += pixels

    def shoot(self, bullets_group):
        if random.random() < self.shoot_chance:
            enemy_bullets_count = sum(1 for bullet in bullets_group if bullet.owner == "enemy")
            if enemy_bullets_count < 5:
                bullet = Bullet(self.rect.centerx, self.rect.bottom, 7, "enemy")
                audio.play_sound('enemy_shoot')
                return bullet
        return None

    def to_dict(self):
        return {
            'x': self.rect.x, 'y': self.rect.y,
            'type': self.enemy_type,
            'animation_counter': self.animation_counter,
            'speed': self.speed
        }

    @classmethod
    def from_dict(cls, data, enemy_textures, death_image):
        img1, img2, _ = enemy_textures[data['type']]
        enemy = cls(data['x'], data['y'], img1, img2, death_image, data['type'])
        enemy.animation_counter = data.get('animation_counter', 0)
        enemy.speed = data.get('speed', 1)
        return enemy


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, owner, excel_mode=False, piercing=False):
        super().__init__()
        self.owner = owner
        self.piercing = piercing
        if owner == "player":
            self.image = xml_img if excel_mode else pygame.transform.scale(bullet_image, (10, 20))
        else:
            self.image = enemy_bullet_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

    def to_dict(self):
        return {
            'x': self.rect.centerx, 'y': self.rect.centery,
            'speed': self.speed, 'owner': self.owner
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['x'], data['y'], data['speed'], data['owner'])


class Bunker(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = [pygame.transform.scale(img, (120, 80)) for img in bunker_imgs]
        self.max_stage = len(self.images) - 1
        self.stage = 0
        self.image = self.images[self.stage]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = BUNKER_HEALTH

    def update(self):
        self.image = self.images[self.stage]

    def hit(self):
        self.stage += 1
        if self.stage > self.max_stage:
            self.kill()
            return True
        self.image = pygame.transform.rotate(
            self.images[self.stage],
            random.randint(-3, 3)
        )
        return False

    def to_dict(self):
        return {
            'x': self.rect.x, 'y': self.rect.y,
            'health': self.health, 'stage': self.stage
        }

    @classmethod
    def from_dict(cls, data):
        bunker = cls(data['x'], data['y'])
        bunker.health = data.get('health', 4)
        bunker.stage = data.get('stage', 0)
        bunker.update()
        return bunker


class MysteryShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(secret_enemy_img, (100, 50))
        self.original_image = self.image
        self.rect = self.image.get_rect(topleft=(-150, 80))
        self.speed = 5
        self.direction = 1
        self.hp = 1
        self.active = False
        self.spawn_timer = random.randint(400, 800)
        self.animation_counter = 0

    def update(self):
        self.spawn_timer -= 1
        if self.spawn_timer <= 0 and not self.active:
            self.activate()
        if self.active:
            self.rect.x += self.speed * self.direction
            self.animation_counter += 1
            if self.animation_counter % 20 < 10:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(150)
            if (self.direction == 1 and self.rect.left > WIDTH) or \
                    (self.direction == -1 and self.rect.right < 0):
                self.deactivate()

    def activate(self):
        self.active = True
        self.hp = 1
        self.direction = random.choice([-1, 1])
        if self.direction == 1:
            self.rect.left = -100
        else:
            self.rect.right = WIDTH + 100
        self.rect.y = random.randint(50, 150)
        audio.play_sound('mystery')

    def deactivate(self):
        self.active = False
        self.spawn_timer = random.randint(400, 800)
        self.rect.topleft = (-200, 80)

    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.deactivate()
            self.kill()
            return random.choice(MYSTERY_SCORES)
        return 0

    def to_dict(self):
        return {
            'active': self.active, 'spawn_timer': self.spawn_timer,
            'direction': self.direction, 'x': self.rect.x, 'y': self.rect.y
        }

    def from_dict(self, data):
        self.active = data.get('active', False)
        self.spawn_timer = data.get('spawn_timer', random.randint(300, 600))
        self.direction = data.get('direction', 1)
        self.rect.x = data.get('x', -100)
        self.rect.y = data.get('y', 50)

def create_enemies(level, all_sprites_group):
    enemy_rows = min(2 + (level // 2), 5)
    enemy_cols = 11
    start_x, start_y = 100, 100
    spacing_x, spacing_y = 90, 80
    enemies_group = pygame.sprite.Group()
    base_speed = ENEMY_SPEEDS[min(level - 1, len(ENEMY_SPEEDS) - 1)]

    for row in range(enemy_rows):
        for kind in range(3):
            img1, img2, enemy_type = enemy_textures[kind]
            for col in range(enemy_cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y + kind * 150
                e = Enemy(x, y, img1, img2, death_image, enemy_type)
                e.speed = base_speed
                enemies_group.add(e)
                all_sprites_group.add(e)

    return enemies_group

def create_bunkers(all_sprites_group):
    bunkers_group = pygame.sprite.Group()
    for i in range(4):
        bunker = Bunker(200 + i * 400, HEIGHT - 200)
        bunkers_group.add(bunker)
        all_sprites_group.add(bunker)
    return bunkers_group