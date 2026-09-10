⛳ Golf Off

Golf Off is a fun, physics-based, 2D top-down minigolf game built with Python and Pygame. Play solo or challenge up to 3 friends in local multiplayer as you navigate dynamic courses filled with hazards, moving walls, hills, and pits.

The coolest part? The courses are generated entirely from standard .png images! The game reads the RGB pixel data of an image to place walls, water, spawns, and the goal.
✨ Features

    🏌️ Local Multiplayer: Support for 1 to 4 players. Take turns shooting, or bump your opponents' balls into hazards!

    ⚙️ Physics & Collisions: Features wall bouncing, ball-to-ball collisions, momentum transfer, and friction.

    🗺️ Image-Based Map Generation: The game dynamically builds the tilemap by reading pixel colors from image files (golf_map1.png, etc.).

    🛑 Dynamic Hazards:

        Water: Resets your ball's position and adds a randomized shooting debuff.

        Hills & Pits: Alter your ball's trajectory, speed, and angle.

        Moving Walls: Blocks that patrol back and forth to block your path.

    🎥 Dynamic Camera & Minimap: The camera smoothly follows the current player's ball. Includes a live-updating minimap in the corner of the screen.

    🏆 Score Tracking: Keeps track of your strokes per hole and calculates your total score across all maps.

🛠️ Requirements & Tech Stack

    Language: Python 3.x

    Libraries:

        pygame (Graphics, Input, Window Management)

        Pillow / PIL (Image processing for map generation)

🚀 Getting Started
1. Clone the repository
code Bash

git clone <your-repository-url>
cd <your-repository-folder>

2. Install Dependencies

You need to install Pygame and Pillow to run the game. You can do this via pip:
code Bash

pip install pygame Pillow

3. Setup the Asset Directory

Ensure your project folder contains an img/ directory with the required fonts and map files:
code Text

📁 Project Root
 ├── main.py
 ├── sprites.py
 ├── config.py
 ├── comici.ttf             # Required font file
 └── 📁 img/
      ├── golf_map1.png     # Map 1
      ├── golf_map2.png     # Map 2
      └── golf_map3.png     # Map 3

4. Run the Game
code Bash

python main.py

🎮 Controls
Shooting

    Left Click + Drag: Click on your ball and drag backwards to aim and set the power of your shot.

    Release Left Click: Shoot the ball!

Camera Management

By default, the camera locks onto the current player's ball. You can inspect the map using the Free-Cam:

    W, A, S, D: Move the camera around the map freely.

    Left Shift: Hold while moving to speed up the camera.

    Spacebar: Instantly snap the camera back to the current player's ball and return to shooting mode.

🎨 How Image-Based Maps Work

Golf Off uses a unique map-loading system. In main.py, the create_tilemap function scans a PNG image pixel-by-pixel. The exact RGB color of a pixel determines what object spawns at that tile:

    ⬛ (0, 0, 0): Wall

    ⬜ (211, 211, 211): Player Spawn Point

    🟦 (0, 0, 255): Water Hazard

    🔘 (134, 134, 134): Goal / Hole

    🔴 (50, r, s): Hill (r = radius, s = steepness)

    🟤 (100, r, s): Pit (r = radius, s = steepness)

    🧱 (150, x, y) / (200, x, y): Moving Walls (x and y determine patrol distance)

Want to make your own custom courses? Just open Paint or Photoshop, draw a course using these specific RGB values, save it as a PNG, and add it to self.map_list in main.py!