# bot.py - FSM AI with staggered vision, pathfinding, objective awareness
from ursina import *
from config import DIFFICULTIES, COLORS, MAP_SIZE
from map_manager import MapManager
import random
import time

class Bot(Entity):
    def __init__(self, difficulty='regular', team='red', name=None, map_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.team = team
        self.name = name or f"Bot_{random.randint(100,999)}"
        self.kills = 0
        self.deaths = 0

        diff = DIFFICULTIES[difficulty]
        self.reaction = diff['reaction']
        self.accuracy = diff['accuracy']
        self.move_speed = diff['speed']

        self.health = 100
        self.state = 'roam'
        self.target = None
        self.current_path = []
        self.path_index = 0
        self.last_vision_check = 0
        self.last_shot_time = 0
        self.map_manager = map_manager
        self.last_position = self.position

        self.build_character()

    def update(self):
        if not self.enabled:
            return

        self._vision_check()
        if self.state == 'roam':
            self._roam_behavior()
        elif self.state == 'chase':
            self._chase_behavior()
        elif self.state == 'engage':
            self._engage_behavior()
        elif self.state == 'retreat':
            self._retreat_behavior()

        # Gravity and ground check (prevents floating)
        if self.y > 1.0:
            self.y -= 25 * time.dt
        if self.y < 1.0:
            self.y = 1.0

    def _vision_check(self):
        # Scan for closest enemy
        closest_enemy = None
        closest_dist = 45
        for e in scene.entities:
            if hasattr(e, 'health') and e.health > 0 and hasattr(e, 'team') and e.team != self.team and e != self:
                d = distance(self, e)
                if d < closest_dist:
                    closest_dist = d
                    closest_enemy = e
        self.target = closest_enemy

        if not self.target:
            self.state = 'roam'
            return

        dist = distance(self, self.target)
        if dist > 45:
            self.state = 'roam'
            return

        # Within FOV cone (~110 degrees)
        forward = self.forward
        to_target = (self.target.position - self.position).normalized()
        dot = forward.dot(to_target)
        if dot > 0.4:
            self.state = 'engage'
        else:
            self.state = 'chase'

    def _roam_behavior(self):
        if not self.current_path or self.path_index >= len(self.current_path):
            # Pick random waypoint or objective
            if self.map_manager:
                goal = random.randint(0, len(self.map_manager.waypoints) - 1)
                start = self.map_manager.get_nearest_waypoint(self.position)
                self.current_path = self.map_manager.find_path(start, goal)
                self.path_index = 0
        self._follow_path()

    def _chase_behavior(self):
        if self.target:
            goal = self.map_manager.get_nearest_waypoint(self.target.position)
            start = self.map_manager.get_nearest_waypoint(self.position)
            self.current_path = self.map_manager.find_path(start, goal)
            self.path_index = 0
            self._follow_path()

    def _engage_behavior(self):
        if not self.target or not self.target.enabled:
            self.state = 'roam'
            return

        # Face target but keep body upright (Y-only rotation)
        target_pos = Vec3(self.target.x, self.y, self.target.z)
        self.look_at(target_pos)
        self.rotation_x = 0
        self.rotation_z = 0

        # Fire at target
        now = time.time()
        if now - self.last_shot_time > 0.18:
            self.last_shot_time = now
            if random.random() < self.accuracy * 0.55:
                # Spawn tracer (thin box instead of cylinder)
                dist = distance(self.position, self.target.position)
                tracer = Entity(model='cube', scale=(0.04, dist, 0.04),
                                position=(self.position + self.target.position) / 2,
                                rotation=self.rotation, color=color.yellow)
                tracer.animate_scale((0.0, dist, 0.0), duration=0.08, curve=curve.linear)
                destroy(tracer, delay=0.1)
                self.target.take_damage(18)
                if self.target.health <= 0:
                    self.kills += 1

    def _retreat_behavior(self):
        # Run to nearest safe waypoint
        if self.map_manager and not self.current_path:
            safe_nodes = [i for i in range(len(self.map_manager.waypoints))]
            goal = random.choice(safe_nodes)
            start = self.map_manager.get_nearest_waypoint(self.position)
            self.current_path = self.map_manager.find_path(start, goal)
            self.path_index = 0
        self._follow_path()

    def _follow_path(self):
        if not self.current_path or self.path_index >= len(self.current_path):
            return
        target_wp = self.map_manager.waypoints[self.current_path[self.path_index]]
        direction = (target_wp.position - self.position).normalized()
        self.position += direction * self.move_speed * time.dt
        
        # Y-only look_at to prevent tilting or flipping upside down
        target_pos = Vec3(target_wp.x, self.y, target_wp.z)
        self.look_at(target_pos)
        self.rotation_x = 0
        self.rotation_z = 0

        if distance(self, target_wp) < 2.5:
            self.path_index += 1

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 35:
            self.state = 'retreat'
        if self.health <= 0:
            self.die()

    def die(self):
        self.enabled = False
        # Respawn handled by game_modes

    def build_character(self):
        # Improved low-poly enemy soldier (arms and legs)
        body_color = COLORS['team_red'] if self.team == 'red' else COLORS['team_blue']
        self.body = Entity(parent=self, model='cube', scale=(0.8, 1.1, 0.4), 
                           position=(0, 1.0, 0), color=body_color, collider=None)
        self.head = Entity(parent=self, model='sphere', scale=0.55, 
                           position=(0, 2.0, 0), color=color.rgb(0.95, 0.75, 0.65), collider=None)
        self.helmet = Entity(parent=self.head, model='cube', scale=(0.65, 0.45, 0.7), 
                             position=(0, 0.25, 0), color=color.dark_gray, collider=None)
        # Arms
        self.left_arm = Entity(parent=self, model='cube', scale=(0.25, 0.9, 0.25), 
                               position=(-0.6, 1.1, 0), color=body_color, collider=None)
        self.right_arm = Entity(parent=self, model='cube', scale=(0.25, 0.9, 0.25), 
                                position=(0.6, 1.1, 0), color=body_color, collider=None)
        # Legs
        self.left_leg = Entity(parent=self, model='cube', scale=(0.3, 1.0, 0.3), 
                               position=(-0.3, 0.3, 0), color=color.dark_gray, collider=None)
        self.right_leg = Entity(parent=self, model='cube', scale=(0.3, 1.0, 0.3), 
                                position=(0.3, 0.3, 0), color=color.dark_gray, collider=None)
        self.collider = 'box'  # Main collider on root
        self.scale = (1, 1, 1)
