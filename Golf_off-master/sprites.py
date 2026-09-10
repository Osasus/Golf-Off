import pygame
from config import *
import math
import random

# Define the player class
class Player(pygame.sprite.Sprite):
    # Initialize the player
    def __init__(self, game, x, y, id, color):
        # Define the groups the player belongs to
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.player_sprite
        # Initialize the sprite
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the player's attributes and variables
        self.radius = TILESIZE // 2
        
        self.id = id

        self.total_x = 0
        self.total_y = 0

        self.hits = False
        self.game.first_hit = False
        self.counter = 1
        self.hit_side = False
        self.hit_top = False

        self.first_time = True
        self.stop = False
        self.score = 0
        self.x_offset = 0
        self.y_offset = 0

        self.speed = 0
        self.pos_start = (0, 0)
        self.pos_end = (0, 0)

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.switch = False

        self.angle = 0

        self.debuff = 0

        # Create the player's surface
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        # Draw the player's circle
        self.rect = pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        # Set the player's position
        self.rect.x = self.x
        self.rect.y = self.y

        # Create a sprite for the players center
        self.center = pygame.sprite.Sprite()
        pygame.sprite.Sprite.__init__(self.center, self.groups) 
        self.center.image = pygame.Surface((1, 1))
        self.center.rect = pygame.draw.circle(self.center.image, TRANSPARENT, (self.radius, self.radius), 1)
        self.center.rect.x = self.rect.centerx
        self.center.rect.y = self.rect.centery

    # Update the player
    def update(self):
        # Check if the player is allowed to move
        if not self.stop:
            # Call the movement function
            self.movement()
        # Call the camera movement function if the player is the current player
        if self.game.players[self.game.index] == self:
            self.cameraMove()
        # Call the win function
        self.win()
        # Call the collideMap function
        self.collideMap()

    # Method to check if the player collides with a hill / Pit
    def hillPitCollide(self):
        # Check if the player collides with a hill's rectangular hitbox
        hits_hill = pygame.sprite.spritecollide(self, self.game.hill, False)
        if hits_hill:
            # Check if the players center has collided with the hill's circle
            hits_circle = pygame.sprite.collide_circle(self.center, hits_hill[0])
            if hits_circle:
                # Check if the player is within the selected margin of error
                if abs(hits_hill[0].rect.centerx - self.rect.centerx) > 0.05*hits_hill[0].width or abs(hits_hill[0].rect.centery - self.rect.centery) > 0.05*hits_hill[0].height:
                    # Calculate the angle between the player and the hill
                    hill_angle = math.atan2(hits_hill[0].rect.centery - self.rect.centery, hits_hill[0].rect.centerx - self.rect.centerx)
                    # Calculate the new speed and angle of the player based on the players vector and the hill / pits vector
                    self.speed = math.sqrt((hits_hill[0].speed * math.cos(hill_angle) + self.speed * math.cos(self.angle)) ** 2 + (hits_hill[0].speed * math.sin(hill_angle) + self.speed * math.sin(self.angle)) ** 2)
                    self.angle = math.atan2(hits_hill[0].speed * math.sin(hill_angle) + self.speed * math.sin(self.angle), hits_hill[0].speed * math.cos(hill_angle) + self.speed * math.cos(self.angle))
    
    # Method to check if the player collides with another player
    def collidePlayer(self):
        # Loop through all the players
        for sprite in self.game.players:
            # Check if the player is not the current player
            if sprite != self:
                # Check if the player collides with another player
                hits = pygame.sprite.collide_circle(self, sprite)
                # Check if the player has collided with another player and the player has a score
                if hits and sprite.score != 0 and self.score != 0:
                    # Set a variable for the resistance of the hit player
                    friction = 3
                    # Calculate the angle between the player and the other player
                    angle = math.atan2(sprite.rect.centery - self.rect.centery, sprite.rect.centerx - self.rect.centerx)
                    # Calculate the new speed and angle of the player based on the players vector and the other players vector
                    self.speed = math.sqrt((friction * math.cos(angle) + self.speed * math.cos(self.angle)) ** 2 + (friction * math.sin(angle) + self.speed * math.sin(self.angle)) ** 2)
                    self.angle = math.atan2(friction * math.sin(angle) + self.speed * math.sin(self.angle), friction * math.cos(angle) + self.speed * math.cos(self.angle))
                    # Change the hit players speed and angle
                    sprite.speed = self.speed
                    sprite.angle = math.atan2(self.rect.centery - sprite.rect.centery, self.rect.centerx - sprite.rect.centerx)
    
    # Method to find the goal
    def goalCollide(self):
        # Loop through all the goals
        for sprite in self.game.goal:
            self.goal = sprite
    # Method to check if the player collides with the goal
    def win(self):
        # Call the goalCollide function
        self.goalCollide()
        # Check if the player collides with the goal
        hits = pygame.sprite.collide_circle(self.goal, self.center)
        
        # Check if the player has collided with the goal the player is still
        if hits and self.speed < 0.1:
            # Change the current player
            self.game.index += 1
            if self.game.index > len(self.game.players)-1:
                self.game.index = 0
            # Calculate the offset between the current player and the previous player
            self.x_offset = self.game.players[self.game.index].rect.centerx - self.game.players[self.game.index-1].rect.centerx
            self.y_offset = self.game.players[self.game.index].rect.centery - self.game.players[self.game.index-1].rect.centery
            # Move all the sprites based on the offset
            for sprite in self.game.all_sprites:
                sprite.rect.x -= self.x_offset
                sprite.rect.y -= self.y_offset
            # Remove the player from the game
            self.kill()
            # Remove the player from the player list
            self.game.players.remove(self)
            # Adjust the player index to match the new player list
            if self.game.index != 0:
                self.game.index -= 1
            # Add the players score to the recent score list
            self.game.recent_score[self.id] = self.score
            # Add the players score to the total score list
            self.game.scores[self.id] += self.score

    # Method to move the player in the x direction
    def moveX(self):
        # Move the player in the x direction
        self.rect.x -= self.speed * math.cos(self.angle)
        # Update the total x movement
        self.total_x -= self.speed * math.cos(self.angle)
        # Move the players center
        self.center.rect.x = self.rect.centerx
        # Check if the player is the current player
        if self.game.players[self.game.index] == self:
            # Move all the sprites based on the players movement (Camera movement)
            for sprite in self.game.all_sprites:
                sprite.rect.x += self.speed * math.cos(self.angle)

        
    # Method to move the player in the y direction
    def moveY(self):
        # Move the player in the y direction
        self.rect.y -= self.speed * math.sin(self.angle)
        # Update the total y movement
        self.total_y -= self.speed * math.sin(self.angle)
        # Move the players center
        self.center.rect.y = self.rect.centery
        # Check if the player is the current player
        if self.game.players[self.game.index] == self:
            # Move all the sprites based on the players movement (Camera movement)
            for sprite in self.game.all_sprites:
                sprite.rect.y += self.speed * math.sin(self.angle)

    # Method to move the player
    def movement(self):
        # Check if the player is the current player
        if self.game.players[self.game.index] == self:
            # Call the checkMouse function
            self.checkMouse()
            # Call the collidePlayer function
            self.collidePlayer()
        
        # If the player is supposed to move, move it
        if self.speed > 0.1:
            # Call movement and collision functions
            self.moveX()
            self.collideX()
            self.moveY()
            self.collideY()
        # Adjust player speed to account for friction
        self.speed = self.speed * 0.97

    # Method to check if the player collides with a wall from the x direction    
    def collideX(self):
        # Check if the player collides with a wall
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if hits:
            # Move all the sprites to reflect the player
            for sprite in self.game.all_sprites:
                if sprite != self:
                    sprite.rect.x -= self.speed * math.cos(self.angle)
            # Adjust the players angle
            self.angle = -(self.angle + 180 * 0.0174532925)

    # Method to check if the player collides with a wall from the y direction
    def collideY(self):
        # Check if the player collides with a wall
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if hits: 
            # Move all the sprites to reflect the player
            for sprite in self.game.all_sprites:
                if sprite != self:
                    sprite.rect.y -= self.speed * math.sin(self.angle)
            # Adjust the players angle
            self.angle = -(self.angle + 360 * 0.0174532925)

    # Method to check if the player collides with the map
    def collideMap(self):
        self.hillPitCollide()
        self.waterCollide(False)

    # Method to check if the player collides with water
    def waterCollide(self, called_by_wall):
        # Check if the player collides with water
        hits = pygame.sprite.spritecollide(self, self.game.water, False)
        if hits:
            # Check if the player is slow enough to be affected by the water
            if self.speed < 4:
                self.speed = 0
                # Reset the player ball to the last position where the ball was shot from
                self.rect.x -= self.total_x
                self.rect.y -= self.total_y
                # Adjust the camera if the player is the current player
                if self.game.players[self.game.index] == self:
                    for sprite in self.game.all_sprites:
                            sprite.rect.x += self.total_x
                            sprite.rect.y += self.total_y
                # Give a debuff if the player got pushed in the water by an outside force
                if self.game.players[self.game.index] != self or called_by_wall:
                    self.debuff = random.randint(-60, 60)
            # Reduce the player speed if the player is moving too fast
            else:
                self.speed = self.speed * 0.90
    
    # Method to check if the player is being shot
    def checkMouse(self):
        # Get the mouse position and the mouse button state
        self.mouse_pos = pygame.mouse.get_pos()
        self.pressed = pygame.mouse.get_pressed()

        # Check if the player is not pressed
        if not self.pressed[0]:
            # Check if the player has been shot
            if not self.first_time:
                # Calculate the players speed based on the distance between the start and end position of the mouse
                self.speed = math.sqrt(self.pos_end[0] ** 2 + self.pos_end[1] ** 2) / 10
                # Add a stroke to the player
                self.score += 1
                # Variable to allow the switch of a player
                self.switch = True

            self.first_time = True
            # Check if the player turn has ended
            if self.switch and self.speed < 0.1:
                # Change the current player
                self.game.index += 1
                if self.game.index > len(self.game.players)-1:
                    self.game.index = 0
                # Calculate the offset between the current player and the previous player
                self.x_offset = self.game.players[self.game.index].rect.centerx - self.game.players[self.game.index-1].rect.centerx
                self.y_offset = self.game.players[self.game.index].rect.centery - self.game.players[self.game.index-1].rect.centery
                # Move all the sprites based on the offset
                for sprite in self.game.all_sprites:
                    sprite.rect.x -= self.x_offset
                    sprite.rect.y -= self.y_offset
                # Reset variables
                self.switch = False
                self.debuff = 0

        # Check if the player is pressed and not moving
        if self.pressed[0] and self.rect.collidepoint(self.mouse_pos) and self.speed <= 0.1:
            # Check if the player is being shot for the first time
            if self.first_time:
                # Set the start position of the mouse
                self.pos_start = (self.mouse_pos[0], self.mouse_pos[1])
                # Reset the players previous position
                self.total_x = 0
                self.total_y = 0
                self.first_time = False
        # Update the end mouse position if the mouse is pressed
        if self.pressed[0] and not self.first_time and self.speed <= 0.1:
            # Set the end position of the mouse
            self.pos_end = ((self.mouse_pos[0] - self.pos_start[0]), (self.mouse_pos[1] - self.pos_start[1]))
            # Calculate the angle between the player and the mouse
            self.angle = math.atan2(self.pos_end[1], self.pos_end[0]) + self.debuff * 0.0174532925
            self.hit = False
            # Draw the direction the player is being shot
            if self.debuff == 0:
                color = WHITE
            else:
                color = RED
            self.game.drawDirection(self.pos_end, color)

    # Method to move the camera
    def cameraMove(self):
        # Check if the player is moving
        if self.speed < 0.1:
            # Get the keys pressed
            keys = pygame.key.get_pressed()
            speed_multiplier = 1
            # Check if the shift key is pressed, if so increase the speed of the camera
            if keys[pygame.K_LSHIFT]:
                speed_multiplier = 3
            # If a movement key is pressed, block player movement
            if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
                self.stop = True
            # Move the camera based on the keys pressed
            if keys[pygame.K_w]:
                for sprite in self.game.all_sprites:
                    sprite.rect.y += 5 * speed_multiplier
            if keys[pygame.K_s]:
                for sprite in self.game.all_sprites:
                    sprite.rect.y -= 5 * speed_multiplier
            if keys[pygame.K_a]:
                for sprite in self.game.all_sprites:
                    sprite.rect.x += 5 * speed_multiplier
            if keys[pygame.K_d]:
                for sprite in self.game.all_sprites:
                    sprite.rect.x -= 5 * speed_multiplier
            # Check if the space key is pressed, if so unblock player movement and reset the camera
            if keys[pygame.K_SPACE]:
                self.stop = False
                y_offset = self.rect.centery - WIN_HEIGHT/2
                x_offset = self.rect.centerx - WIN_WIDTH/2
                for sprite in self.game.all_sprites:
                    sprite.rect.x -= x_offset
                    sprite.rect.y -= y_offset

