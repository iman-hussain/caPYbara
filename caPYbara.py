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
EJECTED_CAPYBARA_SIZE = (45, 45)  # Base size of the ejected capybaras
SCORES_FILE = 'scores.csv'

# Setup the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Capybara Evasion")

# Load the capybara image
capybara_img = pygame.image.load(CAPYBARA_IMAGE)
capybara_rect = capybara_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

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
        # If the file doesn't exist, create it
        with open(SCORES_FILE, mode='w', newline='') as file:
            pass  # Just create an empty file
    return scores

# Save score to CSV
def save_score(score):
    with open(SCORES_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

# Function to spawn a new capybara at the center with a random size
def spawn_capybara():
    # Determine a random scale factor between 1 and 2
    scale_factor = random.uniform(1, 2)
    
    # Calculate the new size
    new_size = (int(EJECTED_CAPYBARA_SIZE[0] * scale_factor), int(EJECTED_CAPYBARA_SIZE[1] * scale_factor))
    
    # Scale the capybara image
    new_capybara_img = pygame.transform.scale(capybara_img, new_size)
    new_capybara_rect = new_capybara_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Determine random direction and speed
    direction = random.uniform(0, 2 * math.pi)
    speed = random.uniform(2, 5)
    
    return {
        "rect": new_capybara_rect.copy(),
        "image": new_capybara_img,
        "direction": direction,
        "speed": speed
    }

# Function to display the game over screen and the scores
def show_game_over_screen(score):
    screen.fill(BACKGROUND_COLOR)
    font = pygame.font.Font(None, 74)
    text = font.render(f'Game Over! Score: {score} ms', True, (0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))

    font = pygame.font.Font(None, 50)
    play_again_text = font.render('Press R to Play Again or Q to Quit', True, (0, 0, 0))
    screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2))

    # Load and display previous scores
    scores = load_scores()
    font = pygame.font.Font(None, 36)
    y_offset = HEIGHT // 2 + 100
    for score, timestamp in scores[-5:]:  # Display the last 5 scores
        score_text = font.render(f'Score: {score} ms | Date: {timestamp}', True, (0, 0, 0))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y_offset))
        y_offset += 40

    pygame.display.flip()

# List to hold ejected capybaras
ejected_capybaras = []

# Load previous scores
scores = load_scores()

# Main game loop
clock = pygame.time.Clock()
running = True
game_over = False
initial_spawn_rate = 1  # Starting spawn rate (1 spawn per second)
spawn_rate_multiplier = 2  # Rate of increase in spawn rate
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
        # Calculate the elapsed time in milliseconds
        elapsed_time = time.time() - start_time
        
        # Calculate rotation speed: starts slowly and increases exponentially
        # Time in seconds for exponential growth (e.g., 15 seconds)
        time_to_infinite_speed = 15
        max_rotation_speed = 360 * FPS  # High rotation speed (360 degrees per second)
        rotation_speed = max_rotation_speed * (elapsed_time / time_to_infinite_speed) ** 2
        
        # Update the angle by adding the current rotation speed
        angle += rotation_speed / FPS  # Update angle based on FPS
        angle %= 360  # Keep angle within 0-360 degrees
        
        # Rotate the capybara image and get the new rect
        rotated_capybara_img = pygame.transform.rotate(capybara_img, angle)
        rotated_capybara_rect = rotated_capybara_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(rotated_capybara_img, rotated_capybara_rect)

        # Move and draw ejected capybaras
        for capybara in ejected_capybaras:
            capybara["rect"].x += capybara["speed"] * math.cos(capybara["direction"])
            capybara["rect"].y += capybara["speed"] * math.sin(capybara["direction"])
            screen.blit(capybara["image"], capybara["rect"])

        # Calculate spawn rate: start with 1 spawn per second, then double every second
        elapsed_seconds = int(time.time() - start_time)
        spawn_rate = initial_spawn_rate * (spawn_rate_multiplier ** elapsed_seconds)

        # Spawn a new capybara based on the spawn rate
        if random.random() < spawn_rate / FPS:  # Convert spawns per second to per frame
            ejected_capybaras.append(spawn_capybara())
        
        # Check for collisions with the mouse
        mouse_pos = pygame.mouse.get_pos()
        for capybara in ejected_capybaras:
            if capybara["rect"].collidepoint(mouse_pos):
                game_over = True
                show_game_over_screen(int(elapsed_time * 1000))
                save_score(int(elapsed_time * 1000))

        # Draw the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {int(elapsed_time * 1000)} ms', True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # Draw the mute button
        mute_text = font.render('Mute (M)', True, (0, 0, 0))
        screen.blit(mute_text, (WIDTH - mute_text.get_width() - 10, 10))
    else:
        # When the game is over, keep showing the game over screen
        show_game_over_screen(int(elapsed_time * 1000))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
