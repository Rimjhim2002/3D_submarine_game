# 3D_submarine_game
Sunken Relics — Chase treasure through a deadly ocean. Sharks, enemy subs and hostile corals stand between you and glory. Oxygen drains constantly, so grab seabed refills fast. Follow the minimap to the treasure. Each level gets faster and darker. Cheat mode gives you homing torpedoes.Good luck.

Sunken Relics
Sunken Relics is a 3D submarine game made with Python (OpenGL + GLUT). You control a submarine exploring the ocean, collecting items, avoiding enemies, and trying to reach a hidden treasure.

Core Gameplay
Move your submarine in all directions (forward, turn, up/down)
Follow waypoints to reach the final treasure
Shoot enemies using torpedoes
Collect resources to survive

World
The ocean floor is randomly decorated with rocks, corals, and plants
The environment feels endless as you move

Enemies
Sharks → fast and chase you
Enemy submarines → slower but stronger
Corals → stationary hazards
Enemies follow and attack the player, and more spawn as you move forward.

Combat
You shoot torpedoes to destroy enemies
Simple collision detection is used
In special mode, bullets can track enemies automatically

Resources
Oxygen (constantly decreases)
Extra lives
Coins
You must keep collecting oxygen to stay alive.

Minimap
A small map shows nearby enemies, items, and the treasure
Always points you in the right direction

Boss
A Giant Fish appears sometimes
It chases you and becomes faster when low on health
Defeating it gives a big reward

Special Modes
Cheat Mode → auto-aim, fast shooting, invincibility
Challenging Mode → darker environment + hidden jellyfish enemies (press )

Goal
Reach the treasure after passing checkpoints
Each level gets harder (faster enemies, more danger)
You lose if you run out of lives or oxygen
## Controls Guide

Movement

Key  Action :
| W | Move forward in the direction the submarine is currently facing |
| S | Move backward |
| A | Rotate the submarine left (counter-clockwise) by 5° per press |
| D | Rotate the submarine right (clockwise) by 5° per press |
| Q | Rise upward (capped at height 400) |
| E | Dive downward (capped at minimum height 15, just above the seabed) |

Movement speed increases slightly each level — `speed = base_speed + level × 0.5` — so the submarine feels faster as the game progresses.

---

Combat

Key Action :
| Z | Rotate the gun turret left by 8° per press |
| X | Rotate the gun turret right by 8° per press |
| SPACE | Fire a torpedo in the direction the gun is currently pointing |
| Left Click | Also fires a torpedo (same as SPACE) |

The gun rotates independently of the submarine body, so you can aim sideways or even backward while moving forward.

---

Game Modes

Key Action 
| C | Toggle Cheat Mode — costs 100 coins, enables auto-aim and homing torpedoes |
| H | Toggle Challenging Mode — blinking lights, jellyfish hunt you in the dark |

---

System

Key Action 
| R | Restart the game from scratch |
| P | Pause and unpause |
| ENTER | Advance to the next level after reaching the treasure |
| Right Click | Toggle between follow-camera (tracks the submarine) and free-orbit camera |

---

Camera (Arrow Keys)

Key Action

| ↑ | Move camera higher (max 900 units) |
| ↓ | Move camera lower (min 50 units) |
| ← | Orbit camera left around the scene |
| → | Orbit camera right around the scene |
