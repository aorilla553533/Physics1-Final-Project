"""
menu.py
Handles the main menu, level selection (with locked/unlocked indicators),
leaderboard display, and player name entry.
"""

import sys
import pygame
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_SKY,
    COLOR_SKY_TOP,
    COLOR_SKY_BOTTOM,
    COLOR_GROUND_TOP,
    COLOR_GROUND_BOTTOM,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_GREEN,
    COLOR_GRAY,
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_BLUE,
    COLOR_WOOD,
    COLOR_CLOUD,
    LEVEL_ORDER,
    FPS,
    CHARACTERS,
    CHARACTER_DESCRIPTIONS,
)
from database import get_player_leaderboard, is_level_completed, init_db
from game import run_level


def _get_font(size, bold=False):
    """Load a playful font with system fallback."""
    for name in ["comicsansms", "segoeui", "georgia", "arial"]:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            # Quick validation render
            font.render(" ", True, (0, 0, 0))
            return font
        except Exception:
            continue
    return pygame.font.SysFont("arial", size, bold=bold)


def _create_sky_gradient():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(COLOR_SKY_TOP[0] * (1 - ratio) + COLOR_SKY_BOTTOM[0] * ratio)
        g = int(COLOR_SKY_TOP[1] * (1 - ratio) + COLOR_SKY_BOTTOM[1] * ratio)
        b = int(COLOR_SKY_TOP[2] * (1 - ratio) + COLOR_SKY_BOTTOM[2] * ratio)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    return surf


def _create_ground_gradient(width, height):
    surf = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(COLOR_GROUND_TOP[0] * (1 - ratio) + COLOR_GROUND_BOTTOM[0] * ratio)
        g = int(COLOR_GROUND_TOP[1] * (1 - ratio) + COLOR_GROUND_BOTTOM[1] * ratio)
        b = int(COLOR_GROUND_TOP[2] * (1 - ratio) + COLOR_GROUND_BOTTOM[2] * ratio)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    return surf


class Cloud:
    def __init__(self, x, y, w, h, speed):
        self.x = float(x)
        self.y = float(y)
        self.w = int(w)
        self.h = int(h)
        self.speed = float(speed)

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > SCREEN_WIDTH + self.w:
            self.x = -self.w

    def draw(self, surface):
        pygame.draw.ellipse(surface, COLOR_CLOUD, (int(self.x), int(self.y), self.w, self.h))
        pygame.draw.ellipse(surface, COLOR_CLOUD,
                            (int(self.x + self.w * 0.25), int(self.y - self.h * 0.25),
                             int(self.w * 0.6), int(self.h * 0.7)))
        pygame.draw.ellipse(surface, COLOR_CLOUD,
                            (int(self.x + self.w * 0.55), int(self.y - self.h * 0.1),
                             int(self.w * 0.5), int(self.h * 0.6)))


def _init_clouds():
    return [
        Cloud(100, 80, 120, 50, 12),
        Cloud(500, 140, 160, 60, 8),
        Cloud(800, 60, 100, 45, 15),
        Cloud(300, 200, 140, 55, 10),
    ]


def _draw_menu_background(screen, clouds, dt, ground_y=550):
    screen.blit(_create_sky_gradient(), (0, 0))
    for cloud in clouds:
        cloud.update(dt)
        cloud.draw(screen)
    ground_h = SCREEN_HEIGHT - ground_y
    screen.blit(_create_ground_gradient(SCREEN_WIDTH, ground_h), (0, ground_y))


def _draw_text(surface, text, x, y, font_size=24, color=COLOR_BLACK, center=False,
               outline=False, outline_color=COLOR_BLACK):
    """Helper to draw text with optional outline."""
    font = _get_font(font_size)
    main_surf = font.render(text, True, color)
    if outline:
        out_surf = font.render(text, True, outline_color)
        offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2),
                   (0, -2), (0, 2), (-2, 0), (2, 0)]
        for ox, oy in offsets:
            if center:
                rect = out_surf.get_rect(center=(x + ox, y + oy))
            else:
                rect = out_surf.get_rect(topleft=(x + ox, y + oy))
            surface.blit(out_surf, rect)
    if center:
        rect = main_surf.get_rect(center=(x, y))
    else:
        rect = main_surf.get_rect(topleft=(x, y))
    surface.blit(main_surf, rect)


