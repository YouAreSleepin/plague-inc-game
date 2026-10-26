import os, random
os.environ["SDL_VIDEODRIVER"]="dummy"
from plague_simulator import Game, UPGRADES

def smart_game(seed, buy_resist=True):
    random.seed(seed)
    g = Game()
    g.handle_click(g.regions[30].rect.center)
    t = 0
    while not g.game_over and t < 20000:
        g.tick(); t += 1
        v = g.virus
        # стратегия: сначала скрытность+устойчивость, потом передача, летальные симптомы — в конце
        if buy_resist:
            for i in range(len(UPGRADES["resistance"])):
                if v.can_buy("resistance", i): v.buy("resistance", i)
        for i in range(len(UPGRADES["transmission"])):
            if v.can_buy("transmission", i): v.buy("transmission", i)
        inf_c = sum(1 for r in g.regions if r.infected_bool)
        healthy_left = sum(r.healthy for r in g.regions)
        world = sum(r.total_pop for r in g.regions)
        # открываем lethal только когда почти весь мир заражён
        if inf_c >= 38 or healthy_left < world*0.15:
            for i in [0,1,2,3,4]:
                if v.can_buy("symptoms", i): v.buy("symptoms", i)
    return g, t

for seed in (1, 2, 3):
    g, t = smart_game(seed)
    dead = sum(r.dead for r in g.regions); world = sum(r.total_pop for r in g.regions)
    print(f"[умник seed={seed}] тиков={t} cure={g.cure_progress:.0f}% win={g.win} умерло={dead/world*100:.0f}% | {g.end_reason}")

# без прокачки устойчивости — должно быть сложнее
g, t = smart_game(4, buy_resist=False)
print(f"[без устойчивости] тиков={t} cure={g.cure_progress:.0f}% win={g.win} | {g.end_reason}")
