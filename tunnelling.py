import pygame
import math
import random
import numpy as np
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 999,448
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOREMON'S QUANTUM TUNNEL")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 19)

def make_tone(freq, duration, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    wave = np.sin(freq * t * 2 * np.pi)
    audio = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

def make_sweep(freq_start, freq_end, duration, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration )
    t = np.linspace(0, duration, n_samples, False)
    freq = np.linspace(freq_start, freq_end, n_samples)
    wave = np.sin(2 * np.pi * freq * t)
    audio = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

sound_charge_start = make_tone(220, 0.08)
sound_success = make_sweep(220, 1100, 0.25)
sound_fail = make_sweep(300, 80, 0.3)
sound_observed = make_tone(330, 0.3, 0.2)
sound_decohere = make_sweep(700, 60, 0.45)

DECOHERENCE_TIME = 1.2 ##I was thinking of something unique and ended up at my research again
FALLBACK_TRIVIA = {"q": "A thicker barrier makes tunnelling....", "options": ["easier", "harder", "unchanged"], "answer": 0}
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
        self.hold_at_max = 0.0
        self.partner = None
        self.entangle_bonus = 0.0
        self.forced = None
        self.stored = 0.0
        self.echo = 0.0
        self.link_type = "same"
        self.trivia_energy = 0.0

    def update(self, dt, observing):
        decohered_now = False
        if self.state == "CHARGING":
            self.charge = min(1.0, self.charge + dt * self.charge_speed)
            if observing:
                self.observed_this_charge = True
            if self.charge >= 1.0:
                self.hold_at_max += dt
                if self.hold_at_max >= DECOHERENCE_TIME:
                    self.state = "IDLE"
                    self.charge = 0.0
                    self.hold_at_max = 0.0
                    self.flash_color = (170, 60, 255)
                    self.flash_timer = 0.6
                    self.charge_speed = random.uniform(0.15, 2.25)
                    self.barrier_height = random.uniform(0.5, 2.0)
                    decohered_now = True
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.swirl_angle += dt * (7 + self.charge * 10)
        return decohered_now

    def start_charging(self):
        self.state = "CHARGING"
        self.observed_this_charge = False
        self.hold_at_max = 0.0
        self.charge = self.stored
        self.stored = 0.0

    def stop_charging(self):
        success = False
        if self.state == "CHARGING":
            if self.observed_this_charge:
                self.flash_color = (210,210,225)
            else:
                success = random.random() < self.probability()
                self.flash_color = (53,99,57) if success else (200,60,70)
                if self.partner:
                    self.partner.stored = self.charge if self.link_type == "same" else 1.0 - self.charge
                    self.partner.flash_timer = 0.5
                    self.partner.flash_color = (150, 100, 255) if self.link_type == "same" else (255, 100, 150) 
                self.forced = None
            self.flash_timer = 0.5
        self.state = "IDLE"
        self.charge = 0.0
        self.hold_at_max = 0.0
        self.charge_speed = random.uniform(0.15,2.25)
        self.barrier_height = random.uniform(0.5,2.0)
        self.forced = None
        self.trivia_energy = 0.0
        return success

    def draw(self, surf, camera_x):
        rect = pygame.Rect(self.x - camera_x - self.width_px // 2, HEIGHT * 0.26, self.width_px, HEIGHT * 0.54)
        cold = (96, 200, 246)
        hot = (255, 99, 68)
        level = max(self.charge, self.echo, self.stored)
        color = (
            int(cold[0] + (hot[0] - cold[0]) * level ),
            int(cold[1] + (hot[1] - cold[1]) * level ),
            int(cold[2] + (hot[2] - cold[2]) * level )
        )
        if self.state == "CHARGING" and self.hold_at_max > 0:
            t = min(1.0, self.hold_at_max / DECOHERENCE_TIME)
            purple = (170, 60, 255)
            color = tuple(int(color[i] + (purple[i] - color[i]) * t) for i in range(3))
        if self.forced is True:
            color = (80, 230, 140)
        elif self.forced is False:
            color =(70, 70, 85)
        if self.observed_this_charge:
            color = (190,190,205)
        if self.flash_timer > 0:
            color = self.flash_color
        if self.partner and self.x < self.partner.x:
            link = (150, 100, 255) if self.link_type == "same" else (255, 170, 60)
            if self.forced is True or self.partner.forced is True:
                link = (80, 220, 120)
            elif self.forced is False or self.partner.forced is False:
                link = (255, 90, 90)
            pygame.draw.line(surf, link, (self.x - camera_x, HEIGHT * 0.53), (self.partner.x - camera_x, HEIGHT * 0.53), 3)
        pygame.draw.rect(surf, (color), rect, border_radius=6)

        num_dots = 7
        for i in range(num_dots):
            dot_angle = self.swirl_angle + (i / num_dots) * math.tau
            orbit_x = self.x - camera_x + math.cos(dot_angle) * 30
            orbit_y = HEIGHT * 0.55 + math.sin(dot_angle) * 30
            pygame.draw.circle(surf, (255, 255, 255), (int(orbit_x), int(orbit_y)), 4)

    def probability(self):
        if self.forced is not None:
            return 1.0 if self.forced else 0.0
        width_units = self.width_px /30
        energy = self.charge * 1.4 + self.trivia_energy
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

def pair_barriers():
    for b in barriers: 
        b.partner = None
        b.forced = None
        b.stored = 0.0
        b.echo = 0.0
        b.state = "IDLE"
        b.charge = 0.0
        b.hold_at_max = 0.0
        b.observed_this_charge = False
        b.trivia_energy = 0.0
    order = barriers[:]
    random.shuffle(order)
    for k in range(0, len(order) -1, 2):
        order[k].partner = order[k + 1]
        order[k+1].partner = order[k]
        kind = random.choice(["same", "inverse"])
        order[k].link_type = kind
        order[k + 1].link_type = kind


pair_barriers() ##I wrote earlier,connecting like barrier[0] with barrier[1] but then I rewrote it to add fun
WORLD_END = barriers[-1].x + 325

class Player:
    def __init__(self, x, y):
     self.x = x
     self.y = y
     self.speed = 225
     self.radius = 16
     self.stretch_timer = 0.0

    def update(self, dt, keys):
        old_x = self.x
        if keys[pygame.K_LEFT]:
             self.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
             self.x += self.speed * dt
        for b in barriers:
            half = b.width_px / 2 + self.radius
            if old_x <= b.x:
                self.x = min(self.x, b.x - half)
            else:
                self.x = max(self.x, b.x + half)
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

class QuantumGhost:
    def __init__(self):
        self.active = False
        self.x = 0.0
        self.timer = 0.0
        self.spawn_timer = random.uniform(10.0, 18.0)
        self.touched = set()
        self.phase = 0.0

    def update(self, dt, player):
        self.phase += dt * 5
        if not self.active:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.active = True
                side = random.choice([-1, 1])
                self.x = max(20, min(WORLD_END, player.x + side * 350))
                self.timer = 5.0
                self.touched.clear()
            return

        self.timer -= dt
        self.x += (player.x - self.x) * min(1.0, dt * 1.5)
        for b in barriers:
            if b.partner and b not in self.touched:
                if abs(self.x - b.x) < b.width_px/ 2 + 41:
                    b.partner.stored = min(1.0, b.partner.stored + 0.25)
                    b.partner.flash_timer = 0.5
                    b.partner.flash_color = (100, 210, 255)
                    self.touched.add(b)
                    self.touched.add(b.partner)
        if self.timer <= 0:
            self.active = False
            self.spawn_timer = random.uniform(10.0, 18.0)

    def draw(self, surf, camera_x, player_y):
        if not self.active:
            return
        gx = int(self.x - camera_x)
        gy = int(player_y + math.sin(self.phase) * 12)
        pygame.draw.circle(surf, (102, 222, 255), (gx, gy), 23, 2)
        pygame.draw.circle(surf, (162, 100, 255), (gx, gy), 15, 2)
        pygame.draw.circle(surf, (222, 100, 255), (gx, gy), 5)
player = Player(x=120, y=HEIGHT * 0.6)
ghost = QuantumGhost()
 
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
game_started = False
title_timer = 0.0
CHECK_TIME = 1.8
trivia = FALLBACK_TRIVIA
trivia_barrier = random.choice(barriers)
trivia_state = "waiting" if GROQ_API_KEY else "off"

def reset_game():
    global time_left, score, game_over, player, streak, trivia_state, trivia_barrier
    time_left = random.uniform(19.0, 43.0)
    score = 0
    streak = 0
    game_over = False
    player.x = 120
    player.y = HEIGHT * 0.6 
    trivia_state = "waiting" if GROQ_API_KEY else "off"
    trivia_barrier = random.choice(barriers)
    ghost.active = False
    ghost.spawn_timer = random.uniform(10.0, 18.0)

while running:
    dt = clock.tick(53)/ 1000.0

    if game_started and not game_over:
        time_left -= dt
        if time_left <= 0:
            time_left = 0
            game_over = True

    active_barrier = None
    near_barrier = False
    for b in barriers:
        if abs(player.x - b.x) < b.width_px / 2 + player.radius + 30: ## it is based on how close you need to stand to interactions,it doesn't affects tunnel proability ,only whether you can charge yet.
            active_barrier = b
            break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_started and title_timer >= CHECK_TIME:
            game_started = True
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_1, pygame.K_2, pygame.K_3) and trivia_state == "asking":
            correct = (event.key - pygame.K_1) == trivia[ "answer" ]
            trivia_barrier.trivia_energy = 0.4 if correct else -0.4
            trivia_state = "done"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
             if active_barrier and not game_over:
                 active_barrier.start_charging()
                 sound_charge_start.play()
                 if active_barrier is trivia_barrier and trivia_state == "waiting":
                    trivia_state = "asking"
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if active_barrier and not game_over and active_barrier.state == "CHARGING":
                was_observed = active_barrier.observed_this_charge
                if active_barrier.stop_charging():
                    if player.x < active_barrier.x:
                        player.x = active_barrier.x + active_barrier.width_px / 2 + player.radius + 5
                    else:
                        player.x = active_barrier.x - active_barrier.width_px / 2 - player.radius - 5
                    score += 1
                    streak += 1 ##I ain't giving 26 days bonus steak just because it is my fav number
                    best_streak = max(best_streak, streak)
                    score += streak - 1
                    sound_success.play()
                else:
                    shake = 0.26 ##Is there better number than my birthday?
                    streak = 0
                    if was_observed:
                        sound_observed.play()
                    else:
                        sound_fail.play()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p: ##Instead of going with english restart starting with R, i went with hindi
                    if game_over:
                        reset_game()
                        pair_barriers()
                     
    keys = pygame.key.get_pressed()
    if game_started:
        player.update(dt, keys)
        if not game_over:
            ghost.update(dt, player)

    observing = keys[pygame.K_o]
    camera_x = player.x - WIDTH / 2
    camera_x = max(0, camera_x)
    camera_x = min(camera_x, WORLD_END - WIDTH)
    for b in barriers:
        b.echo = 0.0
    for b in barriers:
        if b.state == "CHARGING" and b.partner:
            b.partner.echo = b.charge if b.link_type == "same" else 1.0 - b.charge
    for b in barriers:
        if b.update(dt, observing):
            streak = 0
            shake = 0.4
            sound_decohere.play()

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
    ghost.draw(screen, camera_x, player.y)

    if not game_started:
         title_timer += dt
         title = font.render("DOREMON'S QUANTUM TUNNEL", True, (255,180, 60))
         screen.blit(title, (WIDTH // 2 - 180, HEIGHT // 2 - 80))
         c1 = font.render("Press left arrow to move left and right arrow to move right  SPACE hold to charge release to tunnel", True, (60, 180, 50))
         screen.blit(c1, (WIDTH // 2 - 486, HEIGHT // 2 - 40))
         c2 = font.render("Hold o while charging to OBSERVE - reveals odds but guarantees failure", True, (80, 45, 140))
         screen.blit(c2, (WIDTH // 2 -270, HEIGHT // 2 - 16))
         if title_timer < CHECK_TIME:
            dots = "." * (int(title_timer * 4) % 4)
            c4 = font.render("Checking for trivia key" + dots, True, (78, 92, 190))
            screen.blit(c4, (WIDTH // 2 - 130, HEIGHT // 2 + 10))
         else:
            if GROQ_API_KEY:
                c4 = font.render("KEY FOUND! - you will get one trivia question to impact your score", True, (120, 255, 90))
            else:
                c4 = font.render("NO KEY FOUND - no problem,you can continue without trivia", True, (90, 255, 120))
            screen.blit(c4, (WIDTH // 2 - c4.get_width() // 2, HEIGHT // 2 ))
         c3 = font.render("Press any key to begin", True, (220, 220, 230))
         screen.blit(c3, (WIDTH // 2 - 100, HEIGHT // 2 + 30))
         pygame.display.flip()
         continue 

    if active_barrier:
        text = font.render(f"charge: {active_barrier.charge:.2f}", True, (220, 220, 230))
        screen.blit(text, (16,16))
        if active_barrier.observed_this_charge:
            ptext = font.render(f"P(tunnel): {active_barrier.probability()*100:.0f}% (OBSERVED - locked)", True, (255, 190, 205))
        else:
            ptext = font.render(f"P(tunnel): ??? Hold o to observe (locks this attempt)", True, (159,124,222))
        screen.blit(ptext, (16, 40))
        if active_barrier.hold_at_max > 0:
            left = DECOHERENCE_TIME - active_barrier.hold_at_max
            warn = font.render(f"DECOHERING in {left:.1f}s - release!", True, (200, 90, 255))
            screen.blit(warn, (16, 64))
        if active_barrier.stored > 0:
            msg = f"ENTANGLED: inherited {active_barrier.stored:.2f} charge"
            screen.blit(font.render(msg, True, (120, 255, 200)), (16,88))
        if active_barrier.partner:
            kind = "mirror" if active_barrier.link_type == "same" else "inverse"
            col = (150, 100, 255) if kind == "mirror" else (255, 170, 60)
            screen.blit(font.render(f"linked: {kind}", True, col), (16, 112))
        if active_barrier.trivia_energy != 0:
            msg = "TRIVIA: correct, boosted!" if active_barrier.trivia_energy > 0 else "TRIVIA: wrong, weakened!"
            screen.blit(font.render(msg, True, (255, 221, 123)), (16,136))
    if trivia_state == "asking":
        screen.blit(font.render(trivia["q"], True, (255, 220, 120)), (16, 170))
        for i, opt in enumerate(trivia["options"]):
            screen.blit(font.render(f"{i + 1}: {opt}", True, (255, 220, 120)), (16, 194 + i * 22))

    timer_text = font.render(f"time: {time_left:.1f} score: {score} streak: {streak} best: {best_streak}", True, (142, 255, 125))
    screen.blit(timer_text, (WIDTH - 373, 16))
        
    if game_over:    
            over_text = font.render(f"Sorry, Time is always limited ! - final score: {score} (press P to restart)", True, (255, 0, 255)) ##I had to replace yellow with hot magenta pink because of visibilty issue,i tried bright yell,green and then the current color
            screen.blit(over_text, (WIDTH // 2 - 347, HEIGHT // 2))

    if camera_x >= WORLD_END - WIDTH:
            end_text = font.render("THIS IS THE END!", True, (255, 0, 0))
            screen.blit(end_text, (WIDTH // 2 - 98, HEIGHT - 195)) ##I changed all colors from plain to vibrant colors
    pygame.display.flip()

pygame.quit()