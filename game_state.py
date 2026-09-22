import json
import os
import random
from config import FPS

class GameState:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.in_menu = True
        self.in_pause_menu = False
        self.excel_mode = False

        self.math_active = False
        self.math_timer = 0
        self.math_input = ""
        self.math_problem = ""
        self.math_answer = ""
        self.next_math_score = 500
        self.math_score_step = 1000

        self.high_scores = self.load_high_scores()
        self.save_slots = self.check_save_slots()

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except:
            return [["Player", 1000], ["Player", 800], ["Player", 600], ["Player", 400], ["Player", 200]]

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def check_save_slots(self):
        save_slots = {}
        for i in range(1, 4):
            filename = f'save_slot_{i}.json'
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        data = json.load(f)
                        save_slots[i] = {
                            'level': data.get('level', 1),
                            'score': data.get('score', 0),
                            'timestamp': data.get('timestamp', 'Unknown'),
                            'lives': data.get('player', {}).get('lives', 3)
                        }
                except:
                    save_slots[i] = None
            else:
                save_slots[i] = None
        return save_slots

    def add_score(self, points):
        self.score += points
        if self.score > self.high_scores[0][1]:
            self.high_scores.insert(0, ["Player", self.score])
            self.high_scores = self.high_scores[:5]
            self.save_high_scores()

    def next_level(self):
        self.level += 1
        return True

    def trigger_battleship_strike(self, enemies_group):
        rows = {}
        for e in enemies_group:
            if not e.is_dying:
                rows.setdefault(e.rect.y, []).append(e)
        for y, row_enemies in rows.items():
            if len(row_enemies) == 4:
                for e in row_enemies:
                    points = e.start_death()
                    self.add_score(points * 10)
                return

    def process_math_input(self, key_event, unicode_char, player):
        if key_event == 'RETURN':
            if self.math_input == self.math_answer:
                self.math_active = False
                player.invincible = 180
                player.fast_shoot_timer = FPS * 1
            else:
                player.take_damage()
                self.math_active = False
            self.next_math_score += self.math_score_step
            self.math_score_step += 500
        elif key_event == 'BACKSPACE':
            self.math_input = self.math_input[:-1]
        else:
            if unicode_char.isdigit() and len(self.math_input) < 10:
                self.math_input += unicode_char

    def update_math_timer(self, player):
        self.math_timer -= 1
        if self.math_timer <= 0:
            player.take_damage()
            self.math_active = False
            self.next_math_score += self.math_score_step
            self.math_score_step += 500