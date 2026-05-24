# player.py - Advanced FPS controller with sprint, slide, crouch, health regen
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from config import *
import time

class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.team = 'blue'
        self.name = 'Player'
        self.kills = 0
        self.deaths = 0
        self.health = HEALTH_MAX
        self.last_damage_time = time.time()
        self.speed = PLAYER_SPEED
        self.sprinting = False
        self.crouching = False
        self.sliding = False
        self.slide_timer = 0
        self.stamina = STAMINA_MAX
        self.fov = FOV_DEFAULT
        self.cursor.visible = False  # We use custom crosshair

        # Build simple soldier model (visible character)
        self.build_character()

        # Custom crosshair
        self.crosshair = Entity(parent=camera.ui, model='quad', scale=0.018, color=COLORS['crosshair'], z=0)
        self.ch_lines = []
        for i in range(4):
            line = Entity(parent=camera.ui, model='quad', scale=(0.025 if i % 2 == 0 else 0.004, 0.004 if i % 2 == 0 else 0.025),
                          color=COLORS['crosshair'], z=0)
            self.ch_lines.append(line)

    def update(self):
        super().update()  # FirstPersonController handles movement, collision, mouse look, gravity, jump
        self._handle_sprint_and_crouch()
        self._handle_regen()
        self._handle_camera_bob()
        self._update_crosshair()

    def _handle_sprint_and_crouch(self):
        # Sprint
        self.sprinting = held_keys['shift'] and self.stamina > 10 and not self.crouching
        if self.sprinting:
            self.speed = PLAYER_SPEED * SPRINT_MULTIPLIER
            self.stamina = max(0, self.stamina - STAMINA_DRAIN * time.dt)
            camera.fov = lerp(camera.fov, self.fov + 8, 8 * time.dt)
        else:
            self.speed = PLAYER_SPEED
            self.stamina = min(STAMINA_MAX, self.stamina + STAMINA_REGEN * time.dt)
            camera.fov = lerp(camera.fov, self.fov, 6 * time.dt)

        # Crouch
        if held_keys['c']:
            self.crouching = True
            camera.y = 1.1
            self.speed = CROUCH_SPEED
            if hasattr(self, 'body'):
                self.body.y = 0.6
                self.head.y = 1.4
                if hasattr(self, 'left_leg'): self.left_leg.y = 0.1
                if hasattr(self, 'right_leg'): self.right_leg.y = 0.1
        else:
            self.crouching = False
            camera.y = 1.8
            if hasattr(self, 'body'):
                self.body.y = 1.0
                self.head.y = 2.0
                if hasattr(self, 'left_leg'): self.left_leg.y = 0.3
                if hasattr(self, 'right_leg'): self.right_leg.y = 0.3

    def _handle_regen(self):
        if time.time() - self.last_damage_time > HEALTH_REGEN_DELAY:
            if self.health < HEALTH_MAX:
                self.health = min(HEALTH_MAX, self.health + HEALTH_REGEN_RATE * time.dt)

    def _update_crosshair(self):
        # Position crosshair lines in center of screen
        for i, line in enumerate(self.ch_lines):
            if i == 0:   # left
                line.position = (-0.02, 0)
            elif i == 1: # right
                line.position = (0.02, 0)
            elif i == 2: # top
                line.position = (0, 0.02)
            else:        # bottom
                line.position = (0, -0.02)

    def _handle_camera_bob(self):
        target_cam_y = 1.1 if self.crouching else 1.8
        if self.sprinting or (self.speed > 4 and not self.crouching):
            bob = math.sin(time.time() * 12) * 0.025
            camera.y = lerp(camera.y, target_cam_y + bob, 12 * time.dt)
        else:
            camera.y = lerp(camera.y, target_cam_y, 10 * time.dt)

    def take_damage(self, amount, direction=None):
        self.health -= amount
        self.last_damage_time = time.time()
        if self.health <= 0:
            self.die()

    def die(self):
        self.health = 0
        # Death handled by game_modes

    def respawn(self, pos):
        self.position = pos
        self.health = HEALTH_MAX
        self.stamina = STAMINA_MAX
        self.sliding = False
        self.crouching = False

    def build_character(self):
        # Improved low-poly soldier (less blocky with arms and legs)
        self.body = Entity(parent=self, model='cube', scale=(0.8, 1.1, 0.4), 
                           position=(0, 1.0, 0), color=color.azure, collider=None)
        self.head = Entity(parent=self, model='sphere', scale=0.55, 
                           position=(0, 2.0, 0), color=color.rgb(0.95, 0.75, 0.65), collider=None)
        self.helmet = Entity(parent=self.head, model='cube', scale=(0.65, 0.45, 0.7), 
                             position=(0, 0.25, 0), color=color.dark_gray, collider=None)
        # Arms
        self.left_arm = Entity(parent=self, model='cube', scale=(0.25, 0.9, 0.25), 
                               position=(-0.6, 1.1, 0), color=color.azure, collider=None)
        self.right_arm = Entity(parent=self, model='cube', scale=(0.25, 0.9, 0.25), 
                                position=(0.6, 1.1, 0), color=color.azure, collider=None)
        # Legs
        self.left_leg = Entity(parent=self, model='cube', scale=(0.3, 1.0, 0.3), 
                               position=(-0.3, 0.3, 0), color=color.dark_gray, collider=None)
        self.right_leg = Entity(parent=self, model='cube', scale=(0.3, 1.0, 0.3), 
                                position=(0.3, 0.3, 0), color=color.dark_gray, collider=None)
        self.collider = 'box'  # Main collider on root (used by FirstPersonController)
        self.scale = (1, 1, 1)
        self.height = 2.0
