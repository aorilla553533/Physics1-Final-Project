"""
database.py
SQLite wrapper for the physics game.
Handles player data, level results, leaderboards, and progress tracking.
"""

import sqlite3
import os
from datetime import datetime

DB_FILE = "physics_game.db"


def _get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they do not exist. Called automatically on first run."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date_played TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS level_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            level_name TEXT NOT NULL,
            attempts INTEGER NOT NULL,
            success INTEGER NOT NULL,
            score INTEGER NOT NULL,
            time_taken REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_score(player_name, level_name, attempts, success, score, time_taken):
    """
    Persist a level result and ensure the player exists in the players table.

    Parameters:
        player_name (str): Name of the player.
        level_name (str): EASY, MEDIUM, or DIFFICULT.
        attempts (int): Number of attempts used.
        success (bool): True if the target was hit.
        score (int): Final score for the level.
        time_taken (float): Time in seconds to complete (or fail) the level.
    """
    conn = _get_connection()
    cursor = conn.cursor()

    # Upsert player record with latest play date
    cursor.execute("""
        SELECT id FROM players WHERE name = ?
    """, (player_name,))
    row = cursor.fetchone()
    now = datetime.now().isoformat()
    if row is None:
        cursor.execute("""
            INSERT INTO players (name, date_played) VALUES (?, ?)
        """, (player_name, now))
    else:
        cursor.execute("""
            UPDATE players SET date_played = ? WHERE name = ?
        """, (now, player_name))

    cursor.execute("""
        INSERT INTO level_results
        (player_name, level_name, attempts, success, score, time_taken)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (player_name, level_name, attempts, int(success), score, time_taken))

    conn.commit()
    conn.close()


def get_leaderboard(level_name=None, limit=10):
    conn = _get_connection()
    cursor = conn.cursor()

    if level_name:
        cursor.execute("""
            SELECT player_name, level_name, score, attempts, time_taken, date_played
            FROM level_results
            JOIN players ON level_results.player_name = players.name
            WHERE level_name = ?
            ORDER BY score DESC
            LIMIT ?
        """, (level_name, limit))
    else:
        cursor.execute("""
            SELECT player_name, level_name, score, attempts, time_taken, date_played
            FROM level_results
            JOIN players ON level_results.player_name = players.name
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_player_leaderboard(player_name, level_name=None, limit=50):
    conn = _get_connection()
    cursor = conn.cursor()

    if level_name:
        cursor.execute("""
            SELECT level_name, score, attempts, time_taken, date_played
            FROM level_results
            JOIN players ON level_results.player_name = players.name
            WHERE level_results.player_name = ? AND level_name = ?
            ORDER BY score DESC
            LIMIT ?
        """, (player_name, level_name, limit))
    else:
        cursor.execute("""
            SELECT level_name, score, attempts, time_taken, date_played
            FROM level_results
            JOIN players ON level_results.player_name = players.name
            WHERE level_results.player_name = ?
            ORDER BY score DESC
            LIMIT ?
        """, (player_name, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows


def is_level_completed(player_name, level_name):
    """
    Check whether a player has any successful attempt for a level.

    Returns:
        bool: True if at least one successful result exists.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM level_results
        WHERE player_name = ? AND level_name = ? AND success = 1
        LIMIT 1
    """, (player_name, level_name))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def get_player_progress(player_name):
    """
    Return a dict mapping level_name -> best score for that player.

    Returns:
        dict[str, int]: Best score per level (0 if no record).
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT level_name, MAX(score) as best_score
        FROM level_results
        WHERE player_name = ? AND success = 1
        GROUP BY level_name
    """, (player_name,))
    rows = cursor.fetchall()
    conn.close()
    progress = {"EASY": 0, "MEDIUM": 0, "DIFFICULT": 0}
    for row in rows:
        progress[row["level_name"]] = row["best_score"]
    return progress
