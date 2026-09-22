import json
import os
import datetime
import logger
import sprites


def save_game(slot, game_state, player, enemies, bunkers, bullets, mystery_ship):
    try:
        save_data = {
            'level': game_state.level,
            'score': game_state.score,
            'player': player.to_dict(),
            'enemies': [enemy.to_dict() for enemy in enemies if not enemy.is_dying],
            'bunkers': [bunker.to_dict() for bunker in bunkers],
            'bullets': [bullet.to_dict() for bullet in bullets],
            'mystery_ship': mystery_ship.to_dict(),
            'enemy_move_direction': sprites.enemy_move_direction,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(f'save_slot_{slot}.json', 'w') as f:
            json.dump(save_data, f, indent=4)
        game_state.save_slots = game_state.check_save_slots()
        return True
    except Exception as e:
        logger.log_error(f"Save error slot {slot}", e)
        return False


def load_game(slot, game_state, all_sprites, enemies, bunkers, bullets, WIDTH, HEIGHT):
    filename = f'save_slot_{slot}.json'
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)

        all_sprites.empty()
        bullets.empty()
        enemies.empty()
        bunkers.empty()

        game_state.level = save_data.get('level', 1)
        game_state.score = save_data.get('score', 0)
        game_state.game_over = False
        game_state.paused = False

        player = sprites.Player(WIDTH // 2, HEIGHT - 100)
        player.from_dict(save_data.get('player', {}))
        all_sprites.add(player)

        for e_data in save_data.get('enemies', []):
            if e_data.get('type', 0) < len(sprites.enemy_textures):
                enemy = sprites.Enemy.from_dict(e_data, sprites.enemy_textures, sprites.death_image)
                enemies.add(enemy)
                all_sprites.add(enemy)

        for b_data in save_data.get('bunkers', []):
            bunker = sprites.Bunker.from_dict(b_data)
            bunkers.add(bunker)
            all_sprites.add(bunker)

        for b_data in save_data.get('bullets', []):
            bullet = sprites.Bullet.from_dict(b_data)
            bullets.add(bullet)
            all_sprites.add(bullet)

        mystery_ship = sprites.MysteryShip()
        mystery_ship.from_dict(save_data.get('mystery_ship', {}))
        all_sprites.add(mystery_ship)

        sprites.enemy_move_direction = save_data.get('enemy_move_direction', 'left')
        game_state.save_slots = game_state.check_save_slots()

        return player, mystery_ship
    except Exception as e:
        logger.log_error(f"Load error slot {slot}", e)
        return None