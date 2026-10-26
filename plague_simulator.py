# -*- coding: utf-8 -*-
"""
ПРАКТИКА «ПАТОГЕН» — симулятор эпидемии в стиле Plague Inc.
Игра на Python + Pygame. Один файл, готов к упаковке через PyInstaller.

Управление:
  - Клик по региону на карте — заражение нулевого пациента (старт игры).
  - Кнопки внизу — прокачка вируса за Очки ДНК.
  - ESC — выйти, R — рестарт после конца игры.
"""

import os
import random
import sys

import pygame


def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает для dev и PyInstaller exe."""
    try:
        # PyInstaller создаёт временную папку _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ============================== НАСТРОЙКИ ==============================

WIDTH, HEIGHT = 1024, 768
FPS = 60

# Цветовая палитра «хакерской био-лаборатории»
C_BG        = (10, 14, 18)     # фон
C_PANEL     = (16, 24, 28)     # панели
C_GRID      = (0, 60, 40)      # сетка-скан
C_GREEN     = (40, 200, 90)    # здоровый регион
C_RED       = (220, 50, 40)    # заражённый регион
C_DEAD      = (35, 35, 40)     # вымерший регион
C_TEXT      = (200, 230, 210)
C_CYAN      = (0, 220, 255)
C_DNA       = (180, 90, 255)
C_BTN       = (25, 40, 45)
C_BTN_ON    = (45, 70, 60)
C_BTN_BORDER= (0, 160, 130)
C_WARN      = (255, 200, 40)

TICK_INTERVAL = 1.0            # секунда игровой логики
CURE_START_DELAY = 30.0        # через сколько секунд начинают разрабатывать лекарство

# ============================== РЕГИОНЫ ==============================
# Каждый регион: название, население, прямоугольник (x, y, w, h), соседи.
# Сетка ~45 регионов, расположенных «как карта мира»:
# Северная Америка, Южная Америка, Европа, Африка, Азия, Океания.

REGIONS_DEF = [
    # name,               pop(млн), rect(x,y,w,h),      neighbors(indices)
    ("Аляска",            0.7,  (30,  90, 70, 55),  [1, 4]),
    ("Канада",             38,   (105, 90, 95, 60),  [0, 2, 4]),
    ("Сев.-Зап. США",      25,   (205, 90, 60, 55),  [1, 3, 5]),
    ("Калифорния",         40,   (205, 150, 60, 50), [2, 5, 6]),
    ("Вост. Канада",       20,   (105, 155, 95, 50), [1, 5, 7]),
    ("Вост. США",          130,  (205, 205, 80, 55), [2, 3, 4, 6, 8]),
    ("Техас",              29,   (150, 210, 50, 55), [3, 5, 7]),
    ("Мексика",            130,  (120, 270, 80, 50), [4, 6, 8]),
    ("Центр. Америка",     50,   (150, 325, 60, 40), [5, 7, 9]),

    ("Колумбия",           50,   (180, 370, 60, 50), [8, 10, 11]),
    ("Бразилия",           215,  (245, 380, 90, 80), [9, 11, 12, 13]),
    ("Перу",               34,   (180, 425, 60, 60), [9, 10, 12]),
    ("Боливия",            12,   (245, 465, 55, 45), [10, 11, 13]),
    ("Аргентина",          46,   (245, 515, 60, 80), [10, 12]),
    ("Чили",               20,   (195, 490, 45, 105),[11, 12]),

    ("Британия",           68,   (400, 100, 45, 45), [17, 18, 21]),
    ("Скандинавия",        27,   (450, 80, 60, 55),  [17, 19, 22]),
    ("Зап. Европа",        160,  (400, 150, 60, 60), [15, 17, 19, 21, 23]),
    ("Вост. Европа",       100,  (465, 140, 70, 60), [16, 17, 20, 22, 24]),
    ("Россия",             144,  (540, 80, 160, 70), [16, 18, 21, 25, 26]),
    ("Средиземноморье",    80,   (465, 205, 70, 45), [18, 19, 23, 24, 27]),
    ("Турция",             85,   (540, 155, 60, 50), [19, 20, 24, 26]),
    ("Иран",               88,   (605, 160, 60, 55), [20, 21, 25, 27, 28]),
    ("Зап. Африка",        380,  (400, 260, 85, 90), [17, 20, 24, 25]),
    ("Центр. Африка",      180,  (490, 255, 80, 90), [20, 21, 23, 26, 27]),
    ("Вост. Африка",       160,  (575, 215, 70, 90), [21, 22, 24, 27, 29]),
    ("Юж. Африка",         130,  (490, 350, 90, 80), [23, 24, 26]),
    ("Мадагаскар",         29,   (650, 310, 45, 55), [25, 27]),

    ("Казахстан",          19,   (605, 100, 95, 55), [19, 22, 28, 29]),
    ("Сибирь",             36,   (705, 80, 110, 70), [19, 28, 30, 31]),
    ("Китай",              1410, (760, 155, 100, 70),[22, 28, 29, 31, 32, 33]),
    ("Япония",             125,  (865, 130, 55, 50), [30, 32]),
    ("Корея",              77,   (830, 160, 45, 45), [30, 31, 33]),
    ("Индия",              1400, (680, 215, 85, 80), [22, 30, 34, 35]),
    ("Юго-Вост. Азия",     680,  (770, 230, 90, 70), [30, 32, 35, 36]),
    ("Индонезия",          275,  (800, 305, 100, 55),[34, 35, 37]),
    ("Филиппины",          115,  (870, 235, 50, 60), [34, 36]),
    ("Австралия",          26,   (830, 380, 120, 90),[36, 39]),
    ("Новая Зеландия",     5,    (955, 480, 45, 55), [38]),
    ("Океания",            13,   (900, 300, 70, 70), [36, 37, 39]),

    ("Гренландия",         0.06, (320, 30, 70, 50),  [15]),
    ("Исландия",           0.4,  (365, 60, 45, 30),  [15, 16]),
]


class Region:
    def __init__(self, idx, name, pop, rect, neighbors):
        self.idx = idx
        self.name = name
        self.total_pop = max(1, int(pop * 1_000_000))
        self.rect = pygame.Rect(rect)
        self.neighbors = neighbors
        self.healthy = self.total_pop
        self.infected = 0
        self.dead = 0
        self.infected_bool = False
        self.dead_region = False

    @property
    def infected_pct(self):
        return self.infected / self.total_pop if self.total_pop else 0

    def color(self):
        if self.dead_region or self.healthy == 0:
            return C_DEAD
        if not self.infected_bool:
            return C_GREEN
        # Плавный переход зелёный -> красный по доле заражённых/мёртвых
        t = min(1.0, (self.infected + self.dead * 2) / self.total_pop)
        r = int(C_GREEN[0] + (C_RED[0] - C_GREEN[0]) * t)
        g = int(C_GREEN[1] + (C_RED[1] - C_GREEN[1]) * t)
        b = int(C_GREEN[2] + (C_RED[2] - C_GREEN[2]) * t)
        return (r, g, b)


def make_regions():
    regions = []
    for i, (name, pop, rect, nb) in enumerate(REGIONS_DEF):
        regions.append(Region(i, name, pop, rect, nb))
    # Симметричность соседей
    for reg in regions:
        for n in list(reg.neighbors):
            if reg.idx not in regions[n].neighbors:
                regions[n].neighbors.append(reg.idx)
    return regions


# ============================== ПРОКАЧКА ==============================
# Три ветки: пути передачи, симптомы, устойчивость.

UPGRADES = {
    "transmission": [
        ("Крысы-переносчики", 5, "Локальное распространение +"),
        ("Комары",            8, "Передача через кровососов +"),
        ("Воздушно-капельный",12,"Заражение соседей ++"),
        ("Водный путь",       15,"Перенос по воде +++"),
        ("Глобальный транспорт",25,"Международные прыжки ++++"),
    ],
    "symptoms": [
        ("Кашель",            4, "Легкий симптом, тяжесть 1"),
        ("Жар",               6, "Тяжесть 2, смертность 1"),
        ("Кровотечения",      10,"Тяжесть 4, смертность 3"),
        ("Отказ органов",     16,"Тяжесть 7, смертность 6"),
        ("Некротическая фаза",24,"Тяжесть 10, смертность 10"),
    ],
    "resistance": [
        ("Холодоустойчивость",6, "Лекарство замедляется"),
        ("Жароустойчивость",  8, "Лекарство замедляется"),
        ("Скрытность",        14,"Доктор медленнее реагирует"),
        ("Геномная стабильность",20,"Сильное замедление лекарства"),
    ],
}

# Влияние каждой купленной прокачки: (тяжесть, смертность, скорость заражения, infect_spread_bonus, cure_slow)
SYMPTOMS_EFFECTS = [(1, 0, 0, 0), (2, 1, 0, 0), (4, 3, 1, 0), (7, 6, 1, 0), (10, 10, 2, 0)]
TRANSMISSION_EFFECTS = [(0, 0, 1, 0.03), (0, 0, 1, 0.05), (0, 0, 2, 0.09), (0, 0, 2, 0.13), (0, 0, 3, 0.22)]
RESIST_EFFECTS = [(0, 0, 0.15), (0, 0, 0.2), (0, 0, 0.3), (0, 0, 0.45)]


class Virus:
    def __init__(self):
        self.dna_points = 10
        self.bought = {"transmission": set(), "symptoms": set(), "resistance": set()}

    @property
    def severity(self):
        s = sum(SYMPTOMS_EFFECTS[i][0] for i in self.bought["symptoms"])
        return s

    @property
    def lethality(self):
        return sum(SYMPTOMS_EFFECTS[i][1] for i in self.bought["symptoms"])

    @property
    def infect_rate(self):
        return 1 + sum(TRANSMISSION_EFFECTS[i][2] for i in self.bought["transmission"]) \
               + sum(SYMPTOMS_EFFECTS[i][2] for i in self.bought["symptoms"])

    @property
    def spread_chance(self):
        return 0.02 + sum(TRANSMISSION_EFFECTS[i][3] for i in self.bought["transmission"])

    @property
    def cure_slow(self):
        return sum(RESIST_EFFECTS[i][2] for i in self.bought["resistance"])

    def cost(self, branch, idx):
        return UPGRADES[branch][idx][1]

    def can_buy(self, branch, idx):
        return idx not in self.bought[branch] and self.dna_points >= UPGRADES[branch][idx][1]

    def buy(self, branch, idx):
        if self.can_buy(branch, idx):
            self.dna_points -= UPGRADES[branch][idx][1]
            self.bought[branch].add(idx)
            return True
        return False


# ============================== ИГРА ==============================

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ПАТОГЕН :: симулятор эпидемии")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Шрифты: пробуем загрузить из assets (для PyInstaller), иначе системный Arial
        font_path = resource_path(os.path.join("assets", "fonts", "DejaVuSans.ttf"))
        if os.path.exists(font_path):
            self.font_big = pygame.font.Font(font_path, 26)
            self.font = pygame.font.Font(font_path, 18)
            self.font_small = pygame.font.Font(font_path, 14)
            self.font_tiny = pygame.font.Font(font_path, 12)
        else:
            self.font_big = pygame.font.SysFont("arial", 26, bold=True)
            self.font = pygame.font.SysFont("arial", 18)
            self.font_small = pygame.font.SysFont("arial", 14)
            self.font_tiny = pygame.font.SysFont("arial", 12)

        # Иконка окна (если есть в assets/icon.ico)
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            try:
                pygame.display.set_icon(pygame.image.load(icon_path))
            except Exception:
                pass

        self.reset()

    def reset(self):
        self.regions = make_regions()
        self.virus = Virus()
        self.started = False
        self.game_over = False
        self.win = False
        self.end_reason = ""
        self.elapsed = 0.0
        self.tick_timer = 0.0
        self.cure_progress = 0.0     # 0..100 %
        self.cure_started = False
        self.news = ["Кликните по региону, чтобы заразить его."]
        self.selected_branch = "transmission"
        # Раскладка кнопок прокачки (вкладки + список выбранный ветки)
        self.buttons = self._make_buttons()

    # ---------- кнопки ----------
    def _make_buttons(self):
        buttons = []
        # Вкладки веток внизу слева
        tab_y = 560
        tabs = [("transmission", "ПУТИ ПЕРЕДАЧИ"), ("symptoms", "СИМПТОМЫ"), ("resistance", "УСТОЙЧИВОСТЬ")]
        for i, (key, label) in enumerate(tabs):
            buttons.append({"type": "tab", "key": key, "label": label,
                            "rect": pygame.Rect(15 + i * 150, tab_y, 140, 34)})
        # Кнопки прокачек выбранной ветки
        for i, (name, cost, desc) in enumerate(UPGRADES[self.selected_branch]):
            buttons.append({"type": "upgrade", "index": i,
                            "rect": pygame.Rect(15, 600 + i * 32, 435, 28)})
        return buttons

    def refresh_upgrade_buttons(self):
        self.buttons = [b for b in self.buttons if b["type"] == "tab"]
        for i in range(len(UPGRADES[self.selected_branch])):
            self.buttons.append({"type": "upgrade", "index": i,
                                 "rect": pygame.Rect(15, 600 + i * 32, 435, 28)})

    # ---------- логика ----------
    def start_infection(self, region):
        self.started = True
        region.infected_bool = True
        region.infected = 1
        region.healthy = region.total_pop - 1
        self.add_news(f"[НУЛЬ] Нулевой пациент: {region.name}")

    def add_news(self, text):
        self.news.append(text)
        if len(self.news) > 5:
            self.news.pop(0)

    def tick(self):
        """Раз в секунду обновляет пандемию (дискретный шаг модели)."""
        v = self.virus
        new_dna = 0

        # --- Фаза 1: рост заражения и смертность в активных очагах -------
        for r in self.regions:
            if not r.infected_bool or r.infected <= 0:
                continue
            # Рост заразы: экспоненциально, зависит от infect_rate и плотности.
            # min(..., healthy // 2) — вирус не «съедает» весь регион за один
            # тик: часть населения всегда остаётся здоровой и является
            # резервуаром для дальнейшего распространения.
            growth = int(r.infected * (0.10 + 0.03 * v.infect_rate)) \
                     + int(r.healthy * 0.01 * v.infect_rate)
            growth = min(growth, r.healthy // 2)
            r.healthy -= growth
            r.infected += growth

            # Смерти: зависят от летальности и доли заражённых.
            # При летальности 0 носительство бессмертно — вирус не «угасает».
            if v.lethality > 0 and r.infected > 0:
                deaths = int(max(1, r.infected * (0.001 + v.lethality * 0.0011)))
                deaths = min(deaths, r.infected)
                if deaths > 0:
                    r.infected -= deaths
                    r.dead += deaths
                    new_dna += deaths // 400000 + 1

            # Регион вымер?
            if r.healthy == 0 and r.infected == 0 and not r.dead_region:
                r.dead_region = True
                self.add_news(f"[СМЕРТЬ] Регион {r.name} полностью вымер.")

            new_dna += 2 + int(r.infected / 5_000_000)  # ДНК за активность очага

        # --- Фаза 2: распространение по соседям --------------------------
        # Отдельно от фазы роста, чтобы свежий нулевой пациент (infected==1)
        # мог стать источником заражения, как только накопит носителей.
        for r in self.regions:
            if not r.infected_bool or r.infected <= 50:
                continue
            for nb_idx in r.neighbors:
                nb = self.regions[nb_idx]
                if nb.healthy > 0 and not nb.infected_bool:
                    chance = v.spread_chance * (r.infected / r.total_pop)
                    if random.random() < chance:
                        nb.infected_bool = True
                        nb.infected = 1
                        nb.healthy -= 1
                        new_dna += 2  # бонус ДНК за новую страну
                        self.add_news(f"[+] Вирус перекинулся: {nb.name}")
                        break

        # Глобальные прыжки (высшая прокачка передачи)
        if 4 in v.bought["transmission"]:
            infected_list = [r for r in self.regions if r.infected_bool and r.infected > 100]
            healthy_list = [r for r in self.regions if r.healthy > 0 and not r.infected_bool]
            if infected_list and healthy_list and random.random() < 0.25:
                src = random.choice(infected_list)
                dst = random.choice(healthy_list)
                dst.infected_bool = True
                dst.infected = 1
                dst.healthy -= 1
                self.add_news(f"[АВИА] Авиаперелёт: {src.name} → {dst.name}")

        # Очки ДНК капают за активность вируса (скорость распространения заразы)
        inf_countries = sum(1 for r in self.regions if r.infected_bool and r.infected > 0)
        self.virus.dna_points += new_dna + max(0, inf_countries - 1)

        # Разработка лекарства: старт через 30 секунд после нулевого пациента
        if self.started and self.elapsed >= CURE_START_DELAY:
            if not self.cure_started:
                self.cure_started = True
                self.add_news("[ЛЕКАРСТВО] WHO начала разработку лекарства!")
            infected_pop = sum(r.infected for r in self.regions)
            alive_pop = sum(r.healthy + r.infected for r in self.regions)
            world_pop = sum(r.total_pop for r in self.regions)
            awareness = min(1.0, inf_countries / len(self.regions))
            # "Тяжесть" симптомов — главный ускоритель разработки (видимые жертвы!)
            base = 0.04 + v.severity * 0.055
            # Много больных = больше лабораторий и финансирования
            sick_share = infected_pop / max(1, world_pop)
            research_power = 0.5 + 1.0 * sick_share          # до 1.5x при пандемии
            # Вымирание мешает учёным: мёртвые лаборатории не работают
            survivors = alive_pop / max(1, world_pop)
            staff = min(1.0, survivors * 4)                  # <25% выживших — дефицит кадров
            speed = base * research_power * (0.3 + 0.7 * awareness) * staff \
                    / (1 + 1.6 * v.cure_slow)
            # После гибели цивилизации разрабатывать некому и не на что
            if survivors < 0.05:
                speed *= max(0.0, (survivors - 0.01) / 0.04)
            self.cure_progress = min(100.0, self.cure_progress + speed)

        # Победа / поражение
        alive_total = sum(r.healthy + r.infected for r in self.regions)
        if self.cure_progress >= 100:
            self.game_over = True
            self.win = False
            self.end_reason = "Человечество создало лекарство. Патоген уничтожен."
        elif alive_total == 0:
            self.game_over = True
            self.win = True
            self.end_reason = "Все люди на Земле мертвы. Вы победили!"
        elif self.started:
            active = any(r.infected > 0 for r in self.regions)
            remaining_healthy = any(r.healthy > 0 for r in self.regions)
            if remaining_healthy and not active:
                # Носителей нет — вирус угас, здоровые регионы спаслись
                self.game_over = True
                self.win = False
                self.end_reason = "Вирус угас: не осталось носителей, а здоровые регионы целы."
            elif not remaining_healthy and 0 < alive_total < 1000:
                # Все здоровые умерли, оставшиеся больные обречены — победа
                self.game_over = True
                self.win = True
                self.end_reason = "Человечество уничтожено. Оставшиеся больные обречены. Победа!"

    # ---------- ввод ----------
    def handle_click(self, pos):
        mx, my = pos
        if self.game_over:
            self.reset()
            return
        # Табы
        for b in self.buttons:
            if b["type"] == "tab" and b["rect"].collidepoint(pos):
                if self.selected_branch != b["key"]:
                    self.selected_branch = b["key"]
                    self.refresh_upgrade_buttons()
                return
        # Прокачки
        branch = self.selected_branch
        for b in self.buttons:
            if b["type"] == "upgrade" and b["rect"].collidepoint(pos):
                i = b["index"]
                name, cost, _ = UPGRADES[branch][i]
                if self.virus.buy(branch, i):
                    self.add_news(f"[ГЕНОМ] Прокачано: {name} (-{cost} ДНК)")
                else:
                    self.add_news(f"Недостаточно ДНК для: {name}")
                return
        # Карта
        for r in self.regions:
            if r.rect.collidepoint(pos):
                if not self.started:
                    self.start_infection(r)
                elif r.healthy > 0 and not r.infected_bool:
                    # Прямое заражение кликом за 5 ДНК
                    if self.virus.dna_points >= 5:
                        self.virus.dna_points -= 5
                        r.infected_bool = True
                        r.infected = 1
                        r.healthy -= 1
                        self.add_news(f"[ИНЪЕКЦИЯ] Принудительное заражение: {r.name}")
                    else:
                        self.add_news("Нужно 5 ДНК для ручного заражения.")
                return

    # ---------- отрисовка ----------
    def draw_map(self):
        # Фон-«сканер»
        map_area = pygame.Rect(10, 70, WIDTH - 20, 480)
        pygame.draw.rect(self.screen, (8, 16, 14), map_area, border_radius=6)
        for x in range(map_area.left, map_area.right, 40):
            pygame.draw.line(self.screen, C_GRID, (x, map_area.top), (x, map_area.bottom), 1)
        for y in range(map_area.top, map_area.bottom, 40):
            pygame.draw.line(self.screen, C_GRID, (map_area.left, y), (map_area.right, y), 1)

        mouse = pygame.mouse.get_pos()
        for r in self.regions:
            col = r.color()
            pygame.draw.rect(self.screen, col, r.rect, border_radius=3)
            outline = C_CYAN if r.rect.collidepoint(mouse) else (0, 90, 70)
            pygame.draw.rect(self.screen, outline, r.rect, width=2, border_radius=3)
            # Маркеры
            if r.infected_bool and not r.dead_region:
                pulse = abs(pygame.math.Vector2(1, 0).rotate(self.elapsed * 90).x)
                cx, cy = r.rect.center
                pygame.draw.circle(self.screen, (255, 255, 120), (cx, cy), int(3 + 2 * pulse))
            if r.dead_region:
                cx, cy = r.rect.center
                pygame.draw.line(self.screen, (90, 90, 90), (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
                pygame.draw.line(self.screen, (90, 90, 90), (cx + 6, cy - 6), (cx - 6, cy + 6), 2)

        # Подпись региона под курсором
        for r in self.regions:
            if r.rect.collidepoint(mouse):
                txt = f"{r.name}: зд. {r.healthy:,} | инф. {r.infected:,} | ум. {r.dead:,}".replace(",", " ")
                surf = self.font_small.render(txt, True, C_CYAN)
                bg = pygame.Rect(0, 0, surf.get_width() + 12, 22)
                bg.topleft = (min(mouse[0] + 12, WIDTH - bg.width - 5), 575)
                pygame.draw.rect(self.screen, (5, 20, 25), bg, border_radius=4)
                pygame.draw.rect(self.screen, C_BTN_BORDER, bg, width=1, border_radius=4)
                self.screen.blit(surf, (bg.x + 6, bg.y + 3))
                break

    def draw_stats(self):
        panel = pygame.Rect(0, 0, WIDTH, 64)
        pygame.draw.rect(self.screen, C_PANEL, panel)
        pygame.draw.line(self.screen, C_BTN_BORDER, (0, 64), (WIDTH, 64), 2)

        healthy = sum(r.healthy for r in self.regions)
        infected = sum(r.infected for r in self.regions)
        dead = sum(r.dead for r in self.regions)

        def fmt(n):
            if n >= 1_000_000:
                return f"{n / 1_000_000:.1f} млн"
            if n >= 1_000:
                return f"{n / 1_000:.1f} тыс"
            return str(n)

        stats = [("Здоровые", fmt(healthy), C_GREEN),
                 ("Зараженные", fmt(infected), C_RED),
                 ("Умершие", fmt(dead), (150, 150, 160)),
                 ("Очки ДНК", str(self.virus.dna_points), C_DNA)]
        x = 20
        for label, val, col in stats:
            self.screen.blit(self.font_small.render(label.upper(), True, (120, 160, 140)), (x, 8))
            self.screen.blit(self.font_big.render(val, True, col), (x, 26))
            x += 175

        # Шкала лекарства
        bar = pygame.Rect(x + 20, 22, WIDTH - x - 60, 26)
        self.screen.blit(self.font_small.render("РАЗРАБОТКА ЛЕКАРСТВА", True, (120, 160, 140)), (bar.x, 6))
        pygame.draw.rect(self.screen, (30, 30, 40), bar, border_radius=6)
        fillw = int(bar.width * self.cure_progress / 100)
        if fillw > 0:
            pygame.draw.rect(self.screen, (60, 140, 255), (bar.x, bar.y, fillw, bar.height), border_radius=6)
        pygame.draw.rect(self.screen, C_CYAN, bar, width=2, border_radius=6)
        pct = self.font.render(f"{self.cure_progress:.0f}%", True, C_TEXT)
        self.screen.blit(pct, (bar.right - pct.get_width() - 8, bar.y + 3))

        if self.started and not self.cure_started:
            left = max(0, CURE_START_DELAY - self.elapsed)
            warn = self.font_small.render(f"WHO начнёт разработку лекарства через {left:.0f} с",
                                          True, C_WARN)
            self.screen.blit(warn, (bar.x, bar.bottom + 2))

    def draw_upgrades(self):
        panel = pygame.Rect(10, 552, 460, 206)
        pygame.draw.rect(self.screen, C_PANEL, panel, border_radius=6)
        pygame.draw.rect(self.screen, C_BTN_BORDER, panel, width=2, border_radius=6)

        branch = self.selected_branch
        for b in self.buttons:
            if b["type"] == "tab":
                active = b["key"] == branch
                col = C_BTN_ON if active else C_BTN
                pygame.draw.rect(self.screen, col, b["rect"], border_radius=5)
                pygame.draw.rect(self.screen, C_BTN_BORDER, b["rect"], width=2, border_radius=5)
                t = self.font_small.render(b["label"], True, C_TEXT if active else (110, 140, 125))
                self.screen.blit(t, t.get_rect(center=b["rect"].center))

        for b in self.buttons:
            if b["type"] != "upgrade":
                continue
            i = b["index"]
            name, cost, desc = UPGRADES[branch][i]
            bought = i in self.virus.bought[branch]
            affordable = self.virus.dna_points >= cost
            col = (20, 60, 40) if bought else (C_BTN if affordable else (30, 22, 22))
            pygame.draw.rect(self.screen, col, b["rect"], border_radius=4)
            pygame.draw.rect(self.screen, C_BTN_BORDER if affordable or bought else (90, 50, 50),
                             b["rect"], width=1, border_radius=4)
            label = f"[x] {name}" if bought else name
            self.screen.blit(self.font_small.render(label, True, C_TEXT), (b["rect"].x + 8, b["rect"].y + 5))
            d = self.font_tiny.render(desc, True, (130, 170, 150))
            self.screen.blit(d, (b["rect"].x + 170, b["rect"].y + 7))
            cost_s = self.font_small.render("КУПЛЕНО" if bought else f"{cost} ДНК",
                                            True, C_DNA if affordable else (120, 80, 80))
            self.screen.blit(cost_s, (b["rect"].right - cost_s.get_width() - 8, b["rect"].y + 5))

        # Характеристики вируса
        v = self.virus
        info = (f"Тяжесть: {v.severity}   Летальность: {v.lethality}   "
                f"Заразность: {v.infect_rate}   Распространение: {int(v.spread_chance*100)}%")
        self.screen.blit(self.font_tiny.render(info, True, (150, 200, 170)), (panel.x + 8, panel.bottom - 18))

    def draw_news(self):
        panel = pygame.Rect(480, 552, WIDTH - 490, 206)
        pygame.draw.rect(self.screen, (12, 20, 22), panel, border_radius=6)
        pygame.draw.rect(self.screen, (0, 90, 80), panel, width=1, border_radius=6)
        self.screen.blit(self.font_small.render("ЖУРНАЛ СОБЫТИЙ", True, C_CYAN), (panel.x + 10, panel.y + 8))
        for i, line in enumerate(self.news[-5:]):
            t = self.font_small.render("> " + line, True, (170, 210, 180))
            self.screen.blit(t, (panel.x + 10, panel.y + 32 + i * 24))

    def draw_overlay(self):
        if not self.started:
            surf = self.font_big.render("Кликните по любому региону, чтобы выпустить вирус", True, C_CYAN)
            glow = pygame.Surface((surf.get_width() + 30, surf.get_height() + 16), pygame.SRCALPHA)
            glow.fill((0, 20, 25, 220))
            self.screen.blit(glow, surf.get_rect(center=(WIDTH // 2, 300)))
            self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, 300)))
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            title = "ПОБЕДА ПАТОГЕНА" if self.win else "ПОРАЖЕНИЕ"
            col = C_RED if self.win else C_CYAN
            t1 = self.font_big.render(title, True, col)
            t2 = self.font.render(self.end_reason, True, C_TEXT)
            t3 = self.font_small.render("Нажмите R или кликните мышью — начать заново", True, C_WARN)
            self.screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            self.screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 5)))
            self.screen.blit(t3, t3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45)))

    # ---------- главный цикл ----------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if ev.key == pygame.K_r and self.game_over:
                        self.reset()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.handle_click(ev.pos)

            if self.started and not self.game_over:
                # Игровые часы (для лекарства) идут в реальном времени,
                # а дискретная модель пандемии обновляется раз в секунду.
                self.elapsed += dt
                self.tick_timer += dt
                while self.tick_timer >= TICK_INTERVAL:
                    self.tick_timer -= TICK_INTERVAL
                    self.tick()

            self.screen.fill(C_BG)
            self.draw_stats()
            self.draw_map()
            self.draw_upgrades()
            self.draw_news()
            self.draw_overlay()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