class Button:
    """Clickable button with hover effects and drop shadow."""

    def __init__(self, x, y, width, height, text, color, text_color=COLOR_BLACK, hover_color=None):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        if hover_color is None:
            self.hover_color = tuple(min(255, c + 40) for c in color)
        else:
            self.hover_color = hover_color
        self.font = _get_font(28)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.base_rect.collidepoint(mouse_pos)
        if hovered:
            scale = 1.05
            draw_rect = self.base_rect.inflate(
                int(self.base_rect.width * (scale - 1)),
                int(self.base_rect.height * (scale - 1))
            )
            current_color = self.hover_color
        else:
            draw_rect = self.base_rect
            current_color = self.color

        # Drop shadow
        shadow = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), (0, 0, draw_rect.width, draw_rect.height), border_radius=10)
        surface.blit(shadow, (draw_rect.x + 4, draw_rect.y + 4))

        pygame.draw.rect(surface, current_color, draw_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_BLACK, draw_rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.base_rect.collidepoint(event.pos)
        return False


def get_player_name(screen, clock):
    """
    Prompt the player to enter their name.
    Returns the name string.
    """
    name = ""
    active = True
    font = _get_font(36)
    small_font = _get_font(24)
    clouds = _init_clouds()

    while active:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if event.unicode.isalnum() or event.unicode in " _-":
                        if len(name) < 15:
                            name += event.unicode

        _draw_menu_background(screen, clouds, dt)
        _draw_text(screen, "Enter Your Name", SCREEN_WIDTH // 2, 200, font_size=48, center=True,
                   outline=True, outline_color=COLOR_BLACK)

        box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 280, 400, 50)
        pygame.draw.rect(screen, COLOR_WHITE, box_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BLACK, box_rect, 2, border_radius=6)

        name_surface = font.render(name + "|", True, COLOR_BLACK)
        name_rect = name_surface.get_rect(midleft=(box_rect.left + 10, box_rect.centery))
        screen.blit(name_surface, name_rect)

        instr = small_font.render("Press ENTER to confirm", True, COLOR_BLACK)
        screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH // 2, 380)))

        pygame.display.flip()

    return name.strip()


