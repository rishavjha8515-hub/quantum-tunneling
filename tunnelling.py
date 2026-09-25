import pygame

pygame.init()

WIDTH, HEIGHT = 783,448
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOREMON'S QUANTUM TUNNEL")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 19)

running = True
while running:
    dt = clock.tick(60)/ 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((12, 14, 26))
    pygame.display.flip()

pygame.quit()