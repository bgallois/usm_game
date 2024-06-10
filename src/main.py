import pygame
import random
import pygame_menu
import discover
import power_service
import asyncio
import time
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

try:
    from bleak.backends.winrt.util import allow_sta
    allow_sta()
except:
    pass


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_size, t="peloton"):
        super().__init__()
        self.cycle = []
        for i in range(4):
            try:
                self.cycle.append(pygame.transform.scale(
                    pygame.image.load(resource_path("./assets/demo/{}_{}.webp".format(t, i))), (screen_size[0] // 6, screen_size[0] // 6)))
            except BaseException:
                pass
        self.image = self.cycle[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.count = random.randint(0, 2)
        self.update_count = 0
        self.power = 0
        self.t = t

    def update(self):
        if self.power > 0:
            self.rect.x += int(self.power) / 100
            speed_ratio = 200 // self.power + 1
            self.update_count += 1
            if self.update_count % speed_ratio == 0:
                self.count += 1
            self.image = self.cycle[self.count % len(self.cycle)]

    def update_power(self, power):
        self.power = power

    def get_position(self):
        return self.rect.x

    def resize(self, screen_size):
        self.cycle = []
        for i in range(4):
            try:
                self.cycle.append(pygame.transform.scale(
                    pygame.image.load(resource_path("./assets/demo/{}_{}.webp".format(self.t, i))), (screen_size[0] // 6, screen_size[0] // 6)))
            except BaseException:
                pass
        self.image = self.cycle[0]


class Cat(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_size):
        super().__init__()
        self.cycle = []
        for i in range(9):
            self.cycle.append(pygame.transform.scale(
                pygame.image.load(resource_path("./assets/cat/cat-{}.png".format(i))), (screen_size[0] // 12, screen_size[0] // 12)))
        self.image = self.cycle[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.count = random.randint(0, 9)
        self.update_count = 0
        self.speed = random.randint(1, 15)

    def update(self):
        self.count += 1
        if self.count % self.speed == 0:
            self.image = self.cycle[self.count % len(self.cycle)]
        if self.count % 50 == 0:
            x = random.randint(-25, 25)
            self.rect.x += x
            self.rect.y += random.randint(-25, 25)
            if x > 0:
                self.cycle = [
                    pygame.transform.flip(
                        i, True, False) for i in self.cycle]

    def get_position(self):
        return self.rect.x

    def resize(self, screen_size):
        self.cycle = []
        for i in range(9):
            try:
                self.cycle.append(pygame.transform.scale(
                    pygame.image.load(resource_path("./assets/cat/cat-{}.png".format(i))), (screen_size[0] // 12, screen_size[0] // 12)))
            except BaseException:
                pass
        self.image = self.cycle[0]
        self.rect.x = random.randint(
            int(screen_size[0] * 0.1), int(screen_size[0] * 0.9))
        self.rect.y = random.randint(
            int(screen_size[1] * 0.5), int(screen_size[1] * 0.8))


class PowerGauge():
    def __init__(self, screen_size):
        self.x = screen_size[0] // 25
        self.y = 5
        self.w = screen_size[0] // 4
        self.h = screen_size[1] // 25
        self.hp = 0
        self.max_hp = 800
        self.font = pygame.font.SysFont(None, 32)
        self.image = pygame.transform.scale(
            pygame.image.load(resource_path("./assets/demo/power.webp")), (screen_size[0] // 25, screen_size[0] // 25))

    def draw(self, surface):
        ratio = max(0, min(1, self.hp / self.max_hp))
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(
            surface,
            "green",
            (self.x,
             self.y,
             self.w * ratio,
             self.h))
        text = self.font.render(str(int(self.hp)) + "W", True,
                                (min(255, 255 * ratio), min(255, 255 * (1 - ratio)), 10))
        surface.blit(text, (self.w + 1.2 * self.x, 0.30 * self.h))
        surface.blit(self.image, (0.02 * self.x, 0.008 * self.y))

    def resize(self, screen_size):
        self.x = screen_size[0] // 25
        self.w = screen_size[0] // 4
        self.h = screen_size[1] // 25
        self.font = pygame.font.SysFont(None, screen_size[0] // 40)
        self.image = pygame.transform.scale(
            pygame.image.load(resource_path("./assets/demo/power.webp")), (screen_size[0] // 25, screen_size[0] // 25))


class LevelProgress():
    def __init__(self, screen_size):
        self.x = 5
        self.h = screen_size[1] // 20
        self.y = screen_size[1] - self.h - 5
        self.w = screen_size[0] - 10
        self.progress = 0

    def draw(self, surface):
        rect = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        rect.fill((255, 255, 255, 128))
        surface.blit(rect, (self.x, self.y))
        rect_progress = pygame.Surface(
            (self.w * self.progress, self.h), pygame.SRCALPHA)
        rect_progress.fill((0, 0, 0, 128))
        surface.blit(rect_progress, (self.x, self.y))

    def update(self, progress):
        self.progress = progress

    def resize(self, screen_size):
        self.h = screen_size[1] // 20
        self.y = screen_size[1] - self.h - 5
        self.w = screen_size[0] - 10


class GameProgress():
    def __init__(self, screen_size):
        self.x = 5
        self.h = screen_size[1] // 20
        self.y = screen_size[1] - self.h - screen_size[1] // 20
        self.w = screen_size[0] - 10
        self.progress = 0

    def draw(self, surface):
        rect = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        rect.fill((255, 255, 255, 128))
        surface.blit(rect, (self.x, self.y))
        rect_progress = pygame.Surface(
            (self.w * self.progress, self.h), pygame.SRCALPHA)
        rect_progress.fill((0, 0, 0, 128))
        surface.blit(rect_progress, (self.x, self.y))

    def update(self, progress):
        self.progress = progress

    def resize(self, screen_size):
        self.h = screen_size[1] // 20
        self.y = screen_size[1] - self.h - screen_size[1] // 20
        self.w = screen_size[0] - 10


def connect_power(index, element):
    power_service.stop()
    time.sleep(2)  # Let time to thread to close
    if index[0][0] == "Bot":
        power_service.main()
    elif index[0][0] == "None":
        pass
    else:
        power_service.main(element.address)


def load_level(index=0, path=resource_path("./assets/demo/")):
    try:
        display.blit(pygame.transform.scale(
            pygame.image.load(
                resource_path("{}/background_{}.webp".format(path, index))), screen_size), (0, 0))
        display.blit(pygame.transform.scale(
            pygame.image.load(
                resource_path("{}/reward.png".format(path))), (screen_size[0] // 10, screen_size[0] // 10 * 1.5)), (screen_size[0] - screen_size[0] // 10 * 1.1, 50))
        return (index, ["{}/reward.png".format(path)])
    except Exception as e:
        return (-1, ["{}/reward.png".format(path)])


pygame.init()

screen_size = (1024, 576)
display = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

menu = pygame_menu.Menu(
    "Connection",
    screen_size[0] * 0.75,
    screen_size[1] * 0.75,
    theme=pygame_menu.themes.THEME_BLUE,
    onclose=pygame_menu.events.CLOSE)
devices = discover.get_devices()
items = [("Bot", "-1"), ("None", "-1")]
if devices:
    items.extend([(i.name, i) for i in devices if i.name])
menu.add.dropselect("HT", items=items, onchange=connect_power)

load_level()

power = PowerGauge(screen_size)
level_progress = LevelProgress(screen_size)
game_progress = GameProgress(screen_size)

cat_group = pygame.sprite.Group()
for i in range(8):
    cat = Cat(random.randint(int(screen_size[0] *
                                 0.1), int(screen_size[0] *
              0.9)), random.randint(int(screen_size[1] *
                                        0.5), int(screen_size[1] *
                                                  0.8)), screen_size)
    cat_group.add(cat)


hero = Player(0, screen_size[1] - 160, screen_size, t="hero")
player_group = pygame.sprite.Group()
player_group.add(hero)

peloton = pygame.sprite.Group()
for i in reversed(range(10)):
    conc = Player(-random.randint(100, 300),
                  screen_size[1] - 160 - 1.2 * i, screen_size)
    peloton.add(conc)

running = True
index = 0
level_index = 0
while running:
    # Event handling
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                menu.enable()
        elif event.type == pygame.VIDEORESIZE:
            for i in peloton:
                i.rect.x = i.rect.x / screen_size[0] * event.dict['size'][0]
                i.rect.y = i.rect.y / screen_size[1] * event.dict['size'][1]
            for i in player_group:
                i.rect.x = i.rect.x / screen_size[0] * event.dict['size'][0]
                i.rect.y = i.rect.y / screen_size[1] * event.dict['size'][1]
            screen_size = event.dict['size']
            level_progress.resize(screen_size)
            game_progress.resize(screen_size)
            power.resize(screen_size)
            for i in cat_group:
                i.resize(screen_size)
            for i in peloton:
                i.resize(screen_size)
            hero.resize(screen_size)

    (index, rewards) = load_level(index, resource_path(
        "./assets/stage_{}".format(level_index)))

    if index < 0:
        index = 0
        level_index += 1

        if level_index > 20:
            display.blit(pygame.transform.scale(
                pygame.image.load(
                    resource_path("./assets/final/background_0.webp")), screen_size), (0, 0))
            pygame.display.update()
        continue

    inst_power = power_service.get_power()

    power.hp = inst_power
    power.draw(display)
    hero.power = inst_power

    level_progress.draw(display)
    hero_position = hero.get_position()
    level_progress.update(hero_position / screen_size[0] * 0.25 + 0.25 * index)

    game_progress.draw(display)
    game_progress.update(level_index / 20)

    cat_group.draw(display)
    cat_group.update()

    player_group.draw(display)
    player_group.update()

    # Characters update
    peloton.draw(display)
    for i in peloton:
        if inst_power > 0:
            i.update_power(inst_power + random.randint(-150, 150))
        else:
            i.update_power(inst_power)
    peloton.update()

    if hero_position > screen_size[0]:
        hero.rect.x = 0
        for i in peloton:
            i.rect.x = -random.randint(100, 300)
        index += 1

    if index == 0 and hero_position / screen_size[0] < 0.15:
        display.blit(pygame.transform.scale(
            pygame.image.load(
                rewards[0]), (screen_size[0] // 3, screen_size[0] // 3 * 1.5)), (screen_size[0] // 4, 50))
    # Menu
    if menu.is_enabled():
        menu.draw(display)  # Need to be before update
        menu.update(events)

    pygame.display.update()
    clock.tick(10)

pygame.quit()
