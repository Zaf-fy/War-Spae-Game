import pygame
from pygame.locals import *
import random
import pyodbc

def start_car_game(username, high_score):  
    pygame.init()

    # create the window
    width = 900
    height = 600
    screen_size = (width, height)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Car Game')

    # colors
    WHITE = (255, 255, 255)
    gray = (100, 100, 100)
    green = (76, 208, 56)
    red = (200, 0, 0)
    white = (255, 255, 255)
    yellow = (255, 232, 0)

    # road and marker sizes
    road_width = 300
    marker_width = 10
    marker_height = 50

    # lane coordinates
    left_lane = 150
    center_lane = 250
    right_lane = 350
    lanes = [left_lane, center_lane, right_lane]

    # road and edge markers
    road = (100, 0, road_width, height)
    left_edge_marker = (95, 0, marker_width, height)
    right_edge_marker = (395, 0, marker_width, height)

    # for animating movement of the lane markers
    lane_marker_move_y = 0

    # player's starting coordinates
    player_x = 250
    player_y = 400

    # frame settings
    clock = pygame.time.Clock()
    fps = 120

    # game settings
    gameover = False
    speed = 2
    score = 0

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

    # Update high score in the database
    def update_car_high_score(username, car_high_score):
        conn = connect_to_db()
        cursor = conn.cursor()

        # Check the current high score in the database for the given username
        cursor.execute("SELECT car_high_score FROM PlayerData WHERE username = ?", username)
        result = cursor.fetchone()
    
        if result:
            current_car_high_score = result[0]
            if current_car_high_score is None or car_high_score > current_car_high_score:
                # Update the high score if the current one is higher or if there's no existing high score
                cursor.execute("UPDATE PlayerData SET car_high_score = ? WHERE username = ?", car_high_score, username)
                conn.commit()

        cursor.close()
        conn.close()

    class Vehicle(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            pygame.sprite.Sprite.__init__(self)
            image_scale = 45 / image.get_rect().width
            new_width = image.get_rect().width * image_scale
            new_height = image.get_rect().height * image_scale
            self.image = pygame.transform.scale(image, (new_width, new_height))
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]

    class PlayerVehicle(Vehicle):
        def __init__(self, x, y):
            image = pygame.image.load('images/car.png')
            super().__init__(image, x, y)

    # sprite groups
    player_group = pygame.sprite.Group()
    vehicle_group = pygame.sprite.Group()

    # create the player's car
    player = PlayerVehicle(player_x, player_y)
    player_group.add(player)

    # load the vehicle images
    image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
    vehicle_images = []
    for image_filename in image_filenames:
        image = pygame.image.load('images/' + image_filename)
        vehicle_images.append(image)

    # load the crash image
    crash = pygame.image.load('images/crash.png')
    crash_rect = crash.get_rect()

    # Fetch the high score from the database
    if username:  # Check if username is valid (after login)
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT car_high_score FROM PlayerData WHERE username = ?", username)
        result = cursor.fetchone()
        if result:
            car_high_score = result[0]  # Set the high score from the database
        else:
            car_high_score = 0  # Default high score if no record exists
        cursor.close()
        conn.close()
    else:
        car_high_score = 0  # Default high score if no username is provided

    running = True
    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # move the player's car using the left/right arrow keys
            if event.type == KEYDOWN:
                if event.key == K_LEFT and player.rect.center[0] > left_lane:
                    player.rect.x -= 100
                elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                    player.rect.x += 100

                # check if there's a side swipe collision after changing lanes
                for vehicle in vehicle_group:
                    if pygame.sprite.collide_rect(player, vehicle):
                        gameover = True
                        if event.key == K_LEFT:
                            player.rect.left = vehicle.rect.right
                            crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                        elif event.key == K_RIGHT:
                            player.rect.right = vehicle.rect.left
                            crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

        # draw the grass
        screen.fill(green)

        # draw the road
        pygame.draw.rect(screen, gray, road)

        # draw the edge markers
        pygame.draw.rect(screen, yellow, left_edge_marker)
        pygame.draw.rect(screen, yellow, right_edge_marker)

        # draw the lane markers
        lane_marker_move_y += speed * 2
        if lane_marker_move_y >= marker_height * 2:
            lane_marker_move_y = 0
        for y in range(marker_height * -2, height, marker_height * 2):
            pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
            pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

        # draw the player's car
        player_group.draw(screen)

        # add a vehicle
        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False

            if add_vehicle:
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, height / -2)
                vehicle_group.add(vehicle)

        # make the vehicles move
        for vehicle in vehicle_group:
            vehicle.rect.y += speed
            if vehicle.rect.top >= height:
                vehicle.kill()
                score += 1
                if score > 0 and score % 5 == 0:
                    speed += 1

        # draw the vehicles
        vehicle_group.draw(screen)

        # display the score
        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        text = font.render('Score: ' + str(score), True, white)
        text_rect = text.get_rect()
        text_rect.center = (550, 300)
        screen.blit(text, text_rect)
        car_high_score_text = font.render(f"High Score: {car_high_score}", True, WHITE)
        screen.blit(car_high_score_text, (500, 320))

        # check if there's a head on collision
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]

        # display game over
        if gameover:
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, red, (0, 50, width, 100))
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render('Game over. Play again? (Enter Y or N)', True, white)
            text_rect = text.get_rect()
            text_rect.center = (width / 2, 100)
            screen.blit(text, text_rect)

            # When game over happens, save high score to the database
            update_car_high_score(username, score)

        pygame.display.update()

        # wait for user's input to play again or exit
        while gameover:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    gameover = False
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        gameover = False
                        speed = 2
                        score = 0
                        vehicle_group.empty()
                        player.rect.center = [player_x, player_y]
                    elif event.key == K_n:
                        gameover = False
                        running = False

    # After the car game ends, return to the play_screen
    from play_screen import play_screen  # Import play_screen from the shooting game
    play_screen(username, high_score)  # Call play_screen to return to the game selection screen