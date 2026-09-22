import pygame
import sys
import random
import logger
from config import WIDTH, HEIGHT, FPS

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

import audio
import sprites
import ui
import save_manager
from game_state import GameState

audio.init_audio()

game_state = GameState()
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()

def do_save(slot):
    save_manager.save_game(slot, game_state, player, enemies, bunkers, bullets, mystery_ship)

def do_load(slot):
    global player, mystery_ship
    result = save_manager.load_game(slot, game_state, all_sprites, enemies, bunkers, bullets, WIDTH, HEIGHT)
    if result:
        player, mystery_ship = result
        game_state.in_pause_menu = False

def do_return(): game_state.in_pause_menu = False
def do_quit(): global running; running = False

button_width, button_height = 300, 50
center_x = WIDTH // 2 - button_width // 2

pause_buttons = [
    ui.Button(center_x - 350, 250, button_width, button_height, "Save to Slot 1", action=do_save, action_args=(1,)),
    ui.Button(center_x, 250, button_width, button_height, "Save to Slot 2", action=do_save, action_args=(2,)),
    ui.Button(center_x + 350, 250, button_width, button_height, "Save to Slot 3", action=do_save, action_args=(3,)),
    ui.Button(center_x - 350, 550, button_width, button_height, "Load from Slot 1", action=do_load, action_args=(1,)),
    ui.Button(center_x, 550, button_width, button_height, "Load from Slot 2", action=do_load, action_args=(2,)),
    ui.Button(center_x + 350, 550, button_width, button_height, "Load from Slot 3", action=do_load, action_args=(3,)),
    ui.Button(center_x, 650, button_width, button_height, "Return to Game", (0, 150, 0), (0, 200, 0), action=do_return),
    ui.Button(center_x, 750, button_width, button_height, "Quit Game", (150, 0, 0), (200, 0, 0), action=do_quit)
]

