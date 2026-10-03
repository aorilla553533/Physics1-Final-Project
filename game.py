"""
game.py
Main game loop, level initialization, event handling, and physics simulation.
"""

import sys
import math
import time
import random
import pygame
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_SKY,
    COLOR_SKY_TOP,
    COLOR_SKY_BOTTOM,
    COLOR_GROUND_TOP,
    COLOR_GROUND_BOTTOM,
    COLOR_GROUND,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_TRAJECTORY,
    COLOR_CLOUD,
    COLOR_LAUNCH_BURST,
    COLOR_HIT_BURST,
    COLOR_DUST,
    COLOR_CONFETTI,
    COLOR_WIND_ARROW,
    SLINGSHOT_POS,
    LEVELS,
    LEVEL_ORDER,
    DT,
)
from entities import Player, Target, Obstacle, Slingshot
from utils import (
    calculate_launch_velocity,
    simulate_trajectory,
    circle_rect_collision,
    compute_score,
)
from database import save_score, is_level_completed
from effects import ParticleSystem, FloatingText


def _get_font(size, bold=False):
    """Load a playful font with system fallback."""
    for name in ["comicsansms", "segoeui", "georgia", "arial"]:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            font.render(" ", True, (0, 0, 0))
            return font
        except Exception:
            continue
    return pygame.font.SysFont("arial", size, bold=bold)


def _create_sky_gradient(height):
    surf = pygame.Surface((SCREEN_WIDTH, height))
    for y in range(height):
        ratio = y / height
        r = int(200 * (1 - ratio) + 150 * ratio)
        g = int(230 * (1 - ratio) + 210 * ratio)
        b = int(245 * (1 - ratio) + 235 * ratio)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    return surf


def _draw_cloud_bands(surface, ground_y):
    band_color = (255, 255, 255)
    y_bases = [ground_y - 280, ground_y - 220, ground_y - 170]
    for y_base in y_bases:
        bar_rect = pygame.Rect(-50, y_base, SCREEN_WIDTH + 100, 45)
        pygame.draw.rect(surface, band_color, bar_rect)
        x = -50
        while x < SCREEN_WIDTH + 100:
            w = random.randint(180, 320)
            h = random.randint(30, 50)
            pygame.draw.ellipse(surface, band_color, (x, y_base - 5, w, h + 10))
            pygame.draw.ellipse(surface, band_color, (x + w * 0.3, y_base - h * 0.3, w * 0.6, h * 0.8))
            pygame.draw.ellipse(surface, band_color, (x + w * 0.6, y_base - h * 0.1, w * 0.5, h * 0.6))
            x += w * 0.7


def _draw_mountains(surface, ground_y):
    mist_color = (190, 210, 220)
    far_pts = [(0, ground_y - 80), (200, ground_y - 160), (450, ground_y - 120),
               (700, ground_y - 180), (950, ground_y - 100),
               (SCREEN_WIDTH, ground_y - 140), (SCREEN_WIDTH, ground_y), (0, ground_y)]
    pygame.draw.polygon(surface, mist_color, far_pts)


