import pygame
import random
import time
import pygame_menu
import discover
import power_service
import asyncio

TIME = time.time()
PREV = 0


def get_power():
    # Random power generator for dev
    global TIME
    global PREV
    if time.time() - TIME > 1.5:
        TIME = time.time()
        PREV = random.gauss(300, 100)
    return max(0, PREV)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, t="peloton"):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("./assets/demo/{}_0.webp".format(t)), (150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cycle = [self.image, pygame.transform.scale(
            pygame.image.load("./assets/demo/{}_1.webp".format(t)), (150, 150))]
        self.count = random.randint(0, 2)
        self.update_count = 0
        self.power = 0

    def update(self):
        if self.power > 0:
            self.rect.x += int(self.power) / 100
            speed_ratio = 1000 // self.power + 1
            self.update_count += 1
            if self.update_count % speed_ratio == 0:
                self.count += 1
            self.image = self.cycle[self.count % 2]

    def update_power(self, power):
        self.power = power

    def get_position(self):
        return self.rect.x


class PowerGauge():
    def __init__(self):
        self.x = 40
        self.y = 5
        self.w = 300
        self.h = 20
        self.hp = 0
        self.max_hp = 800
        self.font = pygame.font.SysFont(None, 32)
        self.image = pygame.transform.scale(
            pygame.image.load("./assets/demo/power.webp"), (40, 40))

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
        surface.blit(text, (self.w + 1.2 * self.x, 0.25 * self.h))
        surface.blit(self.image, (self.x - 40, self.y - 10))


class LevelProgress():
    def __init__(self, screen_size):
        self.x = 5
        self.y = screen_size[1] - 25
        self.w = screen_size[0] - 10
        self.h = 20
        self.progress = 0.5

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


def connect_power(index, element):
    power_service.main(element.address)


pygame.init()

screen_size = (1024, 576)
display = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

menu = pygame_menu.Menu(
    "Connection",
    400,
    300,
    theme=pygame_menu.themes.THEME_BLUE,
    onclose=pygame_menu.events.CLOSE)
devices = discover.get_devices()
menu.add.dropselect("HT", items=[(i.name, i)
                    for i in devices], onchange=connect_power)
####

backgrounds = []
for i in range(4):
    backgrounds.append(
        pygame.image.load(
            "./assets/demo/background_{}.webp".format(i)))

power = PowerGauge()
level_progress = LevelProgress(screen_size)

hero = Player(0, screen_size[1] - 150, t="hero")
player_group = pygame.sprite.Group()
player_group.add(hero)

peloton = pygame.sprite.Group()
for i in range(10):
    conc = Player(-random.randint(100, 300), screen_size[1] - 150 - i)
    peloton.add(conc)

running = True
index = 0
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                menu.enable()

    display.blit(pygame.transform.scale(
        backgrounds[index % 4], screen_size), (0, 0))

    inst_power = power_service.get_power()

    power.hp = inst_power
    power.draw(display)
    hero.power = inst_power

    level_progress.draw(display)
    hero_position = hero.get_position()
    level_progress.update(hero_position / screen_size[0] * 0.25 + 0.25 * index)

    player_group.draw(display)
    player_group.update()

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

    if menu.is_enabled():
        menu.draw(display)  # Need to be before update
        menu.update(events)

    pygame.display.update()
    clock.tick(10)

pygame.quit()
