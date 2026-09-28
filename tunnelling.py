import pygame
import math

pygame.init()

WIDTH, HEIGHT = 783,448
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

    def update(self, dt):
        if self.state == "CHARGING":
            self.charge = min(1.0, self.charge + dt * 0.7)

    def start_charging(self):
        self.state = "CHARGING"

    def stop_charging(self):
        self.state = "IDLE"
        self.charge = 0.0

    def draw(self, surf):
        rect = pygame.Rect(self.x - self.width_px // 2, HEIGHT * 0.26, self.width_px, HEIGHT * 0.54)
        cold = (96, 200, 246)
        hot = (255, 99, 68)
        color = (
            int(cold[0] + (hot[0] - cold[0]) * self.charge),
            int(cold[1] + (hot[1] - cold[1]) * self.charge),
            int(cold[2] + (hot[2] - cold[2]) * self.charge)
        )
        pygame.draw.rect(surf, (color), rect, border_radius=6)

    def probability(self):
        width_units = self.width_px /30
        energy = self.charge * 1.4
        deficit = max(0.001, 1.0 - energy)
        T = math.exp(-2 * width_units * math.sqrt(deficit))
        return _____

barrier = Barrier(x=450, width_px=40)

class Player:
    def __init__(self, x, y):
     self.x = x
     self.y = y
     self.speed = 225
     self.radius = 16

    def update(self, dt, keys):
        if keys[pygame.K_LEFT]:
             self.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
             self.x += self.speed * dt

    def draw(self, surf):
        pygame.draw.circle(surf, (230,230, 240), (int(self.x), int(self.y)), self.radius)   

player = Player(x=120, y=HEIGHT * 0.6)

running = True
was_near = False
near_barrier = False

while running:
    dt = clock.tick(60)/ 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if near_barrier:
                barrier.start_charging()
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            barrier.stop_charging()

    keys = pygame.key.get_pressed()
    player.update(dt, keys)
    barrier.update(dt)

    near_barrier = abs(player.x - barrier.x) < 60
    if near_barrier != was_near:
        print("near_barrier:", near_barrier)
        was_near = near_barrier

        print(barrier.state)
    
    screen.fill((12, 14, 26))
    barrier.draw(screen)
    player.draw(screen)
    text = font.render(f"charge: {barrier.charge:.2f}", True, (220, 220, 230))
    screen.blit(text, (16,16))
    pygame.display.flip()

pygame.quit()