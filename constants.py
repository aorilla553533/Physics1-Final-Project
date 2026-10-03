"""
constants.py
Contains screen settings, colors, physics constants, scaling factors,
and level configurations for the physics game.
"""

import pygame

# ---------------------------------------------------------------------------
# Screen Settings
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# ---------------------------------------------------------------------------
# Colors (RGB)
# ---------------------------------------------------------------------------
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 20, 60)
COLOR_DARK_RED = (139, 0, 0)
COLOR_GREEN = (34, 139, 34)
COLOR_BLUE = (30, 144, 255)
COLOR_SKY = (135, 206, 235)
COLOR_GROUND = (139, 69, 19)
COLOR_WOOD = (160, 82, 45)
COLOR_YELLOW = (255, 215, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_ORANGE = (255, 165, 0)

# New visual colors for gradients, particles, and UI polish
COLOR_SKY_TOP = (100, 180, 255)
COLOR_SKY_BOTTOM = (135, 206, 235)
COLOR_GROUND_TOP = (160, 120, 80)
COLOR_GROUND_BOTTOM = (100, 60, 30)
COLOR_CLOUD = (255, 255, 255)
COLOR_TRAJECTORY = (255, 255, 255)  # white
COLOR_BRICK_LIGHT = (190, 110, 70)
COLOR_BRICK_DARK = (130, 65, 35)
COLOR_DUST = (194, 178, 128)
COLOR_LAUNCH_BURST = (255, 200, 50)
COLOR_HIT_BURST = (50, 255, 150)
COLOR_CONFETTI = [
    (255, 50, 50),
    (50, 150, 255),
    (255, 215, 0),
    (50, 255, 100),
    (255, 100, 200),
    (100, 50, 255),
]
COLOR_WIND_ARROW = (220, 220, 220)
COLOR_GLOW = (255, 255, 100)

# ---------------------------------------------------------------------------
# Physics Constants
# ---------------------------------------------------------------------------
# Gravity g = 9.8 m/s^2 (real-world value).
# We scale it to pixels per second^2 for the simulation.
GRAVITY_MPS2 = 9.8
PIXELS_PER_METER = 50.0
# Scaled gravity for the game loop: g (px/s^2) = 9.8 * 50 = 490 px/s^2
GRAVITY_PXPS2 = GRAVITY_MPS2 * PIXELS_PER_METER

# Time step per frame (seconds). At 60 FPS, dt ≈ 1/60 s.
DT = 1.0 / FPS

# Maximum drag distance from slingshot (pixels)
MAX_DRAG_DISTANCE = 120

# Launch power scaling factor: pixels dragged -> launch velocity (px/s)
# v = drag_distance * POWER_SCALE
POWER_SCALE = 12.0

# ---------------------------------------------------------------------------
# Entity Defaults
# ---------------------------------------------------------------------------
SLINGSHOT_POS = (150, 500)
PLAYER_RADIUS = 20
PLAYER_MASS = 1.0  # kg (for future extension)

# ---------------------------------------------------------------------------
# Level Configurations
# ---------------------------------------------------------------------------
LEVELS = {
    "EASY": {
        "target_pos": (800, 430),
        "target_radius": 40,
        "target_speed": 0.0,
        "obstacles": [],
        "wind": 0.0,
        "max_velocity": None,
        "max_attempts": 5,
        "ground_y": 550,
    },
    "MEDIUM": {
        "target_pos": (800, 468),
        "target_radius": 25,
        "target_speed": 0.0,
        "obstacles": [
            {"rect": pygame.Rect(500, 350, 40, 200), "color": COLOR_WOOD},
        ],
        "wind": 0.0,
        "max_velocity": None,
        "max_attempts": 5,
        "ground_y": 550,
    },
    "DIFFICULT": {
        "target_pos": (800, 493),
        "target_radius": 15,
        "target_speed": 80.0,
        "obstacles": [
            {"rect": pygame.Rect(400, 420, 40, 130), "color": COLOR_WOOD},
            {"rect": pygame.Rect(600, 300, 40, 250), "color": COLOR_WOOD},
        ],
        "wind": 60.0,
        "max_velocity": 900.0,
        "max_attempts": 7,
        "ground_y": 550,
    },
}

# ---------------------------------------------------------------------------
# Character Definitions
# ---------------------------------------------------------------------------
# Each character has a color palette for pygame.draw primitives
CHARACTERS = {
    "RED": {
        "body": (220, 20, 60),
        "outline": (139, 0, 0),
        "eyes": (255, 255, 255),
        "pupils": (0, 0, 0),
        "eyebrows": (0, 0, 0),
        "beak": (255, 215, 0),
        "belly": (255, 220, 177),
        "feathers": (220, 20, 60),
    },
    "BOMB": {
        "body": (20, 20, 20),
        "outline": (50, 50, 50),
        "eyes": (255, 255, 255),
        "eye_patch": (80, 80, 80),
        "pupils": (0, 0, 0),
        "eyebrows": (180, 80, 0),
        "beak": (255, 165, 0),
        "belly": (60, 60, 60),
        "fuse": (50, 30, 0),
        "spark": (255, 255, 100),
    },
    "CHUCK": {
        "body": (255, 200, 50),
        "outline": (230, 160, 30),
        "eyes": (255, 255, 255),
        "pupils": (0, 0, 0),
        "eyebrows": (139, 69, 19),
        "beak": (255, 140, 0),
        "hair": (0, 0, 0),
        "belly": (255, 240, 180),
    },
    "SILVER": {
        "body": (192, 192, 192),
        "outline": (130, 130, 140),
        "eyes": (255, 255, 255),
        "pupils": (0, 0, 0),
        "beak": (255, 140, 0),
        "beak_detail": (200, 50, 50),
        "belly": (220, 220, 230),
        "crest": (160, 160, 170),
    },
    "SHADE": {
        "body": (240, 240, 250),
        "outline": (200, 200, 210),
        "eyes": (139, 69, 19),
        "eye_highlight": (255, 255, 255),
        "eyelashes": (0, 0, 0),
        "beak": (255, 140, 0),
        "beak_dark": (200, 80, 0),
        "belly": (255, 255, 255),
        "feathers_main": (101, 67, 33),
        "feathers_stripe": (255, 255, 255),
        "tufts": (0, 0, 0),
    },
}

CHARACTER_DESCRIPTIONS = {
    "RED": (
        "The classic projectile pioneer! Red is a born leader who knows that "
        "the perfect launch angle and velocity are the keys to victory. "
        "His no-nonsense attitude keeps the flock focused on hitting the target."
    ),
    "BOMB": (
        "Packed with potential energy! Bomb may look calm, but his explosive "
        "mass gives him serious momentum. His fuse is always lit and ready "
        "to convert chemical energy into kinetic motion."
    ),
    "CHUCK": (
        "The speedster of velocity! Chuck lives for high-speed trajectories. "
        "His triangular shape slices through the air with minimal drag, "
        "making him the fastest bird in the flock."
    ),
    "SILVER": (
        "The aerodynamics expert! Silver's sleek design lets her glide "
        "gracefully through the air. She learned from the pigs that "
        "a streamlined body reduces air resistance for maximum range."
    ),
    "SHADE": (
        "The gravity-defying ghost! Shade seems to float and fall with "
        "an eerie elegance. She understands that gravity is just another "
        "force to be mastered on the path to the target."
    ),
}

# Level unlock order
LEVEL_ORDER = ["EASY", "MEDIUM", "DIFFICULT"]