def _draw_platform(surface, x, y, width, height):
    dark_earth = (45, 30, 15)
    earth_top = (65, 45, 25)
    grass_color = (80, 150, 50)
    plat_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, dark_earth, plat_rect)
    pygame.draw.rect(surface, earth_top, (x, y, width, 8))
    for gx in range(x, x + width, 6):
        gh = 5 + ((gx // 3) % 5)
        pts = [(gx, y), (gx + 3, y - gh), (gx + 6, y)]
        pygame.draw.polygon(surface, grass_color, pts)
    pygame.draw.rect(surface, COLOR_BLACK, plat_rect, 1)
    for i in range(3):
        spike_x = x + 20 + i * (width // 4)
        spike_pts = [(spike_x, y + height), (spike_x + 8, y + height + 12), (spike_x + 16, y + height)]
        pygame.draw.polygon(surface, dark_earth, spike_pts)


def _draw_waiting_birds(surface, start_x, ground_y):
    bird_colors = [(220, 20, 60), (255, 200, 50), (220, 20, 60), (255, 200, 50)]
    for i, color in enumerate(bird_colors):
        bx = start_x + i * 28
        by = ground_y - 12
        br = 10
        pygame.draw.circle(surface, color, (bx, by), br)
        pygame.draw.circle(surface, COLOR_BLACK, (bx, by), br, 1)
        pygame.draw.circle(surface, COLOR_WHITE, (bx - 3, by - 3), 4)
        pygame.draw.circle(surface, COLOR_WHITE, (bx + 3, by - 3), 4)
        pygame.draw.circle(surface, COLOR_BLACK, (bx - 3, by - 3), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (bx + 3, by - 3), 2)
        beak = [(bx + 6, by), (bx + 14, by - 3), (bx + 14, by + 3)]
        pygame.draw.polygon(surface, (255, 165, 0), beak)


class Cloud:
    """Simple drifting cloud made of ellipses."""

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
        # Main body
        pygame.draw.ellipse(surface, COLOR_CLOUD, (int(self.x), int(self.y), self.w, self.h))
        # Extra puffs
        pygame.draw.ellipse(surface, COLOR_CLOUD,
                            (int(self.x + self.w * 0.25), int(self.y - self.h * 0.25),
                             int(self.w * 0.6), int(self.h * 0.7)))
        pygame.draw.ellipse(surface, COLOR_CLOUD,
                            (int(self.x + self.w * 0.55), int(self.y - self.h * 0.1),
                             int(self.w * 0.5), int(self.h * 0.6)))


def _draw_text_outlined(surface, text, font, color, outline_color, pos, center=True):
    """Draw text with a thick dark outline."""
    outline = font.render(text, True, outline_color)
    main = font.render(text, True, color)
    offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2),
               (0, -2), (0, 2), (-2, 0), (2, 0)]
    for ox, oy in offsets:
        if center:
            rect = outline.get_rect(center=(pos[0] + ox, pos[1] + oy))
        else:
            rect = outline.get_rect(topleft=(pos[0] + ox, pos[1] + oy))
        surface.blit(outline, rect)
    if center:
        rect = main.get_rect(center=pos)
    else:
        rect = main.get_rect(topleft=pos)
    surface.blit(main, rect)


def _draw_wind_indicator(surface, wind, x, y):
    """Draw a small arrow showing wind direction and strength."""
    if abs(wind) < 1:
        return
    direction = 1 if wind > 0 else -1
    arrow_len = min(60, abs(wind))
    end_x = x + direction * arrow_len
    pygame.draw.line(surface, COLOR_WIND_ARROW, (x, y), (end_x, y), 3)
    # Arrowhead
    pygame.draw.polygon(surface, COLOR_WIND_ARROW, [
        (end_x, y),
        (end_x - direction * 8, y - 5),
        (end_x - direction * 8, y + 5),
    ])
    font = _get_font(16)
    text = font.render(f"{abs(wind):.0f}", True, COLOR_WHITE)
    text_x = x + direction * (arrow_len + 14)
    surface.blit(text, (text_x - text.get_width() // 2, y - 8))


def run_level(screen, clock, player_name, level_name, character_type="RED"):
    """
    Run a single level.

    Parameters:
        screen (pygame.Surface): Main display surface.
        clock (pygame.time.Clock): Frame rate clock.
        player_name (str): Current player's name.
        level_name (str): EASY, MEDIUM, or DIFFICULT.
        character_type (str): Selected character name (RED, BOMB, CHUCK, SILVER, SHADE).

    Returns:
        dict: Result with keys 'success' (bool), 'score' (int), 'next_level' (str|None).
    """
    config = LEVELS[level_name]
    ground_y = config["ground_y"]

    # -----------------------------------------------------------------------
    # Level Entities
    # -----------------------------------------------------------------------
    slingshot = Slingshot(SLINGSHOT_POS)
    player = Player(SLINGSHOT_POS[0], SLINGSHOT_POS[1], character_type)

    target = Target(
        config["target_pos"][0],
        config["target_pos"][1],
        config["target_radius"],
        speed=config["target_speed"],
        move_range=50 if config["target_speed"] > 0 else 0,
        ground_y=ground_y,
    )

    obstacles = []
    for obs_data in config["obstacles"]:
        obstacles.append(Obstacle(obs_data["rect"], obs_data.get("color", COLOR_GROUND)))

    # -----------------------------------------------------------------------
    # Game State
    # -----------------------------------------------------------------------
    max_attempts = config["max_attempts"]
    attempts_used = 0
    shots_left = max_attempts
    wind = config["wind"]
    max_velocity = config["max_velocity"]

    state = "aiming"  # aiming | flying | landed | won | lost
    result = {"success": False, "score": 0, "next_level": None}

    start_time = time.time()
    font = _get_font(24)
    big_font = _get_font(48, bold=True)

    # Visual assets
    sky_surf = _create_sky_gradient(ground_y)

    clouds = [
        Cloud(100, 80, 130, 45, 12),
        Cloud(350, 140, 170, 55, 8),
        Cloud(650, 70, 150, 50, 15),
        Cloud(880, 180, 110, 40, 10),
    ]

    particles = ParticleSystem()

    overlay_alpha = 0
    win_confetti_spawned = False
    was_on_ground = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # actual delta time in seconds
        prev_state = state

        # -------------------------------------------------------------------
        # Event Handling
        # -------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state == "aiming":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    slingshot.start_drag(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    slingshot.update_drag(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if slingshot.dragging:
                        drag_vector = slingshot.end_drag()
                        vx, vy = calculate_launch_velocity(drag_vector, max_velocity)
                        if math.hypot(vx, vy) > 10.0:
                            player.launch(vx, vy)
                            attempts_used += 1
                            shots_left -= 1
                            state = "flying"
                        else:
                            # Cancel weak pull
                            slingshot.stretch_pos = SLINGSHOT_POS

            elif state in ("won", "lost"):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Retry same level
                        return run_level(screen, clock, player_name, level_name)
                    elif event.key == pygame.K_m:
                        running = False
                    elif event.key == pygame.K_n and result["next_level"]:
                        return run_level(screen, clock, player_name, result["next_level"])

        # -------------------------------------------------------------------
        # Update Physics
        # -------------------------------------------------------------------
        target.update(DT)

        if state == "flying":
            player.update(wind=wind, ground_y=ground_y)

            # Check obstacle collisions
            for obs in obstacles:
                if circle_rect_collision(player.get_center(), player.radius, obs.rect):
                    # Simple response: stop the projectile
                    player.active = False
                    state = "landed"
                    break

            if player.active:
                hit_something = target.check_collision(player)
                if hit_something:
                    player.active = False
                    player.on_ground = True
                    if target.all_pigs_dead():
                        state = "won"
                        blocks_destroyed = sum(1 for b in target.blocks if not b.active)
                        pigs_killed = sum(1 for p in target.pigs if not p.active)
                        base_score = 1000
                        block_bonus = blocks_destroyed * 50
                        pig_bonus = pigs_killed * 200
                        attempt_penalty = attempts_used * 100
                        result["score"] = max(0, base_score + block_bonus + pig_bonus - attempt_penalty)
                        result["success"] = True
                        time_taken = time.time() - start_time
                        save_score(
                            player_name, level_name, attempts_used,
                            True, result["score"], time_taken,
                        )
                        idx = LEVEL_ORDER.index(level_name)
                        if idx + 1 < len(LEVEL_ORDER):
                            result["next_level"] = LEVEL_ORDER[idx + 1]
                    else:
                        state = "landed"

            if (player.x > SCREEN_WIDTH + 100 or player.x < -100 or
                    player.y < -500):
                player.active = False
                state = "landed"

            if not player.active and state != "won":
                state = "landed"

        elif state == "landed":
            if shots_left <= 0:
                state = "lost"
                time_taken = time.time() - start_time
                save_score(
                    player_name, level_name, attempts_used,
                    False, 0, time_taken,
                )
            else:
                pygame.time.wait(300)
                player.reset(SLINGSHOT_POS[0], SLINGSHOT_POS[1])
                was_on_ground = False
                state = "aiming"

        if target.all_pigs_dead() and state not in ("won", "lost"):
            state = "won"
            blocks_destroyed = sum(1 for b in target.blocks if not b.active)
            pigs_killed = sum(1 for p in target.pigs if not p.active)
            base_score = 1000
            block_bonus = blocks_destroyed * 50
            pig_bonus = pigs_killed * 200
            attempt_penalty = attempts_used * 100
            result["score"] = max(0, base_score + block_bonus + pig_bonus - attempt_penalty)
            result["success"] = True
            time_taken = time.time() - start_time
            save_score(
                player_name, level_name, attempts_used,
                True, result["score"], time_taken,
            )
            idx = LEVEL_ORDER.index(level_name)
            if idx + 1 < len(LEVEL_ORDER):
                result["next_level"] = LEVEL_ORDER[idx + 1]

        # -------------------------------------------------------------------
        # Visual Effects Updates
        # -------------------------------------------------------------------
        for cloud in clouds:
            cloud.update(dt)

        particles.update_all(dt)

        # Trigger effects on state transitions
        if state == "flying" and prev_state == "aiming":
            particles.add_burst(
                slingshot.stretch_pos[0], slingshot.stretch_pos[1],
                count=15, color=COLOR_LAUNCH_BURST,
                min_speed=50, max_speed=250,
                min_life=0.3, max_life=0.7,
                min_size=2, max_size=5,
                gravity=400
            )

        if state == "won" and prev_state != "won":
            target.hit_flash = 0.5
            particles.add_burst(
                target.x, target.y,
                count=25, color=COLOR_HIT_BURST,
                min_speed=40, max_speed=180,
                min_life=0.5, max_life=1.2,
                min_size=3, max_size=6,
                gravity=120
            )
            particles.add_text(FloatingText(
                target.x, target.y - 30,
                f"+{result['score']}",
                COLOR_YELLOW, _get_font(28, bold=True),
                life=1.5, vy=-55
            ))
            if not win_confetti_spawned:
                for _ in range(60):
                    particles.add_burst(
                        random.randint(0, SCREEN_WIDTH), -10,
                        count=1, color=random.choice(COLOR_CONFETTI),
                        min_speed=80, max_speed=250,
                        min_life=2.0, max_life=4.0,
                        min_size=4, max_size=8,
                        gravity=180
                    )
                win_confetti_spawned = True

        # Ground hit dust
        if player.on_ground and not was_on_ground:
            particles.add_burst(
                player.x, ground_y,
                count=12, color=COLOR_DUST,
                min_speed=20, max_speed=90,
                min_life=0.4, max_life=0.9,
                min_size=3, max_size=6,
                gravity=60
            )
        was_on_ground = player.on_ground

        if state in ("won", "lost"):
            overlay_alpha = min(180, overlay_alpha + 5)

        # -------------------------------------------------------------------
        # Drawing
        # -------------------------------------------------------------------
        screen.blit(sky_surf, (0, 0))
        for cloud in clouds:
            cloud.draw(screen)

        left_plat_x = 0
        left_plat_w = 220
        right_plat_x = 580
        right_plat_w = SCREEN_WIDTH - right_plat_x
        plat_height = SCREEN_HEIGHT - ground_y + 60

        _draw_platform(screen, left_plat_x, ground_y - 20, left_plat_w, plat_height)
        _draw_platform(screen, right_plat_x, ground_y - 20, right_plat_w, plat_height)
        _draw_waiting_birds(screen, SLINGSHOT_POS[0] - 70, ground_y - 20)

        for obs in obstacles:
            obs.draw(screen)

        target.draw(screen)

        # Slingshot
        if state == "aiming":
            if slingshot.dragging:
                slingshot.draw(screen, player_pos=slingshot.stretch_pos)
                temp_player = Player(slingshot.stretch_pos[0], slingshot.stretch_pos[1], character_type)
                temp_player.draw(screen)

                # Trajectory preview (fading dotted line)
                drag_vector = (
                    slingshot.drag_current[0] - slingshot.pos[0],
                    slingshot.drag_current[1] - slingshot.pos[1],
                )
                preview_vx, preview_vy = calculate_launch_velocity(drag_vector, max_velocity)
                preview_points = simulate_trajectory(
                    slingshot.stretch_pos,
                    (preview_vx, preview_vy),
                    steps=20,
                    step_dt=0.08,
                    wind=wind,
                    obstacles=[obs.rect for obs in obstacles],
                    ground_y=ground_y,
                )
                for i, pt in enumerate(preview_points):
                    ratio = i / max(1, len(preview_points) - 1)
                    alpha = int(255 * (1 - ratio * 0.7))
                    dot_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(dot_surf, (*COLOR_TRAJECTORY, alpha), (3, 3), 3)
                    screen.blit(dot_surf, (int(pt[0]) - 3, int(pt[1]) - 3))
            else:
                slingshot.draw(screen, player_pos=SLINGSHOT_POS)
                player.draw_shadow(screen, ground_y)
                player.draw(screen)
        else:
            slingshot.draw(screen, player_pos=SLINGSHOT_POS)
            player.draw_shadow(screen, ground_y)
            player.draw(screen)

        # Particles
        particles.draw_all(screen)

        # HUD
        hud_panel = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        hud_panel.fill((0, 0, 0, 120))
        screen.blit(hud_panel, (0, 0))

        hud_text = f"Level: {level_name}  |  Shots Left: {shots_left}  |  Wind: {wind:.1f} px/s²"
        hud_surface = font.render(hud_text, True, COLOR_WHITE)
        screen.blit(hud_surface, (15, 12))

        score_text = f"Score: {result['score']}"
        score_surface = font.render(score_text, True, COLOR_YELLOW)
        screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 20, 12))

        _draw_wind_indicator(screen, wind, 850, 18)

        if state == "flying":
            speed = math.hypot(player.vx, player.vy)
            angle = math.degrees(math.atan2(-player.vy, player.vx))
            info = f"v={speed:.1f} px/s  angle={angle:.1f}°"
            info_surface = font.render(info, True, COLOR_WHITE)
            screen.blit(info_surface, (15, 42))

        # Win / Lose overlays
        if state == "won":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(overlay_alpha)
            overlay.fill(COLOR_BLACK)
            screen.blit(overlay, (0, 0))

            _draw_text_outlined(screen, "LEVEL COMPLETE!", big_font, COLOR_YELLOW, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            _draw_text_outlined(screen, f"Score: {result['score']}", font, COLOR_WHITE, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 5))
            next_str = (f"Next Level: {result['next_level'] or 'None'} (Press N)"
                        if result["next_level"]
                        else "All levels complete! (Press M for menu)")
            _draw_text_outlined(screen, next_str, font, COLOR_WHITE, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            _draw_text_outlined(screen, "Retry: R  |  Menu: M", font, COLOR_WHITE, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

        elif state == "lost":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(overlay_alpha)
            overlay.fill(COLOR_BLACK)
            screen.blit(overlay, (0, 0))

            _draw_text_outlined(screen, "GAME OVER", big_font, COLOR_ORANGE, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            _draw_text_outlined(screen, "Retry: R  |  Menu: M", font, COLOR_WHITE, COLOR_BLACK,
                                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()

    return result
