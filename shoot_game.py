import pygame
import random
import time
import pyodbc

#def start_game(username, high_score):
# Initialize Pygame
pygame.init()

# Declaration
username = ''
high_score = ''

# Screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game settings
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# Database connection using Windows Authentication
def connect_to_db():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=localhost;'
                              'DATABASE=GameDB;'
                              'Trusted_Connection=yes;')
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Save player data (username, password, high_score) to the database
def save_player_data(username, password, high_score):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM PlayerData WHERE username = ?", username)
    existing_player = cursor.fetchone()
    
    if existing_player:
        cursor.close()
        conn.close()
        return False  # Username already exists
    else:
        # Insert new player data
        cursor.execute("""
            INSERT INTO PlayerData (username, password, high_score)
            VALUES (?, ?, ?)
        """, username, password, high_score)
    
    conn.commit()
    cursor.close()
    conn.close()
    return True  # Successfully saved new player data

# Retrieve player data for login (verify username and password)
def authenticate_user(username, password):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT high_score FROM PlayerData WHERE username = ? AND password = ?", username, password)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        global high_score
        high_score = result[0]  # Fetch the high score
        return True  # Successful login
    return False  # Failed login

# Update high score in the database
def update_high_score(username, high_score):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check the current high score in the database for the given username
    cursor.execute("SELECT high_score FROM PlayerData WHERE username = ?", username)
    result = cursor.fetchone()
    
    if result:
        current_high_score = result[0]
        if score > current_high_score:
            # Update the high score if the current one is higher
            cursor.execute("UPDATE PlayerData SET high_score = ? WHERE username = ?", high_score, username)
            conn.commit()
    
    cursor.close()
    conn.close()

# Load assets
BACKGROUND_IMAGE = pygame.image.load("assets/background3.jpg")
PLAYER_IMAGE = pygame.image.load("assets/player.png")
ENEMY_IMAGE = pygame.image.load("assets/enemy.png")
BULLET_IMAGE = pygame.image.load("assets/bullet1.png")
EXPLOSION_IMAGE = pygame.image.load("assets/explosion.png")
MUSIC = pygame.mixer.Sound("assets/music1.wav")
BULLET_SOUND = pygame.mixer.Sound("assets/bullet1.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("assets/explosion.wav")

# Game variables
score = 0
done = False
clock = pygame.time.Clock()
game_active = True  # Start the game directly
game_over = False
replay_cost = 100  # Initial replay cost

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("War Space")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMAGE
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x = PLAYER_SPEED
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        BULLET_SOUND.play()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = ENEMY_SPEED + random.uniform(-1, 1)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            global score
            score -= 1

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = BULLET_IMAGE
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = EXPLOSION_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.kill()

# Button class
class Button:
 def __init__(self, text, pos, font, bg_color=BLUE, text_color=WHITE):
     self.x, self.y = pos
     self.font = pygame.font.Font(None, font)
     self.bg_color = bg_color
     self.text_color = text_color
     self.change_text(text)
 def change_text(self, text):
     self.text = self.font.render(text, True, self.text_color)
     self.size = self.text.get_size()
     self.surface = pygame.Surface((self.size[0] + 20, self.size[1] + 20))
     self.surface.fill(self.bg_color)
     self.surface.blit(self.text, (10, 10))
     self.rect = self.surface.get_rect(center=(self.x, self.y))
 def show(self, screen):
     screen.blit(self.surface, self.rect.topleft)
 def click(self, event):
     if event.type == pygame.MOUSEBUTTONDOWN:
         if self.rect.collidepoint(event.pos):  # Only check position, no get_pressed()
             return True
     return False

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

def start_game():
 global all_sprites, high_score, enemies, bullets, player, score, game_over, game_active, replay_cost, username
 print(f"Welcome, {username}!")
 print(f"Your current high score is: {high_score}")
 all_sprites = pygame.sprite.Group()
 enemies = pygame.sprite.Group()
 bullets = pygame.sprite.Group()
 player = Player()
 all_sprites.add(player)
 
 for i in range(8):
     enemy = Enemy()
     all_sprites.add(enemy)
     enemies.add(enemy)
 
 score = 0
 replay_cost = 100
 game_over = False
 game_active = True  

# Play background music
MUSIC.play(-1)

# Add button areas
left_button = pygame.Rect(50, SCREEN_HEIGHT - 100, 100, 50)
right_button = pygame.Rect(200, SCREEN_HEIGHT - 100, 100, 50)
fire_button = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100, 100, 50)

