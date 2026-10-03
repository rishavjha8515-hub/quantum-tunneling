import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 999,448
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
        self.charge_speed = 0.26 ## I am making it all about myself,but 26 is special because it is between a perfect square and perfect cube + my birthday
        self.barrier_height = random.uniform(0.5,2.0)
        self.observed_this_charge = False

    def update(self, dt, observing):
        if self.state == "CHARGING":
            self.charge = min(1.0, self.charge + dt * self.charge_speed)
            if observing:
                self.observed_this_charge = True
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.swirl_angle += dt * (7 + self.charge * 10)

    def start_charging(self):
        self.state = "CHARGING"
        self.observed_this_charge = False

    def stop_charging(self):
        success = False
        if self.state == "CHARGING":
            if self.observed_this_charge:
                success = False
                self.flash_color = (210,210,225)
            else:
                success = random.random() < self.probability()
                self.flash_color = (53,99,57) if success else (200,60,70)
            self.flash_timer = 0.5
            if success:
                self.flash_color = (53, 99, 57)
            else:
                self.flash_color = (200, 60, 70)
        self.state = "IDLE"
        self.charge = 0.0
        self.charge_speed = random.uniform(0.15,2.25)
        self.barrier_height = random.uniform(0.5,2.0)
        return success

    def draw(self, surf, camera_x):
        rect = pygame.Rect(self.x - camera_x - self.width_px // 2, HEIGHT * 0.26, self.width_px, HEIGHT * 0.54)
        cold = (96, 200, 246)
        hot = (255, 99, 68)
        color = (
            int(cold[0] + (hot[0] - cold[0]) * self.charge),
            int(cold[1] + (hot[1] - cold[1]) * self.charge),
            int(cold[2] + (hot[2] - cold[2]) * self.charge)
        )
        if self.observed_this_charge:
            color = (190,190,205)
        if self.flash_timer > 0:
            color = self.flash_color
        pygame.draw.rect(surf, (color), rect, border_radius=6)

        num_dots = 7
        for i in range(num_dots):
            dot_angle = self.swirl_angle + (i / num_dots) * math.tau
            orbit_x = self.x - camera_x + math.cos(dot_angle) * 30
            orbit_y = HEIGHT * 0.55 + math.sin(dot_angle) * 30
            pygame.draw.circle(surf, (255, 255, 255), (int(orbit_x), int(orbit_y)), 4)

    def probability(self):
        width_units = self.width_px /30
        energy = self.charge * 1.4
        deficit = max(0.001, self.barrier_height - energy)
        T = math.exp(-2 * width_units * math.sqrt(deficit))
        return max(0.02, min(0.98, T))

NUM_BARRIERS = 5
barriers = []
for i in range(NUM_BARRIERS):
    x = 440 + i * 220
    width = random.uniform(40, 140)
    barriers.append(Barrier(x=x, width_px=width))
## No need to experiment with width,as randomized barriers will generate barriers of different width giving different baseline proabability.

WORLD_END = barriers[-1].x + 325

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
        self.x = max(20, min(WORLD_END, self.x))
        if self.stretch_timer > 0:
            self.stretch_timer -= dt

    def draw(self, surf, camera_x):
        w = self.radius * 2
        h = self.radius * 2
        if self.stretch_timer > 0:
            w = self.radius * 2 * 1.6

        left = self.x - camera_x - w / 2
        top = self.y - h / 2
        pygame.draw.ellipse(surf, (230, 230, 240), (left, top, w, h))

player = Player(x=120, y=HEIGHT * 0.6)

running = True
was_near = False
near_barrier = False
shake = 0.0
time_left = random.uniform(19.0, 43.0)
score = 0
game_over = False
camera_x = 0.0
streak = 0
best_streak = 0

def reset_game():
    global time_left, score, game_over, player, streak
    time_left = random.uniform(19.0, 43.0)
    score = 0
    streak = 0
    game_over = False
    player.x = 120
    player.y = HEIGHT * 0.6


while running:
    dt = clock.tick(60)/ 1000.0

    if not game_over:
        time_left -= dt
        if time_left <= 0:
            time_left = 0
            game_over = True

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
             if active_barrier and not game_over:
                 active_barrier.start_charging()
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if active_barrier and not game_over and active_barrier.stop_charging():
                if player.x < active_barrier.x:
                    player.x = active_barrier.x + active_barrier.width_px / 2 + player.radius + 5
                else:
                    player.x = active_barrier.x - active_barrier.width_px / 2 - player.radius - 5
                score += 1
                streak += 1 ##I ain't giving 26 days bonus steak just because it is my fav number
                best_streak = max(best_streak, streak)
                score += streak - 1
            else:
                shake = 0.26 ##Is there better number than my birthday?
                streak = 0
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p: ##Instead of going with english restart starting with R, i went with hindi
                    if game_over:
                        reset_game()
                     
    keys = pygame.key.get_pressed()
    player.update(dt, keys)

    observing = keys[pygame.K_o]
    camera_x = player.x - WIDTH / 2
    camera_x = max(0, camera_x)
    camera_x = min(camera_x, WORLD_END - WIDTH)
    for b in barriers:
        b.update(dt, observing)

    shake_x, shake_y = 0,0
    if shake > 0:
            shake -= dt
            shake_x = random.randint(-6, 6)
            shake_y = random.randint(-8, 8)

    screen.fill((12, 14, 26))
    for b in barriers:
        b.x += shake_x
        b.draw(screen, camera_x)
        b.x -= shake_x
    player.x += shake_x
    player.draw(screen, camera_x)
    player.x -= shake_x

    if active_barrier:
        text = font.render(f"charge: {active_barrier.charge:.2f}", True, (220, 220, 230))
        screen.blit(text, (16,16))
        if active_barrier.observed_this_charge:
            ptext = font.render(f"P(tunnel): {active_barrier.probability()*100:.0f}% (OBSERVED - locked)", True, (255, 190, 205))
        else:
            ptext = font.render(f"P(tunnel): ??? Hold o to observe (locks this attempt)", True, (159,124,222))
        screen.blit(ptext, (16, 40))

    timer_text = font.render(f"time: {time_left:.1f} score: {score} streak: {streak} best: {best_streak}", True, (142, 255, 125))
    screen.blit(timer_text, (WIDTH - 373, 16))
        
    if game_over:    
            over_text = font.render(f"Sorry, Time is always limited ! - final score: {score} (press P to restart)", True, (255, 0, 255)) ##I had to replace yellow with hot magenta pink because of visibilty issue,i tried bright yell,green and then the current color
            screen.blit(over_text, (WIDTH // 2 - 347, HEIGHT // 2))

    if camera_x >= WORLD_END - WIDTH:
            end_text = font.render("THIS IS THE END!", True, (255, 0, 0))
            screen.blit(end_text, (WIDTH // 2 - 98, HEIGHT - 224)) ##I changed all colors from plain to vibrant colors
    pygame.display.flip()

pygame.quit()