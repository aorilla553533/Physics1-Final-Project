"""
effects.py
Particle system and visual effects for the physics game.
"""

import math
import random
import pygame


class Particle:
    """A single particle with position, velocity, lifetime, and fade-out."""

    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.life = float(life)
        self.max_life = float(life)
        self.color = color
        self.size = int(size)
        self.gravity = float(gravity)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        # Use a temporary SRCALPHA surface for per-dot alpha
        temp = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(temp, c, (self.size, self.size), self.size)
        surface.blit(temp, (int(self.x - self.size), int(self.y - self.size)))


class FloatingText:
    """Text that floats upward and fades out."""

    def __init__(self, x, y, text, color, font, life=1.5, vy=-40):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.font = font
        self.life = float(life)
        self.max_life = float(life)
        self.vy = float(vy)

    def update(self, dt):
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        text_surf = self.font.render(self.text, True, self.color)
        # Apply overall alpha via a temporary SRCALPHA surface
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(text_surf, (0, 0))
        alpha_surf.set_alpha(alpha)
        rect = alpha_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(alpha_surf, rect)


class ParticleSystem:
    """Manages collections of particles and floating texts."""

    def __init__(self):
        self.particles = []
        self.texts = []

    def add_burst(self, x, y, count, color, min_speed, max_speed, min_life, max_life,
                  min_size, max_size, gravity=0.0, spread=math.pi * 2):
        """Spawn a burst of particles radiating from (x, y)."""
        for _ in range(count):
            angle = random.uniform(0, spread)
            speed = random.uniform(min_speed, max_speed)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(min_life, max_life)
            size = random.uniform(min_size, max_size)
            self.particles.append(Particle(x, y, vx, vy, life, color, size, gravity))

    def add_text(self, floating_text):
        """Add a floating text effect."""
        self.texts.append(floating_text)

    def update_all(self, dt):
        """Update all particles and texts, removing dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]
        self.texts = [t for t in self.texts if t.update(dt)]

    def draw_all(self, surface):
        """Render all particles and texts."""
        for p in self.particles:
            p.draw(surface)
        for t in self.texts:
            t.draw(surface)

    def clear(self):
        """Remove all effects."""
        self.particles.clear()
        self.texts.clear()
