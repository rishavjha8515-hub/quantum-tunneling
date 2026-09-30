import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 808,448
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOREMON'S QUANTUM TUNNEL")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 19)

class Barrier:
    def __init__(self, x, width_px):
        self.x = x
        self.width_px = width_px
        self.state = "IDLE"
        self.charge = 0.0
        self.flash_timer = 0.0
        self.flash_color = (255,255,255)
        self.swirl_angle = 0.0

    def update(self, dt):
        if self.state == "CHARGING":
            self.charge = min(1.0, self.charge + dt * 0.7)
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.swirl_angle += dt * (7 + self.charge * 10)

    def start_charging(self):
        self.state = "CHARGING"

    def stop_charging(self):
        success = False
        if self.state == "CHARGING":
            success = random.random() < self.probability()
            self.flash_timer = 0.5
            if success:
                self.flash_color = (53, 99, 57)
            else:
                self.flash_color = (200, 60, 70)
        self.state = "IDLE"
        self.charge = 0.0
        return success

    def draw(self, surf):
        rect = pygame.Rect(self.x - self.width_px // 2, HEIGHT * 0.26, self.width_px, HEIGHT * 0.54)
        cold = (96, 200, 246)
        hot = (255, 99, 68)
        color = (
            int(cold[0] + (hot[0] - cold[0]) * self.charge),
            int(cold[1] + (hot[1] - cold[1]) * self.charge),
            int(cold[2] + (hot[2] - cold[2]) * self.charge)
        )
        if self.flash_timer > 0:
            color = self.flash_color
        pygame.draw.rect(surf, (color), rect, border_radius=6)

        num_dots = 7
        for i in range(num_dots):
            dot_angle = self.swirl_angle + (i / num_dots) * math.tau
            orbit_x = self.x + math.cos(dot_angle) * 30
            orbit_y = HEIGHT * 0.55 + math.sin(dot_angle) * 30
            pygame.draw.circle(surf, (255, 255, 255), (int(orbit_x), int(orbit_y)), 4)

    def probability(self):
        width_units = self.width_px /30
        energy = self.charge * 1.4
        deficit = max(0.001, 1.0 - energy)
        T = math.exp(-2 * width_units * math.sqrt(deficit))
        return max(0.02, min(0.98, T))

barrier1 = Barrier(x=456, width_px=48)
barrier2 = Barrier(x=664, width_px=96)#Took 560 as midpoint to change x for both and changed width values to make new barrier 2x of earlier
barriers = [barrier1, barrier2]
## I would suggest to experiment with width here, as it changes the baseline proability.

class Player:
    def __init__(self, x, y):
     self.x = x
     self.y = y
     self.speed = 225
     self.radius = 16
     self.stretch_timer = 0.0


    def update(self, dt, keys):
        if keys[pygame.K_LEFT]:
             self.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
             self.x += self.speed * dt
        if self.stretch_timer > 0:
            self.stretch_timer -= dt

    def draw(self, surf):
        w = self.radius * 2
        h = self.radius * 2
        if self.stretch_timer > 0:
            w = self.radius * 2 * 1.6

        left = self.x - w / 2
        top = self.y - h / 2
        pygame.draw.ellipse(surf, (230, 230, 240), (left, top, w, h))

player = Player(x=120, y=HEIGHT * 0.6)

running = True
was_near = False
near_barrier = False
shake = 0.0

while running:
    dt = clock.tick(60)/ 1000.0

    active_barrier = None
    near_barrier = False
    for b in barriers:
        if abs(player.x - b.x) < 96: ## it is based on how close you need to stand to interactions,it doesn't affects tunnel proability ,only whether you can charge yet.
            active_barrier = b
            break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
             if active_barrier:
                 active_barrier.start_charging()
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if active_barrier:
                success = active_barrier.start_charging()
            if active_barrier and active_barrier.stop_charging():
                if player.x < active_barrier.x:
                    player.x = active_barrier.x + active_barrier.width_px / 2 + player.radius + 5
                else:
                    player.x = active_barrier.x - active_barrier.width_px / 2 - player.radius - 5
            else:
                shake = 0.26 ##Is a better number than my birthday?

    keys = pygame.key.get_pressed()
    player.update(dt, keys)
    for b in barriers:
        b.update(dt)

    shake_x, shake_y = 0,0
    if shake > 0:
            shake -= dt
            shake_x = random.randint(-6, 6)
            shake_y = random.randint(-8, 8)

    screen.fill((12, 14, 26))
    for b in barriers:
        b.x += shake_x
        b.draw(screen)
        b.x -= shake_x
    player.x += shake_x
    player.draw(screen)
    player.x -= shake_x

    if active_barrier:
        text = font.render(f"charge: {active_barrier.charge:.2f}", True, (220, 220, 230))
        screen.blit(text, (16,16))
        ptext = font.render(f"P(tunnel): {active_barrier.probability()*100:.0f}%", True, (220, 220, 230))
        screen.blit(ptext, (16, 40))
    pygame.display.flip()

pygame.quit()