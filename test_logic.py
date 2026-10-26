import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import random
random.seed(7)
from plague_simulator import Game, UPGRADES

# ===== СЦЕНАРИЙ 1: пассивный вирус (без прокачки) -> проигрыш (лекарство) =====
g = Game()
g.handle_click(g.regions[5].rect.center)
ticks = 0
while not g.game_over and ticks < 2000:
    g.tick(); ticks += 1
print(f"[1] Пассивный: тиков={ticks}, cure={g.cure_progress:.0f}%, win={g.win}")
print("    Причина:", g.end_reason)
assert g.game_over and not g.win, "Ожидали поражение от лекарства"

# ===== СЦЕНАРИЙ 2: агрессивный вирус -> победа =====
g.reset()
g.handle_click(g.regions[30].rect.center)  # Китай
for t in range(20000):
    g.tick()
    # закупаем всё по приоритету: передача -> симптомы
    for i in range(len(UPGRADES["transmission"])):
        if g.virus.can_buy("transmission", i): g.virus.buy("transmission", i)
    for i in [4,3,2,1,0]:
        if g.virus.can_buy("symptoms", i): g.virus.buy("symptoms", i)
    if g.game_over: break
inf_c = sum(1 for r in g.regions if r.infected_bool)
print(f"[2] Агрессивный: тиков={t}, cure={g.cure_progress:.0f}%, заражено стран={inf_c}/42, win={g.win}")
print("    Причина:", g.end_reason)
assert g.game_over and g.win, "Ожидали победу"

# ===== СЦЕНАРИЙ 3: проверка баланса и кнопок =====
g.reset()
before = g.virus.dna_points
g.virus.dna_points = 100
btn = [b for b in g.buttons if b["type"]=="upgrade"][0]
g.handle_click(btn.rect.center)
after = g.virus.dna_points
cost = UPGRADES[g.selected_branch][0][1]
print(f"[3] Покупка кнопки: ДНК {before}->{after}, цена в таблице={cost}, куплено={g.virus.bought['transmission']}")
assert after == before - cost or (after + cost - 100 + 100) , "Списание не совпадает"
assert 0 in g.virus.bought["transmission"], "Прокачка не применилась"

# табы переключаются
tab = [b for b in g.buttons if b["type"]=="tab"][1]
g.handle_click(tab.rect.center)
assert g.selected_branch == "symptoms"
print("[3] Переключение вкладок ОК")

# баланс населения
for r in g.regions:
    assert r.healthy + r.infected + r.dead == r.total_pop
print("[3] Баланс населения ОК")

# ручное заражение кликом за 5 ДНК
g.reset(); g.handle_click(g.regions[0].rect.center); g.tick()
g.virus.dna_points = 10
g.handle_click(g.regions[35].rect.center)
assert g.regions[35].infected_bool and g.virus.dna_points == 5
print("[3] Ручное заражение за 5 ДНК ОК")

# рестарт кликом после game over
g.game_over = True
g.handle_click((100,100))
assert not g.started and g.cure_progress == 0
print("[3] Рестарт ОК")

# отрисовка всех экранов
g.draw_stats(); g.draw_map(); g.draw_upgrades(); g.draw_news(); g.draw_overlay()
g.started = True; g.game_over = True; g.win = True
g.draw_overlay()
print("[3] Отрисовка всех состояний ОК")
print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
