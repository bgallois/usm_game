import pygame
import random
import time

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
        self.dt = 10 / 1000

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


pygame.init()
screen_size = (1024, 576)
display = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

background = pygame.image.load("./assets/demo/background.webp")

power = PowerGauge()
hero = Player(0, screen_size[1] - 150, t="hero")
player_group = pygame.sprite.Group()
player_group.add(hero)

peloton = pygame.sprite.Group()
for i in range(10):
    conc = Player(-random.randint(100, 300), screen_size[1] - 150 - i)
    peloton.add(conc)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    display.blit(pygame.transform.scale(background, screen_size), (0, 0))

    inst_power = get_power()

    power.hp = inst_power
    power.draw(display)
    hero.power = inst_power

    player_group.draw(display)
    player_group.update()

    peloton.draw(display)
    for i in peloton:
        if inst_power > 0:
            i.update_power(inst_power + random.randint(-150, 150))
        else:
            i.update_power(inst_power)
    peloton.update()

    pygame.display.update()
    clock.tick(10)

pygame.quit()
