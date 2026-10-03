"""
entities.py
Defines game entity classes:
  - Player (red circle with a smiley face)
  - Target (circle target)
  - Obstacle (rectangle wall/platform)
  - Slingshot (drawn with lines)
"""

import math
import pygame
from constants import (
    COLOR_RED,
    COLOR_DARK_RED,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_WOOD,
    COLOR_BRICK_LIGHT,
    COLOR_BRICK_DARK,
    PLAYER_RADIUS,
    GRAVITY_PXPS2,
    DT,
    CHARACTERS,
)


class Player:
    """
    The projectile character: a selectable bird-like character.
    Physics state includes position and velocity.
    """

    def __init__(self, x, y, character_type="RED"):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = PLAYER_RADIUS
        self.active = False
        self.on_ground = False
        self.character_type = character_type

    def launch(self, vx, vy):
        """Set initial velocity and mark as active."""
        self.vx = vx
        self.vy = vy
        self.active = True
        self.on_ground = False

    def update(self, wind=0.0, ground_y=700):
        """
        Update physics state for one frame.

        Physics (projectile motion, discrete integration):
          - x = x0 + vx * dt
          - y = y0 + vy * dt
          - vy = vy + g * dt   (gravity accelerates downward in screen coords)
          - vx = vx + wind * dt
        """
        if not self.active:
            return

        # x = x0 + vx * dt
        self.x += self.vx * DT
        # y = y0 + vy * dt
        self.y += self.vy * DT
        # vy = vy + g * dt
        self.vy += GRAVITY_PXPS2 * DT
        # Apply wind acceleration to horizontal velocity
        self.vx += wind * DT

        # Ground collision
        if self.y + self.radius >= ground_y:
            self.y = ground_y - self.radius
            self.active = False
            self.on_ground = True

    def draw_shadow(self, surface, ground_y):
        """Draw a subtle shadow beneath the player when in the air."""
        if self.on_ground or not self.active:
            return
        height_above = ground_y - (self.y + self.radius)
        if height_above <= 0:
            return
        max_height = 300.0
        ratio = max(0.0, min(1.0, 1.0 - height_above / max_height))
        shadow_w = int(self.radius * (1.5 - 0.5 * ratio))
        shadow_h = int(self.radius * 0.4 * (1.0 - ratio * 0.5))
        alpha = int(80 * ratio)
        temp = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(temp, (0, 0, 0, alpha), (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(temp, (int(self.x - shadow_w), int(ground_y - shadow_h)))

    def draw(self, surface):
        """Draw the character based on selected type."""
        if self.character_type == "RED":
            self._draw_red(surface)
        elif self.character_type == "BOMB":
            self._draw_bomb(surface)
        elif self.character_type == "CHUCK":
            self._draw_chuck(surface)
        elif self.character_type == "SILVER":
            self._draw_silver(surface)
        elif self.character_type == "SHADE":
            self._draw_shade(surface)
        else:
            self._draw_red(surface)

    def _draw_red(self, surface):
        """RED: Classic round bird with angry eyebrows and yellow beak."""
        c = CHARACTERS["RED"]
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        pygame.draw.circle(surface, c["body"], (cx, cy), r)
        pygame.draw.circle(surface, c["outline"], (cx, cy), r, 2)

        eye_off_x, eye_off_y = int(r * 0.3), int(r * -0.25)
        eye_r = int(r * 0.25)
        pupil_r = int(r * 0.1)

        left_eye = (cx - eye_off_x, cy + eye_off_y)
        right_eye = (cx + eye_off_x, cy + eye_off_y)

        pygame.draw.circle(surface, c["eyes"], left_eye, eye_r)
        pygame.draw.circle(surface, c["eyes"], right_eye, eye_r)
        pygame.draw.circle(surface, c["pupils"], left_eye, pupil_r)
        pygame.draw.circle(surface, c["pupils"], right_eye, pupil_r)

        brow_y = cy + eye_off_y - int(r * 0.4)
        brow_len = int(r * 0.25)
        pygame.draw.line(surface, c["eyebrows"], (left_eye[0] - brow_len, brow_y),
                         (left_eye[0] + brow_len, brow_y - int(r * 0.1)), 2)
        pygame.draw.line(surface, c["eyebrows"], (right_eye[0] - brow_len, brow_y - int(r * 0.1)),
                         (right_eye[0] + brow_len, brow_y), 2)

        beak_pts = [(cx + int(r * 0.1), cy), (cx + int(r * 0.8), cy - int(r * 0.3)),
                    (cx + int(r * 0.8), cy + int(r * 0.3))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)

        belly_r = int(r * 0.5)
        belly_rect = pygame.Rect(cx - belly_r, cy + int(r * 0.1), belly_r * 2, belly_r)
        pygame.draw.arc(surface, c["belly"], belly_rect, 0, math.pi, int(r * 0.2))

        pygame.draw.ellipse(surface, c["feathers"], (cx - int(r * 0.25), cy - int(r * 0.9), int(r * 0.25), int(r * 0.3)))
        pygame.draw.ellipse(surface, c["feathers"], (cx + int(r * 0.0), cy - int(r * 0.95), int(r * 0.25), int(r * 0.3)))

    def _draw_bomb(self, surface):
        """BOMB: Black round bird with grey eye patches and a fuse."""
        c = CHARACTERS["BOMB"]
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        pygame.draw.circle(surface, c["body"], (cx, cy), r)
        pygame.draw.circle(surface, c["outline"], (cx, cy), r, 2)

        eye_patch_r = int(r * 0.45)
        pygame.draw.circle(surface, c["eye_patch"], (cx - int(r * 0.3), cy - int(r * 0.1)), eye_patch_r)
        pygame.draw.circle(surface, c["eye_patch"], (cx + int(r * 0.3), cy - int(r * 0.1)), eye_patch_r)

        eye_r = int(r * 0.28)
        pupil_r = int(r * 0.12)
        left_eye = (cx - int(r * 0.3), cy - int(r * 0.1))
        right_eye = (cx + int(r * 0.3), cy - int(r * 0.1))

        pygame.draw.circle(surface, c["eyes"], left_eye, eye_r)
        pygame.draw.circle(surface, c["eyes"], right_eye, eye_r)
        pygame.draw.circle(surface, c["pupils"], left_eye, pupil_r)
        pygame.draw.circle(surface, c["pupils"], right_eye, pupil_r)

        brow_y = cy - int(r * 0.5)
        brow_len = int(r * 0.35)
        pygame.draw.line(surface, c["eyebrows"], (left_eye[0] - brow_len, brow_y),
                         (left_eye[0] + brow_len, brow_y), 3)
        pygame.draw.line(surface, c["eyebrows"], (right_eye[0] - brow_len, brow_y),
                         (right_eye[0] + brow_len, brow_y), 3)

        beak_pts = [(cx + int(r * 0.1), cy), (cx + int(r * 0.7), cy - int(r * 0.15)),
                    (cx + int(r * 0.7), cy + int(r * 0.25))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)

        belly_r = int(r * 0.45)
        belly_rect = pygame.Rect(cx - belly_r, cy + int(r * 0.15), belly_r * 2, belly_r)
        pygame.draw.arc(surface, c["belly"], belly_rect, 0, math.pi, int(r * 0.15))

        pygame.draw.line(surface, c["fuse"], (cx, cy - r), (cx - int(r * 0.2), cy - int(r * 1.3)), 2)
        pygame.draw.circle(surface, c["spark"], (cx - int(r * 0.2), cy - int(r * 1.35)), int(r * 0.15))

    def _draw_chuck(self, surface):
        """CHUCK: Yellow triangle bird with spiky hair."""
        c = CHARACTERS["CHUCK"]
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        pts = [
            (cx + r, cy),
            (cx - int(r * 0.7), cy - int(r * 0.8)),
            (cx - int(r * 0.7), cy + int(r * 0.8)),
        ]
        pygame.draw.polygon(surface, c["body"], pts)
        pygame.draw.polygon(surface, c["outline"], pts, 2)

        hair_pts = [
            (cx - int(r * 0.5), cy - int(r * 0.8)),
            (cx - int(r * 0.9), cy - int(r * 1.4)),
            (cx - int(r * 0.3), cy - int(r * 0.9)),
            (cx - int(r * 0.7), cy - int(r * 1.5)),
            (cx - int(r * 0.1), cy - int(r * 0.85)),
            (cx - int(r * 0.6), cy - int(r * 1.6)),
            (cx + int(r * 0.1), cy - int(r * 0.75)),
        ]
        for i in range(0, len(hair_pts) - 1, 2):
            if i + 1 < len(hair_pts):
                pygame.draw.polygon(surface, c["hair"], [hair_pts[i], hair_pts[i + 1], (cx - int(r * 0.5), cy - int(r * 0.7))])

        eye_r = int(r * 0.25)
        pupil_r = int(r * 0.1)
        left_eye = (cx - int(r * 0.1), cy - int(r * 0.2))
        right_eye = (cx + int(r * 0.35), cy - int(r * 0.15))

        pygame.draw.circle(surface, c["eyes"], left_eye, eye_r)
        pygame.draw.circle(surface, c["eyes"], right_eye, eye_r)
        pygame.draw.circle(surface, c["pupils"], left_eye, pupil_r)
        pygame.draw.circle(surface, c["pupils"], right_eye, pupil_r)

        brow_y = cy - int(r * 0.5)
        pygame.draw.line(surface, c["eyebrows"], (left_eye[0] - int(r * 0.2), brow_y),
                         (left_eye[0] + int(r * 0.2), brow_y - int(r * 0.15)), 3)
        pygame.draw.line(surface, c["eyebrows"], (right_eye[0] - int(r * 0.2), brow_y - int(r * 0.1)),
                         (right_eye[0] + int(r * 0.2), brow_y - int(r * 0.25)), 3)

        beak_pts = [(cx + int(r * 0.5), cy - int(r * 0.1)), (cx + int(r * 1.1), cy),
                    (cx + int(r * 0.5), cy + int(r * 0.2))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)

        belly_pts = [(cx - int(r * 0.5), cy + int(r * 0.3)), (cx + int(r * 0.3), cy + int(r * 0.5)),
                     (cx - int(r * 0.5), cy + int(r * 0.7))]
        pygame.draw.polygon(surface, c["belly"], belly_pts)

    def _draw_silver(self, surface):
        """SILVER: Grey teardrop bird with a crest and orange beak."""
        c = CHARACTERS["SILVER"]
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        body_pts = [
            (cx + int(r * 0.9), cy),
            (cx + int(r * 0.3), cy - int(r * 0.8)),
            (cx - int(r * 0.8), cy - int(r * 0.3)),
            (cx - int(r * 0.9), cy + int(r * 0.2)),
            (cx - int(r * 0.5), cy + int(r * 0.8)),
            (cx + int(r * 0.2), cy + int(r * 0.8)),
        ]
        pygame.draw.polygon(surface, c["body"], body_pts)
        pygame.draw.polygon(surface, c["outline"], body_pts, 2)

        crest_pts = [
            (cx + int(r * 0.1), cy - int(r * 0.8)),
            (cx - int(r * 0.3), cy - int(r * 1.3)),
            (cx - int(r * 0.5), cy - int(r * 0.7)),
        ]
        pygame.draw.polygon(surface, c["crest"], crest_pts)

        eye_r = int(r * 0.28)
        pupil_r = int(r * 0.12)
        left_eye = (cx - int(r * 0.1), cy - int(r * 0.2))
        right_eye = (cx + int(r * 0.4), cy - int(r * 0.15))

        pygame.draw.circle(surface, c["eyes"], left_eye, eye_r)
        pygame.draw.circle(surface, c["eyes"], right_eye, eye_r)
        pygame.draw.circle(surface, c["pupils"], left_eye, pupil_r)
        pygame.draw.circle(surface, c["pupils"], right_eye, pupil_r)

        beak_pts = [(cx + int(r * 0.6), cy - int(r * 0.05)), (cx + int(r * 1.1), cy),
                    (cx + int(r * 0.6), cy + int(r * 0.15))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)
        pygame.draw.line(surface, c["beak_detail"], (cx + int(r * 0.7), cy + int(r * 0.02)),
                         (cx + int(r * 0.95), cy + int(r * 0.02)), 2)

        tail_pts = [(cx - int(r * 0.9), cy + int(r * 0.2)), (cx - int(r * 1.4), cy - int(r * 0.1)),
                    (cx - int(r * 1.3), cy + int(r * 0.3))]
        pygame.draw.polygon(surface, c["outline"], tail_pts)

    def _draw_shade(self, surface):
        """SHADE: White owl-like bird with large brown eyes and feather tufts."""
        c = CHARACTERS["SHADE"]
        cx, cy = int(self.x), int(self.y)
        r = self.radius

        pygame.draw.ellipse(surface, c["body"], (cx - int(r * 0.8), cy - int(r * 0.7), int(r * 1.6), int(r * 1.4)))
        pygame.draw.ellipse(surface, c["outline"], (cx - int(r * 0.8), cy - int(r * 0.7), int(r * 1.6), int(r * 1.4)), 2)

        feather_y = cy - int(r * 0.9)
        for i, fx in enumerate([cx - int(r * 0.4), cx + int(r * 0.1)]):
            pts = [(fx, feather_y + int(r * 0.4)), (fx - int(r * 0.15), feather_y - int(r * 0.5)),
                   (fx + int(r * 0.15), feather_y + int(r * 0.3))]
            pygame.draw.polygon(surface, c["feathers_main"], pts)
            pygame.draw.line(surface, c["feathers_stripe"], (fx - int(r * 0.05), feather_y),
                             (fx, feather_y - int(r * 0.35)), 2)

        eye_r = int(r * 0.45)
        left_eye = (cx - int(r * 0.35), cy - int(r * 0.15))
        right_eye = (cx + int(r * 0.35), cy - int(r * 0.15))

        pygame.draw.circle(surface, c["eyes"], left_eye, eye_r)
        pygame.draw.circle(surface, c["eyes"], right_eye, eye_r)
        pygame.draw.circle(surface, c["eye_highlight"], (left_eye[0] - int(r * 0.15), left_eye[1] - int(r * 0.15)), int(r * 0.12))
        pygame.draw.circle(surface, c["eye_highlight"], (right_eye[0] - int(r * 0.15), right_eye[1] - int(r * 0.15)), int(r * 0.12))

        for ex, ey in [left_eye, right_eye]:
            pygame.draw.line(surface, c["eyelashes"], (ex - int(r * 0.35), ey - int(r * 0.4)),
                             (ex - int(r * 0.55), ey - int(r * 0.55)), 2)
            pygame.draw.line(surface, c["eyelashes"], (ex - int(r * 0.15), ey - int(r * 0.45)),
                             (ex - int(r * 0.25), ey - int(r * 0.65)), 2)
            pygame.draw.line(surface, c["eyelashes"], (ex + int(r * 0.15), ey - int(r * 0.45)),
                             (ex + int(r * 0.25), ey - int(r * 0.65)), 2)
            pygame.draw.line(surface, c["eyelashes"], (ex + int(r * 0.35), ey - int(r * 0.4)),
                             (ex + int(r * 0.55), ey - int(r * 0.55)), 2)

        beak_pts = [(cx - int(r * 0.1), cy + int(r * 0.25)), (cx + int(r * 0.1), cy + int(r * 0.25)),
                    (cx, cy + int(r * 0.45))]
        pygame.draw.polygon(surface, c["beak"], beak_pts)
        pygame.draw.line(surface, c["beak_dark"], (cx - int(r * 0.08), cy + int(r * 0.32)),
                         (cx + int(r * 0.08), cy + int(r * 0.32)), 2)

        pygame.draw.ellipse(surface, c["belly"], (cx - int(r * 0.35), cy + int(r * 0.25), int(r * 0.7), int(r * 0.45)))

        for tx in [cx - int(r * 0.85), cx + int(r * 0.75)]:
            tuft_pts = [(tx, cy), (tx + (int(r * 0.3) if tx > cx else -int(r * 0.3)), cy - int(r * 0.3)),
                        (tx + (int(r * 0.2) if tx > cx else -int(r * 0.2)), cy + int(r * 0.15))]
            pygame.draw.polygon(surface, c["tufts"], tuft_pts)

    def get_center(self):
        return (self.x, self.y)

    def reset(self, x, y):
        """Return player to slingshot rest position."""
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.active = False
        self.on_ground = False


class Block:
    def __init__(self, x, y, w, h, block_type='wood'):
        self.rect = pygame.Rect(x, y, w, h)
        self.block_type = block_type
        self.health = {'wood': 1, 'ice': 1, 'stone': 2}[block_type]
        self.max_health = self.health
        self.active = True
        self.vx = 0.0
        self.vy = 0.0
        self.damaged = False
        self.damage_timer = 0.0

    def hit(self, damage=1):
        if not self.active:
            return
        self.health -= damage
        self.damaged = True
        self.damage_timer = 0.15
        if self.health <= 0:
            self.active = False

    def update(self, dt, all_blocks, ground_y):
        if not self.active:
            return
        if self.damaged and self.damage_timer > 0:
            self.damage_timer -= dt
            if self.damage_timer <= 0:
                self.damaged = False

        gravity = 500.0
        support = False
        margin = 2
        if self.rect.bottom >= ground_y - margin:
            support = True
            self.rect.bottom = ground_y
            self.vy = 0
            self.vx *= 0.9
        else:
            for other in all_blocks:
                if other is self or not other.active:
                    continue
                if (self.rect.bottom >= other.rect.top - margin and
                    self.rect.bottom <= other.rect.top + margin + 5 and
                    self.rect.centerx > other.rect.left and
                    self.rect.centerx < other.rect.right):
                    support = True
                    self.rect.bottom = other.rect.top
                    self.vy = 0
                    self.vx *= 0.9
                    break

        if not support:
            self.vy += gravity * dt
            self.rect.y += self.vy * dt
            self.rect.x += self.vx * dt

        if self.rect.y > ground_y + 200:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        colors = {
            'wood': ((180, 120, 60), (210, 150, 80), (140, 90, 40)),
            'ice': ((173, 216, 230), (220, 240, 255), (120, 180, 210)),
            'stone': ((150, 150, 150), (180, 180, 180), (110, 110, 110)),
        }
        c, light, dark = colors[self.block_type]
        pygame.draw.rect(surface, c, self.rect)
        pygame.draw.rect(surface, light, (self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, 3))
        pygame.draw.rect(surface, dark, (self.rect.x + 2, self.rect.bottom - 5, self.rect.width - 4, 3))
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, 1)

        if self.block_type == 'wood':
            for ox in range(self.rect.x + 4, self.rect.right - 2, 10):
                pygame.draw.line(surface, dark, (ox, self.rect.y + 2), (ox, self.rect.bottom - 2), 1)
        elif self.block_type == 'ice':
            for ox in range(self.rect.x + 6, self.rect.right - 4, 12):
                pygame.draw.line(surface, light, (ox, self.rect.y + 4), (ox, self.rect.bottom - 4), 2)
        elif self.block_type == 'stone':
            pygame.draw.rect(surface, dark, (self.rect.x + 6, self.rect.y + 6, self.rect.width - 12, self.rect.height - 12), 1)

        if self.damaged:
            flash = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 120))
            surface.blit(flash, self.rect.topleft)


