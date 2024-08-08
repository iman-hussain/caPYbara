import pygame
import random
import sys
import math
import time
import csv
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
CAPYBARA_IMAGE = 'capybara.png'
MUSIC_FILE = 'music.mp3'
FPS = 60
EJECTED_CAPYBARA_SIZE = (45, 45)  # Size of the ejected capybaras
SCORES_FILE = 'scores.csv'

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Capybara Evasion")

# Load the capybara image
capybara_img = pygame.image.load(CAPYBARA_IMAGE)
capybara_rect = capybara_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Create a smaller capybara image for the ejected capybaras
small_capybara_img = pygame.transform.scale(capybara_img, EJECTED_CAPYBARA_SIZE)
small_capybara_rect = small_capybara_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Load and play background music
pygame.mixer.music.load(MUSIC_FILE)
pygame.mixer.music.play(-1)

# Mute button state
is_muted = False

# Load scores from CSV
def load_scores():
    scores = []
    try:
        with open(SCORES_FILE, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                scores.append((row[0], row[1]))
    except FileNotFoundError:
        pass
    return scores

# Save score to CSV
def save_score(score):
    with open(SCORES_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

# Function to spawn a new capybara at the center
def spawn_capybara():
    direction = random.uniform(0, 2 * math.pi)
    speed = random.uniform(2, 5)
    return {
        "rect": small_capybara_rect.copy(),
        "direction": direction,
        "speed": speed
    }

# Function to display the game over screen
def show_game_over_screen(score):
    screen.fill(BACKGROUND_COLOR)
    font = pygame.font.Font(None, 74)
    text = font.render(f'Game Over! Score: {score}', True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))

    font = pygame.font.Font(None, 50)
    play_again_text = font.render('Press R to Play Again or Q to Quit', True, (0, 0, 0))
    screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()

# List to hold ejected capybaras
ejected_capybaras = []

# Load previous scores
scores = load_scores()

# Main game loop
clock = pygame.time.Clock()
running = True
game_over = False
initial_spawn_rate = 0.02
spawn_rate = initial_spawn_rate
start_time = time.time()
angle = 0

while running:
    screen.fill(BACKGROUND_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    ejected_capybaras = []
                    spawn_rate = initial_spawn_rate
                    start_time = time.time()
                    game_over = False
                elif event.key == pygame.K_q:
                    running = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    is_muted = not is_muted
                    if is_muted:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

    if not game_over:
        # Draw and rotate the central capybara
        elapsed_time = time.time() - start_time
        angle += spawn_rate * 10
        rotated_capybara_img = pygame.transform.rotate(capybara_img, angle)
        rotated_capybara_rect = rotated_capybara_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(rotated_capybara_img, rotated_capybara_rect)

        # Move and draw ejected capybaras
        for capybara in ejected_capybaras:
            capybara["rect"].x += capybara["speed"] * math.cos(capybara["direction"])
            capybara["rect"].y += capybara["speed"] * math.sin(capybara["direction"])
            screen.blit(small_capybara_img, capybara["rect"])

        # Spawn a new capybara with increasing difficulty
        if random.random() < spawn_rate:
            ejected_capybaras.append(spawn_capybara())
        
        # Exponentially increase spawn rate over time
        spawn_rate = initial_spawn_rate * (2 ** elapsed_time)

        # Check for collisions with the mouse
        mouse_pos = pygame.mouse.get_pos()
        for capybara in ejected_capybaras:
            if capybara["rect"].collidepoint(mouse_pos):
                game_over = True
                show_game_over_screen(int(elapsed_time))
                save_score(int(elapsed_time))

        # Draw the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {int(elapsed_time)}', True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Draw the mute button
        mute_text = font.render('Mute (M)', True, (0, 0, 0))
        screen.blit(mute_text, (WIDTH - mute_text.get_width() - 10, 10))
    else:
        # When the game is over, keep showing the game over screen
        show_game_over_screen(int(elapsed_time))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
