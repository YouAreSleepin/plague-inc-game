import os, random
os.environ["SDL_VIDEODRIVER"]="dummy"
random.seed(1)
from plague_simulator import Game, UPGRADES

g = Game(); g.handle_click(g.regions[5].rect.center)
t=0
while not g.game_over and t<3000: g.tick(); t+=1
print("[пассив] тиков:", t, "cure:", round(g.cure_progress), "win:", g.win, "|", g.end_reason)

g.reset(); g.handle_click(g.regions[30].rect.center)
t=0
while not g.game_over and t<20000:
    g.tick()
    for br in ("transmission","symptoms"):
        for i in range(len(UPGRADES[br])):
            if g.virus.can_buy(br,i): g.virus.buy(br,i)
    t+=1
print("[агресс] тиков:", t, "cure:", round(g.cure_progress), "win:", g.win, "|", g.end_reason)

g.reset(); g.handle_click(g.regions[19].rect.center)
t=0
while not g.game_over and t<3000:
    g.tick()
    for i in range(len(UPGRADES["transmission"])):
        if g.virus.can_buy("transmission",i): g.virus.buy("transmission",i)
    t+=1
inf=sum(1 for r in g.regions if r.infected_bool)
print("[умерен] тиков:", t, "cure:", round(g.cure_progress), "стран заражено:", inf, "win:", g.win, "|", g.end_reason)
