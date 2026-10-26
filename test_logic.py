# -*- coding: utf-8 -*-
"""
Тесты игровой логики «ПАТОГЕН» (запуск без графического окна).

Проверяются ключевые требования ТЗ:
  1. Игра стартует по клику на регион.
  2. Заражённые регионы растут каждую игровую секунду.
  3. Прокачанные пути передачи перекидывают вирус на соседей.
  4. Очки ДНК капают автоматически.
  5. Лекарство стартует через 30 секунд, скорость зависит от тяжести.
  6. Победа — вымирание человечества; поражение — лекарство 100%.

Запуск:  python test_logic.py
"""

import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import headless  # noqa: F401,E402  (устанавливает заглушки Pygame)
from plague_simulator import Game, UPGRADES  # noqa: E402


def total_pop(g):
    return sum(r.total_pop for r in g.regions)


# ===== ТЕСТ 1: старт игры по клику =====================================
g = Game()
assert not g.started, "Игра не должна идти до клика"
g.handle_click(g.regions[5].rect.center)
assert g.started, "Клик по региону должен запустить игру"
assert any(r.infected == 1 for r in g.regions), "Должен появиться нулевой пациент"
print("[1] Старт по клику ....................... OK")

# ===== ТЕСТ 2: рост заражённых и капля ДНК =============================
dna0 = g.virus.dna_points
inf0 = sum(r.infected for r in g.regions)
for _ in range(20):
    g.tick()
inf1 = sum(r.infected for r in g.regions)
assert inf1 > inf0, "Число больных должно расти каждую секунду"
assert g.virus.dna_points > dna0, "Очки ДНК должны капать автоматически"
print(f"[2] Рост заразы {inf0}->{inf1}, ДНК {dna0}->{g.virus.dna_points} ... OK")

# ===== ТЕСТ 3: лекарство начинается ровно через 30 секунд ==============
g2 = Game()
g2.handle_click(g2.regions[30].rect.center)
for _ in range(29):
    g2.tick()
assert not g2.cure_started and g2.cure_progress == 0, "До 30 с лекарство не идёт"
g2.tick()  # 30-я секунда
assert g2.cure_started, "На 30-й секунде WHO начинает разработку"
assert g2.cure_progress > 0, "Прогресс лекарства должен расти"
print("[3] Лекарство стартует на 30-й секунде ... OK")

# ===== ТЕСТ 4: тяжесть симптомов ускоряет лекарство ====================
def cure_after(severity_buy_count, ticks=120):
    g3 = Game()
    g3.handle_click(g3.regions[30].rect.center)
    for i in range(severity_buy_count):
        g3.virus.buy("symptoms", i)
    for _ in range(ticks):
        g3.tick()
    return g3.cure_progress

slow = cure_after(0)
fast = cure_after(5)
assert fast > slow, "Прокачка симптомов должна ускорять разработку лекарства"
print(f"[4] Тяжесть ускоряет лекарство: {slow:.1f}% -> {fast:.1f}% ... OK")

# ===== ТЕСТ 5: прокачанные пути передачи заражают соседей ===============
random.seed(11)
g4 = Game()
g4.handle_click(g4.regions[30].rect.center)
home = g4.regions[30]
for i in range(len(UPGRADES["transmission"])):
    g4.virus.buy("transmission", i)
g4.virus.dna_points = 10**9  # чтобы точно хватало на всё
spread_ok = False
for _ in range(600):
    g4.tick()
    if any(g4.regions[n].infected_bool for n in home.neighbors):
        spread_ok = True
        break
assert spread_ok, "Вирус обязан перекидываться на соседние регионы"
nations = sum(1 for r in g4.regions if r.infected_bool)
assert nations > 1
print(f"[5] Передача работает: пандемия в {nations} регионах ... OK")

# ===== ТЕСТ 6а: угасание вируса при живых здоровых = поражение ===========
random.seed(3)
g5 = Game()
g5.handle_click(g5.regions[0].rect.center)   # крошечная Аляска
# Хак: «лекарство» уже запущено, но прогресс принудительно держим на нуле,
# чтобы игра завершилась по правилу «вирус угас», а не по лекарству.
g5.cure_started = True
for _ in range(1000):
    g5.cure_progress = 0.0
    g5.tick()
    if g5.game_over:
        break
assert g5.game_over and not g5.win, \
    "Очаг вымер, здоровые регионы целы, носителей нет -> вирус угас -> поражение"
print(f"[6a] Вирус угас локально: win={g5.win} ({g5.end_reason}) ... OK")

# ===== ТЕСТ 6б: пассивный вирус проигрывает лекарству ====================
random.seed(5)
g7 = Game()
g7.handle_click(g7.regions[0].rect.center)   # Аляска, без прокачки
for _ in range(20000):
    g7.tick()
    if g7.game_over:
        break
assert g7.game_over, "Пассивный вирус должен доиграть до финала"
assert not g7.win, f"Ожидали поражение от лекарства, получили: {g7.end_reason}"
assert g7.cure_progress >= 100
print(f"[6b] Пассивный вирус проиграл лекарству за ~{int(g7.elapsed)} с ... OK")

# ===== ТЕСТ 7: стратегическая игра достижима до победы ==================
g6, used = headless.simulate(3600, seed=42)
assert g6.game_over, "Умная стратегия должна довести игру до конца"
assert g6.win, f"Ожидали победу вируса, получили: {g6.end_reason}"
dead_share = sum(r.dead for r in g6.regions) / total_pop(g6)
assert dead_share > 0.99, "Победа = почти 100% умерших"
print(f"[7] Победа за {used} игровых секунд, смертность {dead_share*100:.1f}% ... OK")

print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ")
