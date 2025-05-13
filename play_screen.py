import pygame
import random
import time
import pyodbc


# Initialize Pygame
pygame.init()

# You can change the size (36) as needed
font = pygame.font.Font(None, 36)  

# Declaration 
username = ""  # Initialize username globally

# Screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False

# Create the Pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create the "Play" button and welcome message
play_button = Button("Shoot Game", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), font=74)

# Logout button at the top left
logout_button = Button("Logout", (50, 50), font=36)

# Function to handle logout action
def logout():
    global username, game_active, game_over
    # Reset game state and user session
    username = ""
    game_active = False
    game_over = False
    # Switch to login screen
    if username:
       from login import game_loop
       game_loop()

def play_screen(username, high_score):
    
    # Fetch the high score from the database when the game ends and the player returns to the main menu
    if username:
        # Reload the high score from the database
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT high_score FROM PlayerData WHERE username = ?", username)
        result = cursor.fetchone()
        if result:
            high_score = result[0]  # Set the high score from the database
        cursor.close()
        conn.close()

    done = False
    while not done:
        screen.fill(BLACK)
        font = pygame.font.Font(None, 74)

        # Display player name at the top (just below the top of the screen)
        if username:  # Check if username is not empty
            player_name_text = font.render(f"Hi, {username}", True, WHITE)
            screen.blit(player_name_text, (SCREEN_WIDTH // 2 - player_name_text.get_width() // 2, 20))  # Position at top
        
        # Display game message
        text = font.render("Choose a Game to Play", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() - 100))

        # Create buttons for game selection
        car_game_button = Button("Car Game", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80), font=50)

        car_game_button.show(screen)
        play_button.show(screen)
        logout_button.show(screen)  # Display the logout button

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.click(event):
                    from shoot_game import start1_game
                    start1_game(username, high_score)  # Start the game when Play is clicked
                    done = True  # Exit play screen and start game loop
                elif car_game_button.click(event):
                    from car_game import start_car_game  # Import start_car_game from the car game
                    start_car_game(username, high_score)  # Start the car game with the current username
                    done = True
                elif logout_button.click(event):  # Handle logout click
                    game_active = False
                    game_over = False
                    logged_in = False  # Logout the current player
                    username = ""
                    password = ""
                    from login import game_loop
                    game_loop()  # Call the game loop to show the login screen again

        pygame.display.flip()