# -*- coding: utf-8 -*-
"""
Головагентный прогон симуляции «ПАТОГЕН» без графического окна.

Модуль plague_simulator не импортируется в средах без дисплея (SDL_INIT_VIDEO),
поэтому перед импортом подменяются видеомодули Pygame и заглушится инициализация.

Запуск:  python headless.py [число_секунд_симуляции]
"""

import os
import random
import sys
import types

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


class _DummySurface:
    def __init__(self, size=(0, 0), flags=0, *a, **kw):
        self.rect = pygame.Rect(0, 0, max(size[0], 1), max(size[1], 1))

    def convert(self, *a, **kw): return self
    def convert_alpha(self, *a, **kw): return self
    def fill(self, *a, **kw): pass
    def blit(self, *a, **kw): return self.rect
    def set_alpha(self, *a, **kw): pass
    def set_colorkey(self, *a, **kw): pass
    def get_width(self): return self.rect.width
    def get_height(self): return self.rect.height
    def get_size(self): return (self.rect.width, self.rect.height)
    def lock(self, *a, **kw): pass
    def unlock(self, *a, **kw): pass


def _install_stubs():
    fake_display = types.ModuleType("pygame.display")
    fake_display.init = lambda: None
    fake_display.quit = lambda: None
    fake_display.get_init = lambda: True
    fake_display.set_mode = lambda *a, **kw: _DummySurface()
    fake_display.set_caption = lambda *a, **kw: None
    fake_display.flip = lambda: None
    fake_display.update = lambda *a, **kw: None
    fake_display.get_surface = lambda: _DummySurface()
    fake_display.get_driver = lambda: "dummy"
    fake_display.Icon = _DummySurface
    fake_display.set_icon = lambda *a, **kw: None
    pygame.display = fake_display
    sys.modules["pygame.display"] = fake_display

    fake_draw = types.ModuleType("pygame.draw")
    fake_draw.rect = lambda *a, **kw: pygame.Rect(0, 0, 0, 0)
    fake_draw.circle = lambda *a, **kw: pygame.Rect(0, 0, 0, 0)
    fake_draw.line = lambda *a, **kw: pygame.Rect(0, 0, 0, 0)
    fake_draw.lines = lambda *a, **kw: pygame.Rect(0, 0, 0, 0)
    fake_draw.polygon = lambda *a, **kw: pygame.Rect(0, 0, 0, 0)
    fake_draw.arc = lambda *a, **kw: pygame.Rect(0, 0, 0, 0)
    pygame.draw = fake_draw
    sys.modules["pygame.draw"] = fake_draw

    pygame.font.SysFont = lambda name, size, bold=False, italic=False: \
        pygame.font.Font(None, size)


_install_stubs()

from plague_simulator import Game, UPGRADES  # noqa: E402


def world_stats(g):
    healthy = sum(r.healthy for r in g.regions)
    infected = sum(r.infected for r in g.regions)
    dead = sum(r.dead for r in g.regions)
    total = healthy + infected + dead
    countries = sum(1 for r in g.regions if r.infected_bool and r.infected > 0)
    return healthy, infected, dead, total, countries


def simulate(seconds=3600, seed=None, strategy="smart"):
    """Прогон игровой логики на `seconds` игровых секунд. Возвращает игру."""
    if seed is not None:
        random.seed(seed)
    g = Game()
    # Нулевой пациент — густонаселённый регион (Китай, индекс 30)
    g.handle_click(g.regions[30].rect.center)

    for t in range(int(seconds)):
        g.tick()
        v = g.virus
        if strategy == "smart":
            # Приоритет: устойчивость -> передача -> симптомы только в конце
            for i in range(len(UPGRADES["resistance"])):
                if v.can_buy("resistance", i):
                    v.buy("resistance", i)
            for i in range(len(UPGRADES["transmission"])):
                if v.can_buy("transmission", i):
                    v.buy("transmission", i)
            inf_c = sum(1 for r in g.regions if r.infected_bool)
            healthy_left = sum(r.healthy for r in g.regions)
            world_pop = sum(r.total_pop for r in g.regions)
            if inf_c >= len(g.regions) - 4 or healthy_left < world_pop * 0.15:
                for i in range(len(UPGRADES["symptoms"])):
                    if v.can_buy("symptoms", i):
                        v.buy("symptoms", i)
        if g.game_over:
            break
    return g, t + 1


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    g, used = simulate(limit, seed=42)
    h, i, d, tot, c = world_stats(g)
    print(f"Игровых секунд пройдено: {used}")
    print(f"Здоровые:   {h:>12,.0f}".replace(",", " "))
    print(f"Заражённые: {i:>12,.0f}".replace(",", " "))
    print(f"Умершие:    {d:>12,.0f}".replace(",", " "))
    print(f"Всего:      {tot:>12,.0f}".replace(",", " "))
    print(f"Стран в пандемии: {c}/{len(g.regions)}")
    print(f"Лекарство: {g.cure_progress:.1f}%")
    print(f"ДНК: {g.virus.dna_points}")
    print(f"Игра окончена: {g.game_over}, победа вируса: {g.win}")
    if g.end_reason:
        print(f"Причина: {g.end_reason}")
