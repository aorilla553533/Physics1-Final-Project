"""
main.py
Entry point for the Physics Projectile Game.
Initializes Pygame and runs the main menu loop.
"""

import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from menu import main_menu, level_select, get_player_name, leaderboard_screen, character_select, character_detail
from game import run_level


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Physics Projectile Game")
    clock = pygame.time.Clock()

    player_name = get_player_name(screen, clock)

    character = None
    while character is None:
        character = character_select(screen, clock)
        if not character:
            return
        proceed = character_detail(screen, clock, character)
        if not proceed:
            character = None

    while True:
        action = main_menu(screen, clock)

        if action == "play":
            level = level_select(screen, clock, player_name)
            if level:
                run_level(screen, clock, player_name, level, character)
        elif action == "leaderboard":
            leaderboard_screen(screen, clock, player_name)


if __name__ == "__main__":
    main()