class Pig:
    def __init__(self, x, y, radius):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.active = True
        self.vx = 0.0
        self.vy = 0.0
        self.damaged = False
        self.damage_timer = 0.0

    def hit(self):
        self.active = False

    def update(self, dt, all_blocks, ground_y):
        if not self.active:
            return
        gravity = 500.0
        support = False
        margin = 2
        bottom_y = self.y + self.radius

        if bottom_y >= ground_y - margin:
            support = True
            self.y = ground_y - self.radius
            self.vy = 0
            self.vx *= 0.9
        else:
            for block in all_blocks:
                if not block.active:
                    continue
                if (bottom_y >= block.rect.top - margin and
                    bottom_y <= block.rect.top + margin + 5 and
                    self.x > block.rect.left and
                    self.x < block.rect.right):
                    support = True
                    self.y = block.rect.top - self.radius
                    self.vy = 0
                    self.vx *= 0.9
                    break

        if not support:
            self.vy += gravity * dt
            self.y += self.vy * dt
            self.x += self.vx * dt

        if self.y > ground_y + 200:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        px, py, pr = int(self.x), int(self.y), self.radius
        body_color = (120, 200, 80)
        outline_color = (80, 160, 50)
        snout_color = (160, 240, 140)
        nostril_color = (60, 120, 40)
        pygame.draw.circle(surface, body_color, (px, py), pr)
        pygame.draw.circle(surface, outline_color, (px, py), pr, 2)
        eye_r = max(3, pr // 3)
        pygame.draw.circle(surface, COLOR_WHITE, (px - pr // 3, py - pr // 4), eye_r)
        pygame.draw.circle(surface, COLOR_WHITE, (px + pr // 3, py - pr // 4), eye_r)
        pygame.draw.circle(surface, COLOR_BLACK, (px - pr // 3, py - pr // 4), max(2, eye_r // 2))
        pygame.draw.circle(surface, COLOR_BLACK, (px + pr // 3, py - pr // 4), max(2, eye_r // 2))
        snout_w = pr
        snout_h = pr // 2
        snout_rect = pygame.Rect(px - snout_w // 2, py - snout_h // 2, snout_w, snout_h)
        pygame.draw.ellipse(surface, snout_color, snout_rect)
        pygame.draw.ellipse(surface, outline_color, snout_rect, 1)
        nostril_r = max(2, snout_h // 4)
        pygame.draw.circle(surface, nostril_color, (px - snout_w // 4, py), nostril_r)
        pygame.draw.circle(surface, nostril_color, (px + snout_w // 4, py), nostril_r)
        ear_r = max(3, pr // 3)
        pygame.draw.circle(surface, body_color, (px - pr // 2, py - pr + ear_r // 2), ear_r)
        pygame.draw.circle(surface, outline_color, (px - pr // 2, py - pr + ear_r // 2), ear_r, 1)
        pygame.draw.circle(surface, body_color, (px + pr // 2, py - pr + ear_r // 2), ear_r)
        pygame.draw.circle(surface, outline_color, (px + pr // 2, py - pr + ear_r // 2), ear_r, 1)


class Target:
    def __init__(self, x, y, radius, speed=0.0, move_range=100, ground_y=550):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.speed = speed
        self.move_range = move_range
        self.origin_x = float(x)
        self.direction = 1
        self.ground_y = ground_y
        self.blocks = []
        self.pigs = []
        self._build_structure()

    def _build_structure(self):
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)
        w = int(r * 3.0)
        h = int(r * 3.0)
        base_x = cx - w // 2
        base_y = cy - h // 2

        bw = max(14, w // 4)
        bh = max(14, h // 5)
        pillar_h = h - bh * 2

        self.blocks.append(Block(base_x, base_y + h - bh, w, bh, 'wood'))

        self.blocks.append(Block(base_x, base_y + bh, bw, pillar_h, 'wood'))
        self.blocks.append(Block(base_x + w - bw, base_y + bh, bw, pillar_h, 'wood'))

        self.blocks.append(Block(base_x, base_y, w, bh, 'wood'))

        pig_x = cx
        pig_y = base_y + h - bh - pillar_h // 2
        pig_r = max(12, r // 2)
        self.pigs.append(Pig(pig_x, pig_y, pig_r))

    def update(self, dt):
        if self.speed != 0.0:
            dx = self.speed * self.direction * dt
            self.x += dx
            if self.x > self.origin_x + self.move_range:
                self.x = self.origin_x + self.move_range
                self.direction = -1
            elif self.x < self.origin_x - self.move_range:
                self.x = self.origin_x - self.move_range
                self.direction = 1
            for block in self.blocks:
                if block.active:
                    block.rect.x += dx
            for pig in self.pigs:
                if pig.active:
                    pig.x += dx

        for block in self.blocks:
            block.update(dt, self.blocks, self.ground_y)
        for pig in self.pigs:
            pig.update(dt, self.blocks, self.ground_y)

    def draw(self, surface):
        for block in self.blocks:
            block.draw(surface)
        for pig in self.pigs:
            pig.draw(surface)

    def all_pigs_dead(self):
        return all(not pig.active for pig in self.pigs)

    def check_collision(self, player):
        hit = False
        for block in self.blocks:
            if block.active and block.rect.colliderect(
                pygame.Rect(player.x - player.radius, player.y - player.radius,
                           player.radius * 2, player.radius * 2)):
                block.hit(1)
                hit = True
        for pig in self.pigs:
            if pig.active:
                dx = player.x - pig.x
                dy = player.y - pig.y
                dist_sq = dx * dx + dy * dy
                if dist_sq <= (player.radius + pig.radius) ** 2:
                    pig.hit()
                    hit = True
        return hit

    def get_center(self):
        return (self.x, self.y)

    def get_rect(self):
        r = int(self.radius)
        w = int(r * 2.5)
        h = int(r * 5.0)
        return pygame.Rect(
            self.x - w // 2,
            self.y - h // 2,
            w,
            h,
        )


class Obstacle:
    """A rectangular wall or platform with a brick pattern."""

    def __init__(self, rect, color=COLOR_WOOD):
        self.rect = rect
        self.color = color

    def draw(self, surface):
        # Drop shadow
        shadow_offset = 5
        shadow_surf = pygame.Surface(
            (self.rect.width + shadow_offset, self.rect.height + shadow_offset),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            shadow_surf, (0, 0, 0, 60),
            (shadow_offset, shadow_offset, self.rect.width, self.rect.height),
            border_radius=2
        )
        surface.blit(shadow_surf, (self.rect.x, self.rect.y))

        # Base dark brick
        pygame.draw.rect(surface, COLOR_BRICK_DARK, self.rect)
        # Brick pattern
        brick_w = 20
        brick_h = 10
        for row in range(self.rect.top, self.rect.bottom, brick_h):
            offset = (row // brick_h % 2) * (brick_w // 2)
            for col in range(self.rect.left + offset, self.rect.right, brick_w):
                brick = pygame.Rect(col, row, brick_w - 1, brick_h - 1)
                clipped = brick.clip(self.rect)
                if clipped.width > 0 and clipped.height > 0:
                    pygame.draw.rect(surface, COLOR_BRICK_LIGHT, clipped)
        # Border
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, 2)


class Slingshot:
    """
    Draws the slingshot structure at a fixed position.
    Also tracks drag state for pulling back.
    """

    def __init__(self, pos):
        self.pos = pos  # (x, y) base position
        self.dragging = False
        self.drag_current = pos
        self.stretch_pos = pos  # Position of the projectile while dragged

    def start_drag(self, mouse_pos):
        """Begin dragging if mouse is near the slingshot."""
        dx = mouse_pos[0] - self.pos[0]
        dy = mouse_pos[1] - self.pos[1]
        if math.hypot(dx, dy) < 60:
            self.dragging = True
            self.drag_current = mouse_pos
            # Initialize stretch position immediately
            self.stretch_pos = (self.pos[0] - dx, self.pos[1] - dy)
            return True
        return False

    def update_drag(self, mouse_pos):
        if self.dragging:
            self.drag_current = mouse_pos
            # The stretch position is opposite to drag direction from base
            # This is where the player sphere sits while pulling
            dx = mouse_pos[0] - self.pos[0]
            dy = mouse_pos[1] - self.pos[1]
            self.stretch_pos = (self.pos[0] - dx, self.pos[1] - dy)

    def end_drag(self):
        """Return the drag vector (from slingshot to mouse) and reset state."""
        self.dragging = False
        dx = self.drag_current[0] - self.pos[0]
        dy = self.drag_current[1] - self.pos[1]
        return (dx, dy)

    def draw(self, surface, player_pos=None):
        """
        Draw the slingshot frame and elastic bands.
        If player_pos is provided, the bands connect to the player sphere.
        """
        base_x, base_y = self.pos
        # Fork dimensions
        fork_height = 60
        fork_width = 30

        # Left and right fork tips
        left_tip = (base_x - fork_width // 2, base_y - fork_height)
        right_tip = (base_x + fork_width // 2, base_y - fork_height)

        # Wood tones for gradient-like effect
        wood_dark = (120, 60, 30)
        wood_mid = (160, 90, 45)
        wood_light = (190, 120, 60)

        # Draw fork with layered lines for depth
        lines = [
            (wood_dark, -2, 8),
            (wood_mid, 0, 6),
            (wood_light, 1, 4),
        ]
        for color, offset, thickness in lines:
            pygame.draw.line(surface, color, (base_x + offset, base_y), (left_tip[0] + offset, left_tip[1]), thickness)
            pygame.draw.line(surface, color, (base_x + offset, base_y), (right_tip[0] + offset, right_tip[1]), thickness)
            pygame.draw.line(surface, color, (left_tip[0] + offset, left_tip[1]), (right_tip[0] + offset, right_tip[1]), max(1, thickness - 2))

        # Draw elastic bands
        band_attach = player_pos if player_pos is not None else self.pos
        # Tension-based color: white -> red
        if player_pos is not None:
            dx = band_attach[0] - self.pos[0]
            dy = band_attach[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            tension = min(1.0, dist / 80.0)
            r = int(255)
            g = int(255 * (1.0 - tension))
            b = int(255 * (1.0 - tension))
            band_color = (r, g, b)
        else:
            band_color = COLOR_WHITE

        pygame.draw.line(surface, band_color, left_tip, band_attach, 3)
        pygame.draw.line(surface, band_color, right_tip, band_attach, 3)
