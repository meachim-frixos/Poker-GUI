import pygame
import sys

pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Circle Surface")

# Define the radius of the circle
circle_radius = 100

# Create a surface for the circle
circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)

# Draw the circle on the surface
pygame.draw.circle(circle_surface, (255, 0, 0), (circle_radius, circle_radius), circle_radius)

# Main loop
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    # Blit the circle surface onto the screen
    screen.blit(circle_surface, (screen_width // 2 - circle_radius, screen_height // 2 - circle_radius))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
