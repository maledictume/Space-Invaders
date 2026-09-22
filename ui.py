import pygame
from config import WIDTH, HEIGHT, FPS


class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150), action=None,
                 action_args=()):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 32)
        self.action = action
        self.action_args = action_args

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 3, border_radius=10)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        if self.rect.collidepoint(pos) and click:
            if self.action:
                self.action(*self.action_args)
            return True
        return False


def draw_save_slots_text(screen, game_state, start_y):
    font = pygame.font.SysFont('Arial', 36)
    if not game_state.save_slots:
        return
    title_str = 'Available save slots:' if not game_state.in_pause_menu else 'Current save slots:'
    text = font.render(title_str, True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, start_y - 50))

    y_pos = start_y
    for slot in range(1, 4):
        data = game_state.save_slots.get(slot)
        if data:
            text = font.render(
                f'Slot {slot}: Level {data["level"]}, Score {data["score"]}, Lives {data.get("lives", 3)}', True,
                (0, 255, 0))
        else:
            text = font.render(f'Slot {slot}: Empty', True, (150, 150, 150))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += 45


def draw_main_menu(screen, game_state):
    screen.fill((0, 0, 30))
    font = pygame.font.SysFont('Arial', 72)
    title_text = font.render('SPACE INVADERS', True, (255, 255, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    font = pygame.font.SysFont('Arial', 48)
    text = font.render('HIGH SCORES', True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))
    for i, (name, score) in enumerate(game_state.high_scores):
        text = font.render(f'{i + 1}. {name}: {score}', True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 280 + i * 60))

    font = pygame.font.SysFont('Arial', 36)
    text = font.render('Press SPACE to start or L to load game', True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 250))
    draw_save_slots_text(screen, game_state, HEIGHT - 130)


def draw_pause_menu(screen, game_state, buttons):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont('Arial', 72)
    title_text = font.render('PAUSE MENU', True, (255, 255, 0))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    for btn in buttons:
        btn.draw(screen)

    draw_save_slots_text(screen, game_state, 350)
    font_small = pygame.font.SysFont('Arial', 36)
    text = font_small.render('Press ESC to return to game', True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))


def draw_game_over(screen, game_state):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('Arial', 72)
    text = font.render('GAME OVER', True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
    font = pygame.font.SysFont('Arial', 36)
    text = font.render(f'Final Score: {game_state.score}', True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    text = font.render('Press R to restart or Q to quit', True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 100))


def draw_hud(screen, game_state, player):
    font = pygame.font.SysFont('Arial', 36)
    s_text = f'Rows Migrated: {game_state.score}' if game_state.excel_mode else f'Score: {game_state.score}'
    l_text = f'Sprint: {game_state.level}' if game_state.excel_mode else f'Level: {game_state.level}'
    screen.blit(font.render(s_text, True, (255, 255, 255)), (20, 20))
    screen.blit(font.render(l_text, True, (255, 255, 255)), (20, 70))
    screen.blit(font.render(f'Lives: {player.lives}', True, (255, 255, 255)), (20, 120))

    esc_text = font.render('Press ESC for menu', True, (200, 200, 200))
    screen.blit(esc_text, (WIDTH - esc_text.get_width() - 20, 20))


def draw_math_puzzle(screen, game_state):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))
    screen.blit(overlay, (0, 0))
    font = pygame.font.SysFont('Arial', 48)
    title = font.render('SYSTEM OVERRIDE: SOLVE TO CONTINUE', True, (255, 0, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    font_small = pygame.font.SysFont('Arial', 36)
    desc = font_small.render(f'Calculate: {game_state.math_problem}', True, (255, 255, 255))
    screen.blit(desc, (WIDTH // 2 - desc.get_width() // 2, 300))
    time_left = game_state.math_timer // FPS
    timer_txt = font.render(f'Time: {time_left}', True, (255, 255, 0))
    screen.blit(timer_txt, (WIDTH // 2 - timer_txt.get_width() // 2, 400))
    input_txt = font.render(f'> {game_state.math_input}_', True, (0, 255, 0))
    screen.blit(input_txt, (WIDTH // 2 - input_txt.get_width() // 2, 500))