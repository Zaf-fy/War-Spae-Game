import pygame
import pyodbc
import time

# Initialize Pygame
pygame.init()

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

# Font settings
font = pygame.font.Font(None, 36)

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

# Function to display a message on the screen
def show_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + y_offset))

# Create the Pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Login and Signup")

# Function to create a button on the screen
def create_button(message, x, y, width, height, color, text_color):
    pygame.draw.rect(screen, color, pygame.Rect(x, y, width, height))
    text = font.render(message, True, text_color)
    screen.blit(text, (x + width // 2 - text.get_width() // 2, y + height // 2 - text.get_height() // 2))

# Function to check if a button is clicked
def is_button_clicked(x, y, width, height, mouse_pos):
    return x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height

# Function to handle switching between login and signup screens
def game_loop():
    logged_in = False
    signup = False
    username = ""
    password = ""
    high_score = 0  # Temporary high score for the session
    done = False
    clock = pygame.time.Clock()
    
    # Variables to track focus (use tab to switch focus)
    focus_field = "username"  # Start with the username field

    # Message tracking variables
    message = ""  # Variable to store the current message to display
    message_color = WHITE  # Default color of message
    last_message_time = 0  # Time when the message was shown
    message_duration = 3000  # Duration for the message to be displayed (in milliseconds)

    while not done:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if focus_field == "username" and username:
                        username = username[:-1]
                    elif focus_field == "password" and password:
                        password = password[:-1]
                elif event.key == pygame.K_RETURN:  # Submit on Enter key
                    if signup:
                        # Signup process
                        if username and password:
                            # Attempt to save player data
                            if save_player_data(username, password, high_score):
                                message = "Account Created! Switching to login..."
                                message_color = GREEN
                                last_message_time = current_time  # Track when the message was shown
                                pygame.display.flip()
                                time.sleep(1)  # Wait for 1 second before switching to login
                                signup = False  # Switch to the login screen after successful signup
                                username = ""  # Clear fields for login
                                password = ""  # Clear fields for login
                            else:
                                message = "Username already exists! Please choose a different one."
                                message_color = RED
                                last_message_time = current_time
                                time.sleep(1)
                        else:
                            message = "Please fill in both fields"
                            message_color = RED
                            last_message_time = current_time
                            time.sleep(1)
                    else:
                        # Login process
                        if username and password:
                            if authenticate_user(username, password):
                                logged_in = True
                                message = "Login Successful!"
                                message_color = GREEN
                                last_message_time = current_time
                                time.sleep(2)
                                done = True
                            else:
                                message = "Invalid credentials. Please try again."
                                message_color = RED
                                last_message_time = current_time
                                time.sleep(1)
                        else:
                            message = "Please enter both username and password"
                            message_color = RED
                            last_message_time = current_time
                            time.sleep(1)

                elif event.key == pygame.K_TAB:  # Switch between username and password using Tab
                    if focus_field == "username":
                        focus_field = "password"
                    else:
                        focus_field = "username"
                else:
                    # Handle regular typing
                    if focus_field == "username" and len(username) < 20 and event.unicode.isalnum():
                        username += event.unicode
                    elif focus_field == "password" and len(password) < 20:
                        password += event.unicode

            mouse_pos = pygame.mouse.get_pos()

            # Display the login/signup screen
            if not signup:
                show_message("Login", WHITE, -100)
                show_message(f"Username: {username}", WHITE, -50)
                show_message(f"Password: {'*' * len(password)}", WHITE, 0)
                if not username and not password:
                    show_message("Press TAB for switch user & password", WHITE, 50)

                # Create a "Signup" button on the login screen
                create_button("Signup", 350, 400, 200, 50, BLUE, WHITE)
                if is_button_clicked(350, 400, 200, 50, mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    signup = True  # Switch to the signup screen
                    username = ""  # Clear fields for new data
                    password = ""

                # Show error message for login only if it was set recently
                if current_time - last_message_time <= message_duration and message != "":
                    show_message(message, message_color, 170)

            else:
                show_message("Signup", WHITE, -100)
                show_message(f"Username: {username}", WHITE, -50)
                show_message(f"Password: {'*' * len(password)}", WHITE, 0)
                show_message("Press Enter to Submit", WHITE, 50)

                # Create a "Login" button on the signup screen
                create_button("Login", 350, 400, 200, 50, BLUE, WHITE)
                if is_button_clicked(350, 400, 200, 50, mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    signup = False  # Switch to the login screen
                    username = ""  # Clear fields for new data
                    password = ""

                # Show error message for signup only if it was set recently
                if current_time - last_message_time <= message_duration and message != "":
                    show_message(message, message_color, 170)

            pygame.display.flip()
            clock.tick(FPS)
            
    from play_screen import play_screen
    play_screen(username, high_score)

game_loop()