def main_menu(screen, clock):
    """Display the main menu and return the chosen action."""
    init_db()

    btn_play = Button(SCREEN_WIDTH // 2 - 100, 260, 200, 60, "Play", COLOR_GREEN)
    btn_leader = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 60, "Leaderboard", COLOR_YELLOW)
    btn_quit = Button(SCREEN_WIDTH // 2 - 100, 440, 200, 60, "Quit", COLOR_RED)

    running = True
    clouds = _init_clouds()
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_play.is_clicked(event):
                return "play"
            if btn_leader.is_clicked(event):
                return "leaderboard"
            if btn_quit.is_clicked(event):
                pygame.quit()
                sys.exit()

        _draw_menu_background(screen, clouds, dt)

        _draw_text(screen, "Physics Projectile Game", SCREEN_WIDTH // 2, 130, font_size=60,
                   color=COLOR_YELLOW, center=True, outline=True, outline_color=COLOR_BLACK)
        _draw_text(screen, "Learn projectile motion while you play!", SCREEN_WIDTH // 2, 190,
                   font_size=24, color=COLOR_WHITE, center=True, outline=True, outline_color=COLOR_BLACK)

        btn_play.draw(screen)
        btn_leader.draw(screen)
        btn_quit.draw(screen)

        pygame.display.flip()


def level_select(screen, clock, player_name):
    """
    Show level select buttons. Locked levels are grayed out.
    Returns the selected level name or None to go back.
    """
    # Determine unlocked status
    unlocked = {"EASY": True}
    for i, lvl in enumerate(LEVEL_ORDER[1:], start=1):
        prev = LEVEL_ORDER[i - 1]
        unlocked[lvl] = is_level_completed(player_name, prev)

    buttons = {}
    y_start = 240
    for i, lvl in enumerate(LEVEL_ORDER):
        color = COLOR_GREEN if unlocked[lvl] else COLOR_GRAY
        buttons[lvl] = Button(
            SCREEN_WIDTH // 2 - 120,
            y_start + i * 80,
            240,
            60,
            lvl,
            color,
            text_color=COLOR_BLACK if unlocked[lvl] else COLOR_WHITE,
        )

    btn_back = Button(SCREEN_WIDTH // 2 - 80, 560, 160, 50, "Back", COLOR_WOOD)

    running = True
    clouds = _init_clouds()
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for lvl, btn in buttons.items():
                if btn.is_clicked(event) and unlocked[lvl]:
                    return lvl
            if btn_back.is_clicked(event):
                return None

        _draw_menu_background(screen, clouds, dt)
        _draw_text(screen, "Select Level", SCREEN_WIDTH // 2, 130, font_size=52,
                   color=COLOR_WHITE, center=True, outline=True, outline_color=COLOR_BLACK)
        _draw_text(screen, f"Player: {player_name}", SCREEN_WIDTH // 2, 185, font_size=24,
                   color=COLOR_WHITE, center=True)

        for lvl, btn in buttons.items():
            btn.draw(screen)
            if not unlocked[lvl]:
                lock_text = "(Locked)"
                _draw_text(screen, lock_text, btn.base_rect.right + 15, btn.base_rect.centery,
                           font_size=20, color=COLOR_RED)

        btn_back.draw(screen)
        pygame.display.flip()


def leaderboard_screen(screen, clock, player_name):
    rows = get_player_leaderboard(player_name, level_name=None, limit=50)
    btn_back = Button(SCREEN_WIDTH // 2 - 80, 620, 160, 50, "Back", COLOR_WOOD)

    running = True
    clouds = _init_clouds()
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_back.is_clicked(event):
                return

        _draw_menu_background(screen, clouds, dt)
        _draw_text(screen, f"{player_name}'s Scores", SCREEN_WIDTH // 2, 50, font_size=52,
                   color=COLOR_WHITE, center=True, outline=True, outline_color=COLOR_BLACK)

        header_y = 100
        header_rect = pygame.Rect(100, header_y - 8, 800, 38)
        pygame.draw.rect(screen, (70, 130, 180), header_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_BLACK, header_rect, 1, border_radius=4)

        _draw_text(screen, "Rank", 140, header_y, font_size=22, color=COLOR_YELLOW)
        _draw_text(screen, "Level", 300, header_y, font_size=22, color=COLOR_YELLOW)
        _draw_text(screen, "Score", 470, header_y, font_size=22, color=COLOR_YELLOW)
        _draw_text(screen, "Attempts", 620, header_y, font_size=22, color=COLOR_YELLOW)
        _draw_text(screen, "Time (s)", 760, header_y, font_size=22, color=COLOR_YELLOW)

        if not rows:
            _draw_text(screen, "No scores yet. Play a level!", SCREEN_WIDTH // 2, 300,
                       font_size=28, color=COLOR_WHITE, center=True)
        else:
            for i, row in enumerate(rows, start=1):
                y = 150 + i * 38
                if i % 2 == 1:
                    row_rect = pygame.Rect(100, y - 6, 800, 34)
                    pygame.draw.rect(screen, (240, 248, 255), row_rect, border_radius=2)
                _draw_text(screen, str(i), 140, y, font_size=20, color=COLOR_BLACK)
                _draw_text(screen, str(row["level_name"]), 300, y, font_size=20, color=COLOR_BLACK)
                _draw_text(screen, str(row["score"]), 470, y, font_size=20, color=COLOR_BLACK)
                _draw_text(screen, str(row["attempts"]), 620, y, font_size=20, color=COLOR_BLACK)
                _draw_text(screen, f"{row['time_taken']:.1f}", 760, y, font_size=20, color=COLOR_BLACK)

        btn_back.draw(screen)
        pygame.display.flip()


def _draw_character_preview(surface, character_name, center, radius):
    """Draw a character preview at the given center and radius."""
    cx, cy = center
    c = CHARACTERS[character_name]

    if character_name == "RED":
        pygame.draw.circle(surface, c["body"], (cx, cy), radius)
        pygame.draw.circle(surface, c["outline"], (cx, cy), radius, 2)
        eye_r = int(radius * 0.25)
        pygame.draw.circle(surface, c["eyes"], (cx - int(radius * 0.3), cy - int(radius * 0.25)), eye_r)
        pygame.draw.circle(surface, c["eyes"], (cx + int(radius * 0.3), cy - int(radius * 0.25)), eye_r)
        pygame.draw.circle(surface, c["pupils"], (cx - int(radius * 0.3), cy - int(radius * 0.25)), int(radius * 0.1))
        pygame.draw.circle(surface, c["pupils"], (cx + int(radius * 0.3), cy - int(radius * 0.25)), int(radius * 0.1))
        beak_pts = [(cx + int(radius * 0.1), cy), (cx + int(radius * 0.8), cy - int(radius * 0.3)),
                    (cx + int(radius * 0.8), cy + int(radius * 0.3))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)
        pygame.draw.ellipse(surface, c["feathers"], (cx - int(radius * 0.25), cy - int(radius * 0.9), int(radius * 0.25), int(radius * 0.3)))
        pygame.draw.ellipse(surface, c["feathers"], (cx, cy - int(radius * 0.95), int(radius * 0.25), int(radius * 0.3)))

    elif character_name == "BOMB":
        pygame.draw.circle(surface, c["body"], (cx, cy), radius)
        pygame.draw.circle(surface, c["outline"], (cx, cy), radius, 2)
        eye_r = int(radius * 0.28)
        pygame.draw.circle(surface, c["eye_patch"], (cx - int(radius * 0.3), cy - int(radius * 0.1)), int(radius * 0.45))
        pygame.draw.circle(surface, c["eye_patch"], (cx + int(radius * 0.3), cy - int(radius * 0.1)), int(radius * 0.45))
        pygame.draw.circle(surface, c["eyes"], (cx - int(radius * 0.3), cy - int(radius * 0.1)), eye_r)
        pygame.draw.circle(surface, c["eyes"], (cx + int(radius * 0.3), cy - int(radius * 0.1)), eye_r)
        pygame.draw.circle(surface, c["pupils"], (cx - int(radius * 0.3), cy - int(radius * 0.1)), int(radius * 0.12))
        pygame.draw.circle(surface, c["pupils"], (cx + int(radius * 0.3), cy - int(radius * 0.1)), int(radius * 0.12))
        pygame.draw.line(surface, c["fuse"], (cx, cy - radius), (cx - int(radius * 0.2), cy - int(radius * 1.3)), 2)
        pygame.draw.circle(surface, c["spark"], (cx - int(radius * 0.2), cy - int(radius * 1.35)), int(radius * 0.15))

    elif character_name == "CHUCK":
        pts = [(cx + radius, cy), (cx - int(radius * 0.7), cy - int(radius * 0.8)),
               (cx - int(radius * 0.7), cy + int(radius * 0.8))]
        pygame.draw.polygon(surface, c["body"], pts)
        pygame.draw.polygon(surface, c["outline"], pts, 2)
        eye_r = int(radius * 0.25)
        pygame.draw.circle(surface, c["eyes"], (cx - int(radius * 0.1), cy - int(radius * 0.2)), eye_r)
        pygame.draw.circle(surface, c["eyes"], (cx + int(radius * 0.35), cy - int(radius * 0.15)), eye_r)
        pygame.draw.circle(surface, c["pupils"], (cx - int(radius * 0.1), cy - int(radius * 0.2)), int(radius * 0.1))
        pygame.draw.circle(surface, c["pupils"], (cx + int(radius * 0.35), cy - int(radius * 0.15)), int(radius * 0.1))
        beak_pts = [(cx + int(radius * 0.5), cy - int(radius * 0.1)), (cx + int(radius * 1.1), cy),
                    (cx + int(radius * 0.5), cy + int(radius * 0.2))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)
        for i in range(4):
            spike_x = cx - int(radius * 0.5) + i * int(radius * 0.25)
            spike_pts = [(spike_x, cy - int(radius * 0.8)), (spike_x - int(radius * 0.1), cy - int(radius * 1.4)),
                         (spike_x + int(radius * 0.1), cy - int(radius * 0.7))]
            pygame.draw.polygon(surface, c["hair"], spike_pts)

    elif character_name == "SILVER":
        body_pts = [(cx + int(radius * 0.9), cy), (cx + int(radius * 0.3), cy - int(radius * 0.8)),
                    (cx - int(radius * 0.8), cy - int(radius * 0.3)), (cx - int(radius * 0.9), cy + int(radius * 0.2)),
                    (cx - int(radius * 0.5), cy + int(radius * 0.8)), (cx + int(radius * 0.2), cy + int(radius * 0.8))]
        pygame.draw.polygon(surface, c["body"], body_pts)
        pygame.draw.polygon(surface, c["outline"], body_pts, 2)
        eye_r = int(radius * 0.28)
        pygame.draw.circle(surface, c["eyes"], (cx - int(radius * 0.1), cy - int(radius * 0.2)), eye_r)
        pygame.draw.circle(surface, c["eyes"], (cx + int(radius * 0.4), cy - int(radius * 0.15)), eye_r)
        pygame.draw.circle(surface, c["pupils"], (cx - int(radius * 0.1), cy - int(radius * 0.2)), int(radius * 0.12))
        pygame.draw.circle(surface, c["pupils"], (cx + int(radius * 0.4), cy - int(radius * 0.15)), int(radius * 0.12))
        beak_pts = [(cx + int(radius * 0.6), cy - int(radius * 0.05)), (cx + int(radius * 1.1), cy),
                    (cx + int(radius * 0.6), cy + int(radius * 0.15))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)

    elif character_name == "SHADE":
        pygame.draw.ellipse(surface, c["body"], (cx - int(radius * 0.8), cy - int(radius * 0.7), int(radius * 1.6), int(radius * 1.4)))
        pygame.draw.ellipse(surface, c["outline"], (cx - int(radius * 0.8), cy - int(radius * 0.7), int(radius * 1.6), int(radius * 1.4)), 2)
        eye_r = int(radius * 0.45)
        pygame.draw.circle(surface, c["eyes"], (cx - int(radius * 0.35), cy - int(radius * 0.15)), eye_r)
        pygame.draw.circle(surface, c["eyes"], (cx + int(radius * 0.35), cy - int(radius * 0.15)), eye_r)
        pygame.draw.circle(surface, c["eye_highlight"], (cx - int(radius * 0.5), cy - int(radius * 0.3)), int(radius * 0.12))
        pygame.draw.circle(surface, c["eye_highlight"], (cx + int(radius * 0.2), cy - int(radius * 0.3)), int(radius * 0.12))
        pygame.draw.ellipse(surface, c["belly"], (cx - int(radius * 0.35), cy + int(radius * 0.25), int(radius * 0.7), int(radius * 0.45)))
        for fx in [cx - int(radius * 0.4), cx + int(radius * 0.1)]:
            pts = [(fx, cy - int(radius * 0.5)), (fx - int(radius * 0.15), cy - int(radius * 1.0)),
                   (fx + int(radius * 0.15), cy - int(radius * 0.3))]
            pygame.draw.polygon(surface, c["feathers_main"], pts)


class CharacterButton:
    """Clickable button that previews a character."""

    def __init__(self, x, y, width, height, character_name, color):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.character_name = character_name
        self.color = color
        self.font = _get_font(24, bold=True)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.base_rect.collidepoint(mouse_pos)
        if hovered:
            scale = 1.05
            draw_rect = self.base_rect.inflate(
                int(self.base_rect.width * (scale - 1)),
                int(self.base_rect.height * (scale - 1))
            )
            current_color = tuple(min(255, c + 30) for c in self.color)
        else:
            draw_rect = self.base_rect
            current_color = self.color

        shadow = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), (0, 0, draw_rect.width, draw_rect.height), border_radius=12)
        surface.blit(shadow, (draw_rect.x + 4, draw_rect.y + 4))

        pygame.draw.rect(surface, current_color, draw_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BLACK, draw_rect, 2, border_radius=12)

        preview_r = 50
        preview_center = (draw_rect.centerx, draw_rect.centery - 10)
        _draw_character_preview(surface, self.character_name, preview_center, preview_r)

        name_surf = self.font.render(self.character_name, True, COLOR_BLACK)
        name_rect = name_surf.get_rect(center=(draw_rect.centerx, draw_rect.bottom - 30))
        surface.blit(name_surf, name_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.base_rect.collidepoint(event.pos)
        return False


def _wrap_text(text, font, max_width):
    """Split text into lines that fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def character_detail(screen, clock, character_name):
    """
    Show a detailed info screen for the selected character.
    Returns True if player clicks 'Proceed', False if 'Back'.
    """
    desc_font = _get_font(22)
    wrapped = _wrap_text(CHARACTER_DESCRIPTIONS[character_name], desc_font, 700)

    btn_proceed = Button(SCREEN_WIDTH // 2 + 20, 580, 220, 55, "Proceed to Game", COLOR_GREEN)
    btn_back = Button(SCREEN_WIDTH // 2 - 240, 580, 220, 55, "Back", COLOR_WOOD)

    running = True
    clouds = _init_clouds()
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_proceed.is_clicked(event):
                return True
            if btn_back.is_clicked(event):
                return False

        _draw_menu_background(screen, clouds, dt)

        _draw_text(screen, character_name, SCREEN_WIDTH // 2, 80, font_size=64,
                   color=COLOR_YELLOW, center=True, outline=True, outline_color=COLOR_BLACK)

        preview_center = (SCREEN_WIDTH // 2, 240)
        _draw_character_preview(screen, character_name, preview_center, 100)

        y_start = 380
        for i, line in enumerate(wrapped):
            _draw_text(screen, line, SCREEN_WIDTH // 2, y_start + i * 32, font_size=22,
                       color=COLOR_WHITE, center=True, outline=True, outline_color=COLOR_BLACK)

        btn_proceed.draw(screen)
        btn_back.draw(screen)
        pygame.display.flip()


def character_select(screen, clock):
    """
    Display character selection screen with 5 character options.
    Returns the selected character name string, or None to go back.
    """
    btn_w, btn_h = 160, 180
    spacing = 20
    total_w = 5 * btn_w + 4 * spacing
    start_x = (SCREEN_WIDTH - total_w) // 2
    y_pos = 220

    char_names = ["RED", "BOMB", "CHUCK", "SILVER", "SHADE"]
    wood_color = (210, 180, 140)
    buttons = {}
    for i, name in enumerate(char_names):
        x = start_x + i * (btn_w + spacing)
        buttons[name] = CharacterButton(x, y_pos, btn_w, btn_h, name, wood_color)

    btn_back = Button(SCREEN_WIDTH // 2 - 80, 450, 160, 50, "Back", COLOR_WOOD)

    running = True
    clouds = _init_clouds()
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for name, btn in buttons.items():
                if btn.is_clicked(event):
                    return name
            if btn_back.is_clicked(event):
                return None

        _draw_menu_background(screen, clouds, dt)
        _draw_text(screen, "Choose Your Character", SCREEN_WIDTH // 2, 120, font_size=52,
                   color=COLOR_WHITE, center=True, outline=True, outline_color=COLOR_BLACK)

        for btn in buttons.values():
            btn.draw(screen)

        btn_back.draw(screen)
        pygame.display.flip()