# Draw buttons function (updated for transparent buttons)
def draw_buttons():
    font = pygame.font.Font(None, 36)
    left_text = font.render("Left", True, WHITE)
    right_text = font.render("Right", True, WHITE)
    fire_text = font.render("Fire", True, WHITE)

    # Render text directly onto the screen at the button locations
    screen.blit(left_text, (left_button.x + 25, left_button.y + 10))
    screen.blit(right_text, (right_button.x + 20, right_button.y + 10))
    screen.blit(fire_text, (fire_button.x + 20, fire_button.y + 10))

# Speed increment for button-based movement
BUTTON_MOVEMENT_SPEED = 35  # Increased speed for button clicks

def start1_game(username, high_score):
 global done, game_over, score, replay_cost
 # Fetch the high score from the database when the game ends and the player returns to the main menu
 if username:  # Check if username is valid (after login)
        # Reload the high score from the database
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM PlayerData WHERE username = ?", username)
        result = cursor.fetchone()
        if result:
            high_score = result[0]  # Set the high score from the database
        cursor.close()
        conn.close()


 
 # Start the game directly
 start_game()
 
 # Game loop (modified)
 while not done:
     screen.fill(BLACK)
     screen.blit(BACKGROUND_IMAGE, (0, 0))
 
     if game_over:
         if score >= replay_cost:
             restart_button = Button("Restart", (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2), font=50)
             quit_button = Button("Quit", (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2), font=50)
             restart_button.show(screen)
             quit_button.show(screen)
             font = pygame.font.Font(None, 36)
             text = font.render(f"Use {replay_cost} score points to replay?", True, WHITE)
             screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
             for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     done = True
                 elif event.type == pygame.MOUSEBUTTONDOWN:
                     if restart_button.click(event):
                         score -= replay_cost
                         replay_cost += 100
                         start_game()
                     elif quit_button.click(event):
                         done = True
         else:
             font = pygame.font.Font(None, 36)
             text = font.render("Not enough score for replay. Exiting in 5 seconds.", True, RED)
             screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
             pygame.display.flip()
             time.sleep(5)
             from play_screen import play_screen
             play_screen(username, high_score)
             # Transition back to home screen
             game_active = False
             game_over = False
     else:
         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 done = True
             elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_SPACE:
                     player.shoot()
             elif event.type == pygame.MOUSEBUTTONDOWN:
                 if left_button.collidepoint(event.pos):
                     player.rect.x -= BUTTON_MOVEMENT_SPEED
                 elif right_button.collidepoint(event.pos):
                     player.rect.x += BUTTON_MOVEMENT_SPEED
                 elif fire_button.collidepoint(event.pos):
                     player.shoot()
 
         all_sprites.update()
         hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
         for hit in hits:
             score += 1
             explosion = Explosion(hit.rect.center)
             all_sprites.add(explosion)
             EXPLOSION_SOUND.play()
             enemy = Enemy()
             all_sprites.add(enemy)
             enemies.add(enemy)
 
         hits = pygame.sprite.spritecollide(player, enemies, True)
         if hits:
             game_over = True
 
         # When game over happens, save high score to the database
         if game_over:
             update_high_score(username, score)
 
         all_sprites.draw(screen)
         font = pygame.font.Font(None, 36)
         text = font.render("Score: " + str(score), True, WHITE)
         screen.blit(text, (10, 10))
         high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
         screen.blit(high_score_text, (10, 35))
 
         draw_buttons()  # Draw buttons
 
     pygame.display.flip()
     clock.tick(FPS)