def reset_game():
    global player, enemies, bunkers, mystery_ship, all_sprites, bullets
    all_sprites.empty()
    bullets.empty()
    player = sprites.Player(WIDTH // 2, HEIGHT - 100)
    all_sprites.add(player)
    enemies = sprites.create_enemies(game_state.level, all_sprites)
    bunkers = sprites.create_bunkers(all_sprites)
    mystery_ship = sprites.MysteryShip()
    all_sprites.add(mystery_ship)
    sprites.enemy_move_direction = 'left'

    game_state.game_over = False
    game_state.paused = False
    game_state.in_pause_menu = False
    game_state.math_active = False

player = None
enemies = None
bunkers = None
mystery_ship = None
reset_game()

running = True
mouse_pos = (0, 0)
key_buffer = []

while running:
    clock.tick(FPS)
    mouse_click = False

    if game_state.score >= game_state.next_math_score and not game_state.math_active:
        game_state.math_active = True
        game_state.math_timer = FPS * 10
        game_state.math_input = ""
        a, b = random.randint(11, 99), random.randint(11, 99)
        game_state.math_problem = f"{a} + {b}"
        game_state.math_answer = str(a + b)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if game_state.math_active:
                key_event = 'RETURN' if event.key == pygame.K_RETURN else 'BACKSPACE' if event.key == pygame.K_BACKSPACE else None
                game_state.process_math_input(key_event, event.unicode, player)
                continue

            if event.unicode.isalnum():
                key_buffer.append(event.unicode.lower())
                if len(key_buffer) > 5: key_buffer.pop(0)
                word = "".join(key_buffer)

                if word.endswith("xml"):
                    game_state.excel_mode = not game_state.excel_mode
                    key_buffer.clear()
                elif word.endswith("b4"):
                    game_state.trigger_battleship_strike(enemies)
                    key_buffer.clear()

            if event.key == pygame.K_p:
                game_state.paused = not game_state.paused
            if event.key == pygame.K_r and game_state.game_over:
                game_state = GameState()
                reset_game()
            if event.key == pygame.K_ESCAPE:
                if game_state.in_menu:
                    running = False
                elif game_state.game_over:
                    game_state.in_menu = True
                else:
                    game_state.in_pause_menu = not game_state.in_pause_menu
            if event.key == pygame.K_SPACE and game_state.in_menu:
                game_state.in_menu = False
                reset_game()
            if event.key == pygame.K_l and game_state.in_menu:
                if game_state.save_slots:
                    for slot in range(1, 4):
                        if slot in game_state.save_slots and game_state.save_slots[slot]:
                            do_load(slot)
                            game_state.in_menu = False
                            break
            if event.key == pygame.K_q and game_state.game_over:
                running = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True
#логика интерфейса
    if game_state.math_active:
        game_state.update_math_timer(player)
        screen.fill((0, 0, 30))
        all_sprites.draw(screen)
        ui.draw_hud(screen, game_state, player)
        ui.draw_math_puzzle(screen, game_state)
        pygame.display.flip()
        continue

    if game_state.in_pause_menu:
        for btn in pause_buttons:
            btn.check_hover(mouse_pos)
            if mouse_click:
                btn.is_clicked(mouse_pos, mouse_click)
        ui.draw_pause_menu(screen, game_state, pause_buttons)
        pygame.display.flip()
        continue

    if game_state.in_menu:
        ui.draw_main_menu(screen, game_state)
        pygame.display.flip()
        continue

    if game_state.game_over:
        ui.draw_game_over(screen, game_state)
        pygame.display.flip()
        continue

    if game_state.paused:
        font = pygame.font.SysFont('Arial', 72)
        text = font.render('PAUSED', True, (255, 255, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
        pygame.display.flip()
        continue

#физика
    keys = pygame.key.get_pressed()
    player.update(keys, bullets, all_sprites, game_state.excel_mode)

    change_direction = False
    for enemy in enemies:
        if (enemy.rect.left <= 0 and sprites.enemy_move_direction == 'left') or \
                (enemy.rect.right >= WIDTH and sprites.enemy_move_direction == 'right'):
            change_direction = True
            break

    if change_direction:
        sprites.enemy_move_direction = 'right' if sprites.enemy_move_direction == 'left' else 'left'
        for enemy in enemies:
            enemy.move_down(40)

    enemies.update(game_state.excel_mode)

    for enemy in enemies:
        if not enemy.is_dying:
            enemy_bullet = enemy.shoot(bullets)
            if enemy_bullet:
                bullets.add(enemy_bullet)
                all_sprites.add(enemy_bullet)

    bullets.update()
    mystery_ship.update()

#столкновения
    for bullet in list(bullets):
        bunker_hit = pygame.sprite.spritecollide(bullet, bunkers, False)
        if bunker_hit:
            if not (bullet.owner == "player" and bullet.piercing):
                bunker_hit[0].hit()
                bullet.kill()
                continue

        if bullet.owner == "player":
            enemy_hit = pygame.sprite.spritecollide(bullet, enemies, False)
            if enemy_hit:
                for enemy in enemy_hit:
                    if not enemy.is_dying:
                        points = enemy.start_death()
                        game_state.add_score(points)
                        if not bullet.piercing:
                            bullet.kill()
                        break

            elif mystery_ship.active and mystery_ship.rect.colliderect(bullet.rect):
                if not bullet.piercing:
                    bullet.kill()
                points = mystery_ship.take_damage()
                if points:
                    game_state.add_score(points)

        elif bullet.owner == "enemy":
            if player.rect.colliderect(bullet.rect):
                bullet.kill()
                if player.take_damage() and player.lives <= 0:
                    game_state.game_over = True

    if len(enemies) == 0:
        game_state.next_level()
        reset_game()

    for enemy in enemies:
        if enemy.rect.bottom >= HEIGHT - 100:
            game_state.game_over = True
            break

    screen.fill((0, 0, 30))
    all_sprites.draw(screen)
    ui.draw_hud(screen, game_state, player)
    pygame.display.flip()

pygame.quit()
sys.exit()