# Define the wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Define the groups the wall belongs to
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the walls attributes
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = pygame.surface.Surface([self.width, self.height])
        self.image.fill(BROWN)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

# Define the water class
class Water(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Define the groups the water belongs to
        self.game = game
        self._layer = CIRCLE_LAYER
        self.groups = self.game.all_sprites, self.game.water
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the water attributes
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = pygame.surface.Surface([self.width, self.height])
        self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

# Define the goal class
class Goal(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Define the groups the goal belongs to
        self.game = game
        self._layer = GOAL_LAYER
        self.groups = self.game.all_sprites, self.game.goal
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the goal attributes
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE * 2
        self.height = TILESIZE * 2

        self.radius = TILESIZE // 2
        self.image = pygame.surface.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = pygame.draw.circle(self.image, BLACK, (self.radius, self.radius), self.radius)
        self.rect.x = self.x
        self.rect.y = self.y

# Define the hill class
class Hill(pygame.sprite.Sprite):
    def __init__(self, game, x, y, radius, speed):
        # Define the groups the hill belongs to
        self.game = game
        self._layer = CIRCLE_LAYER
        self.groups = self.game.all_sprites, self.game.hill
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the hill attributes
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE * radius
        self.height = TILESIZE * radius
        self.color = LIGHT_GREEN
        
        # Define steepness for vector addition
        self.speed = speed

        self.radius = (radius * TILESIZE) / 2
        self.image = pygame.surface.Surface ((self.width, self.height), pygame.SRCALPHA)
       # Define colors for gradient
        start_color = (0, 200, 0)
        mid_color = (144, 235, 144)

        color_steps = []
        for i in range(3):
            color_steps.append([(mid_color[i] - start_color[i]) / (self.radius / 5) * (1 - math.cos((math.pi / 2) * (j / 2 / 5))) for j in range(int(self.radius / 5) * 5)])

        # Draw concentric circles with gradient
        current_color = start_color
        for step in range(int(self.radius), 0, -5):
            color = tuple(int(max(min(current_color[j] + color_steps[j][min(step // 5, len(color_steps[j]) - 1)], mid_color[j]), start_color[j])) for j in range(3))
            pygame.draw.circle(self.image, color, (int(self.radius), int(self.radius)), step)
            current_color = color

        self.rect = self.image.get_rect()
        self.rect.x = self.x - self.radius / 2
        self.rect.y = self.y - self.radius / 2

# Define the pit class
class Pit(pygame.sprite.Sprite):
    def __init__(self, game, x, y, radius, speed):
        # Define the groups the pit belongs to
        self.game = game
        self._layer = CIRCLE_LAYER
        self.groups = self.game.all_sprites, self.game.hill
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the pit attributes
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE * radius
        self.height = TILESIZE * radius
        self.color = GREEN
        
        self.speed = -speed

        self.radius = (radius * TILESIZE) / 2
        self.image = pygame.surface.Surface ((self.width, self.height), pygame.SRCALPHA)

        i = self.width
        segment_width = 5  # Desired width of each segment
        while i > 0:
            step = max(segment_width, int(i / 20))  # Adjust step size
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), int(i/2), segment_width)
            i -= step
            self.color = (self.color[0], max(self.color[1] - step, 100), self.color[2])

        self.rect = self.image.get_rect()
        self.rect.x = self.x - self.radius / 2
        self.rect.y = self.y - self.radius / 2

# Define the wall class
class WallOfDestruction(pygame.sprite.Sprite):
    def __init__(self, game, x, y, move_x, move_y, speed):
        # Define the groups the wall belongs to
        self.groups = game.all_sprites, game.blocks
        self.game = game
        self._layer = MOVING_LAYER
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Define the walls attributes
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.facing_x = "right"
        self.facing_y = "up"
        self.movement_loop_x = 0
        self.movement_loop_y = 0

        self.max_x = move_x * TILESIZE
        self.max_y = move_y * TILESIZE

        self.speed = speed

        self.image = pygame.surface.Surface([self.width, self.height])
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    # Update the wall
    def update(self):
        self.moveX()
        self.moveY()
        self.collide()

    # Method to move the wall in the x direction
    def moveX(self):
        # Check if the wall is supposed to move in the x direction
        if self.max_x != 0:
            # Move the wall in the x direction
            if self.facing_x == 'left':
                self.rect.x -= self.speed
                self.movement_loop_x -= self.speed
                # Check if the wall has reached the end of its movement
                if self.movement_loop_x <= 0:
                    self.facing_x = 'right'
            if self.facing_x == 'right':
                self.rect.x += self.speed
                self.movement_loop_x += self.speed
                if self.movement_loop_x >= self.max_x:
                    self.facing_x = 'left'

    # Method to move the wall in the y direction
    def moveY(self):
        # Check if the wall is supposed to move in the y direction
        if self.max_y:
            if self.facing_y == 'up':
                self.rect.y -= self.speed
                self.movement_loop_y -= self.speed
                if self.movement_loop_y <= 0:
                    self.facing_y = 'down'
            if self.facing_y == 'down':
                self.rect.y += self.speed
                self.movement_loop_y += self.speed
                if self.movement_loop_y >= self.max_y:
                    self.facing_y = 'up'

    # Method to check if the wall collides with a player
    def collide(self):
        # Check if the wall collides with a player
        hits = pygame.sprite.spritecollide(self, self.game.player_sprite, False)
        if hits:
            # Move the player based on the walls movement
            if self.max_x != 0:    
                if self.facing_x == 'left':
                    hits[0].rect.x -= self.speed+1
                    hits[0].total_x -= self.speed+1
                    if self.game.players[self.game.index] == hits[0]:
                        for sprite in self.game.all_sprites:
                            sprite.rect.x += self.speed+1

                if self.facing_x == 'right':
                    hits[0].rect.x += self.speed+1
                    hits[0].total_x += self.speed+1
                    if self.game.players[self.game.index] == hits[0]:
                        for sprite in self.game.all_sprites:
                            sprite.rect.x -= self.speed+1
            if self.max_y != 0:
                if self.facing_y == 'up':
                    hits[0].rect.y -= self.speed +1
                    hits[0].total_y -= self.speed+1
                    if self.game.players[self.game.index] == hits[0]:
                        for sprite in self.game.all_sprites:
                            sprite.rect.y += self.speed+1

                if self.facing_y == 'down':
                    hits[0].rect.y += self.speed+1
                    hits[0].total_y += self.speed+1
                    if self.game.players[self.game.index] == hits[0]:
                        for sprite in self.game.all_sprites:
                            sprite.rect.y -= self.speed+1
            # Call the waterCollide function to check if the player is in water
            hits[0].waterCollide(True)


# Define the button class
class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        # Define the buttons attributes
        self.font = pygame.font.Font("comici.ttf", fontsize)
        self.content = content
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()
        
        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center =(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)
    
    # Method to check if the button is pressed
    def isPressed(self, pos, pressed):
        # Check if the mouse is over the button
        if self.rect.collidepoint(pos):
            # Check if the button is pressed
            if pressed[0]:
                # Return True if the button is pressed
                return True
            return False
        return False
    

            
            
