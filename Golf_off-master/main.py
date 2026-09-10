import pygame
from config import *
from sprites import *
from PIL import Image
import sys

class Game: 
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        # Set the title of the game window
        pygame.display.set_caption("GOLF OFF")
        # Set up the game window with specified width and height
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        # Create a surface for the minimap with alpha transparency
        self.minimap = pygame.surface.Surface((100, 100), pygame.SRCALPHA)
        # Initialize the clock for controlling the frame rate
        self.clock = pygame.time.Clock()
        # Load a font for rendering text, "comici.ttf" should be in the same directory
        self.font = pygame.font.Font("comici.ttf", 32)
        # Set the running flag to True to indicate the game is running
        self.running = True
        # List of map images to be used in the game
        self.map_list = ["img/golf_map1.png", "img/golf_map2.png", "img/golf_map3.png"]

        # Initialize the current player index
        self.index = 0
        # Placeholder for the image of the direction indicator
        self.directionImage = None

        # List to keep track of player scores
        self.scores = []

    def new(self):
        # Check if there are maps available to play
        if self.map_list:
            # Set the playing flag to True to indicate a new game session
            self.playing = True
            # Define a list of colors that may be used in the game (e.g., for players or objects)
            self.colors = [LIGHT_BLUE, RED, PURPLE, WHITE, ORANGE, YELLOW, PINK]

            # Create LayeredUpdates groups for different types of sprites
            self.all_sprites   = pygame.sprite.LayeredUpdates()
            self.blocks        = pygame.sprite.LayeredUpdates()
            self.player_sprite = pygame.sprite.LayeredUpdates()
            self.goal          = pygame.sprite.LayeredUpdates()
            self.hill          = pygame.sprite.LayeredUpdates()
            self.water         = pygame.sprite.LayeredUpdates()

            # Randomly select a map from the list of maps
            self.nbr = random.randint(0, len(self.map_list) - 1)
            map = self.map_list[self.nbr]

            # Initialize the list of players
            self.players = []
            # Create the tilemap for the selected map
            self.create_tilemap(map)
            # Generate additional tilemap elements (method implementation not provided)
            self.generateTilemap()
            # Calculate the initial offset to center the player on the screen
            self.y_offset = self.players[0].rect.centery - WIN_HEIGHT / 2
            self.x_offset = self.players[0].rect.centerx - WIN_WIDTH / 2
            # Adjust the position of all sprites based on the calculated offsets
            for sprite in self.all_sprites:
                sprite.rect.x -= self.x_offset
                sprite.rect.y -= self.y_offset

    def events(self):
        # Check if the player quits the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def main(self):
        # Main loop for the game
        while self.playing:
            self.events()
            self.update()
            self.draw()
            # If all players are done, end the game
            if not self.players:
                self.playing = False
                for sprite in self.all_sprites:
                    sprite.kill()
        # If there are maps left to play, call the scoreboard
        if self.map_list:
            self.callScoreboard()
        else:
            self.running = False

    def create_tilemap(self, map):
        # Open the image
        img = Image.open(map)
        
        img = img.convert('RGB')
        
        # Get image dimensions
        height, width = img.size
        
        # Create an empty list to store the tilemap
        self.map = []
        
        # Iterate through the image and extract tiles
        for y in range(width):
            row = []
            for x in range(height):
                # Crop the tile from the image
                tile = img.crop((x, y, (x + 1), (y + 1)))
                # Convert the tile to a list of RGB values
                tile_colors = list(tile.getdata())
                # Append the tile colors to the row
                row.append(tile_colors)
            # Append the row to the tilemap
            self.map.append(row)
    
    def generateTilemap(self):
        # Based on the tilemap, generate the corresponding sprites
        for i, row in enumerate(self.map):
            for j, column in enumerate(row):
                if column == [(0,0,0)]:
                    Wall(self, j, i)
                elif column == [(134,134,134)]:
                    Goal(self, j, i)
                    Pit(self, j, i, 2, 0.1)
                elif column[0][0] == 50:
                    # Based on the color values, determine radius and steepness
                    radius = column[0][1]
                    steepness = column[0][2] / 10
                    Hill(self, j, i, radius, steepness)
                elif column[0][0] == 100:
                    # Based on the color values, determine radius and steepness
                    radius = column[0][1]
                    steepness = column[0][2] / 10
                    Pit(self, j, i, radius, steepness)
                elif column == [(0,0,255)]:
                    Water(self, j, i)
                elif column[0][0] == 150:
                    # Based on the color values, determine the direction of the moving wall
                    move_x = column[0][1]
                    move_y = column[0][2]
                    WallOfDestruction(self, j, i, move_x, move_y, 2)
                elif column[0][0] == 200:
                    # Based on the color values, determine the direction of the moving wall
                    move_x = column[0][1]
                    move_y = column[0][2]
                    WallOfDestruction(self, j, i, move_x, move_y, 1)
                elif column ==[(211, 211, 211)]:
                    # Create player sprites based on the number of players
                    for u in range(self.count):
                        # Randomly select a color for each player
                        color_index = random.randint(0, len(self.colors) - 1)
                        self.players.append(Player(self, j, i, u, self.colors[color_index]))
                        self.colors.pop(color_index)
                    # Create a list to store the scores of each player
                    if not self.scores:
                        self.scores = [0 for u in range(self.count)]
                    self.recent_score = [0 for u in range(self.count)]

        # Create a miniature version of the map for the minimap
        self.minimap.fill(GREEN)
        for sprite in self.all_sprites:
                minisprite = pygame.transform.scale(sprite.image, (1, 1))
                self.minimap.blit(minisprite, (sprite.rect.x/30, sprite.rect.y/30))

        # Create a border for the minimap
        self.minimap_border = pygame.surface.Surface((110, 110), pygame.SRCALPHA)
        pygame.draw.rect(self.minimap_border, BLACK, (0, 0, 110, 110), 5)

    # Method to draw the game window
    def draw(self):
        # Fill the screen with a green background
        self.screen.fill(GREEN)
        # Draw all sprites on the screen
        self.all_sprites.draw(self.screen)
        # Draw the direction indicator if available
        if self.directionImage:
            self.screen.blit(self.directionImage, (0, 0))
            self.directionImage = None
        # Draw the player score on the screen
        if self.players:
            self.screen.blit(pygame.font.Font.render(self.font, str(self.players[self.index].score), True, BLACK), (WIN_WIDTH/2, 10))
        # Draw the minimap on the screen
        self.screen.blit(self.minimap_border, (0, 0))
        self.screen.blit(self.minimap, (5, 5))
        # Update the display
        self.clock.tick(FPS)
        pygame.display.update()

    # Method to draw the direction indicator
    def drawDirection(self, pos, color):
        # Create a surface for the direction indicator
        self.directionImage = pygame.surface.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        # Draw a circle on the surface
        pygame.draw.circle(self.directionImage, color, (WIN_WIDTH/2 - pos[0], WIN_HEIGHT/2 - pos[1]), 5)


    # Method to update all sprites
    def update(self):
        self.all_sprites.update()

    # Method to display the start screen
    def introScreen(self):
        # Set the intro flag to True
        intro = True
        # Prepare the elements for the start screen
        text = self.font.render("Golf Off", True, BLACK)
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
        start_text = self.font.render("Select Player Amount", True, BLACK)
        start_rect = start_text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
        start_button = Button(WIN_WIDTH/2 - 50, 350, 100, 50, BLACK, WHITE, "Start", 32)
        option_1 = Button(WIN_WIDTH/2 - 220, 350, 100, 50, BLACK, WHITE, "1", 32)
        option_2 = Button(WIN_WIDTH/2 - 110, 350, 100, 50, BLACK, WHITE, "2", 32)
        option_3 = Button(WIN_WIDTH/2 + 10, 350, 100, 50, BLACK, WHITE, "3", 32)
        option_4 = Button(WIN_WIDTH/2 + 120, 350, 100, 50, BLACK, WHITE, "4", 32)

        while intro:
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
            # Check if the space key is pressed to start the game
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                intro = False
                start = True
            # Fill the screen with a purple background
            self.clock.tick(FPS)
            self.screen.fill(PURPLE)
            # Draw the text and the start button on the screen
            self.screen.blit(text, text_rect)
            self.screen.blit(start_button.image, start_button.rect)
            pygame.display.update()

            # Set variables for the mouse position and button press
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            # Check if the start button is pressed
            if start_button.isPressed(mouse_pos, mouse_pressed):
                # If the start button is pressed, call the player selection screen
                intro = False
                start = True

        # Call the player selection screen
        while start:
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start = False
                    self.running = False
                # Check if the mouse is pressed
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()
                # Check if the player amount buttons are pressed
                if option_1.isPressed(mouse_pos, mouse_pressed):
                    self.count = 1
                    start = False
                elif option_2.isPressed(mouse_pos, mouse_pressed):
                    self.count = 2
                    start = False
                elif option_3.isPressed(mouse_pos, mouse_pressed):
                    self.count = 3
                    start = False
                elif option_4.isPressed(mouse_pos, mouse_pressed):
                    self.count = 4
                    start = False
            # Fill the screen with a purple background
            self.screen.fill(PURPLE)
            # Draw the player amount buttons on the screen
            self.screen.blit(option_1.image, option_1.rect)
            self.screen.blit(option_2.image, option_2.rect)
            self.screen.blit(option_3.image, option_3.rect)
            self.screen.blit(option_4.image, option_4.rect)
            self.screen.blit(start_text, start_rect)

            pygame.display.update()

    # Method to create the end screen
    def defineScoreboard(self):
        # Define timer variables
        self.start_time = pygame.time.get_ticks()
        self.current_time = pygame.time.get_ticks()
        # Create a surface for the scoreboard with alpha transparency
        self.scoreboard = pygame.surface.Surface((500, 500), pygame.SRCALPHA)
        self.scoreboard.fill(TRANSPARENT)
        # Draw the scoreboard elements
        pygame.draw.rect(self.scoreboard, MAROON, (0, 0, 500, 100))
        # Draw the player scores on the scoreboard
        for i in range(self.count):
            pygame.draw.rect(self.scoreboard, BEIGE, (0, 100 * (i+1), 500, 100))
            pygame.draw.rect(self.scoreboard, MAROON, (0, 100 * (i+1), 500, 100), 5)
            self.scoreboard.blit(pygame.font.Font.render(self.font, "Player " + str(i+1), True, BLACK), (10, 100 * (i+1) + 20))
            self.scoreboard.blit(pygame.font.Font.render(self.font, "Score: " + str(self.recent_score[i]), True, BLACK), (175, 100 * (i+1) + 20))
            self.scoreboard.blit(pygame.font.Font.render(self.font, "Total: " + str(self.scores[i]), True, BLACK), (350, 100 * (i+1) + 20))
    # Method to display the end screen
    def callScoreboard(self):
        # Define the scoreboard
        self.defineScoreboard()
        # Display the scoreboard for 3500 ticks
        while self.current_time - self.start_time < 3500:
            # Update the timer
            self.current_time = pygame.time.get_ticks()
            # Draw the scoreboard on the screen
            self.screen.fill(PURPLE)
            self.screen.blit(self.scoreboard, (50, 50))
            pygame.display.update()
        # Remove the current map from the maplist
        self.map_list.pop(self.nbr)
        print(self.map_list)
        print(self.nbr)
        # Create a new game
        self.new()
        self.main()

# Initialize the game
g = Game()
# Call the start screen
g.introScreen()
# Start the game
g.new()
# Main game loop
while g.running:
    # Call the main game method
    g.main()

# Quit the game
pygame.quit()
sys.exit()