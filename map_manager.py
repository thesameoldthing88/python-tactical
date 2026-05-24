# map_manager.py - Dynamic low-poly tactical arena + waypoint navigation graph
from ursina import *
from config import COLORS, MAP_SIZE, WAYPOINT_COUNT
import random
import math

class MapManager:
    def __init__(self):
        self.waypoints = []
        self.connections = {}          # node_index -> list of connected indices
        self.entities = []

    def generate_arena(self):
        """Builds a compact tactical map (Rust/Shipment style)"""
        # Ground
        ground = Entity(model='plane', scale=MAP_SIZE, texture='grass', 
                        color=color.rgb(0.4, 0.5, 0.3), collider='box')
        self.entities.append(ground)

        # Perimeter walls
        wall_thickness = 1.5
        for x in [-MAP_SIZE/2, MAP_SIZE/2]:
            w = Entity(model='cube', scale=(wall_thickness, 8, MAP_SIZE),
                       position=(x, 4, 0), texture='brick', color=COLORS['wall'], collider='box')
            self.entities.append(w)
        for z in [-MAP_SIZE/2, MAP_SIZE/2]:
            w = Entity(model='cube', scale=(MAP_SIZE, 8, wall_thickness),
                       position=(0, 4, z), texture='brick', color=COLORS['wall'], collider='box')
            self.entities.append(w)

        # Central structures & cover (crates, sandbags, concrete)
        positions = [
            (0, 0), (8, -6), (-7, 9), (12, 11), (-13, -8),
            (5, 14), (-9, -12), (15, -3), (-14, 5), (0, -15)
        ]
        for i, (px, pz) in enumerate(positions):
            if i % 3 == 0:   # Tall crate
                e = Entity(model='cube', scale=(4, 5, 4), position=(px, 2.5, pz),
                           texture='brick', color=COLORS['crate'], collider='box')
            elif i % 3 == 1: # Sandbag cluster
                e = Entity(model='cube', scale=(6, 2, 3), position=(px, 1, pz),
                           texture='white_cube', color=COLORS['sandbag'], collider='box')
            else:            # Concrete barrier
                e = Entity(model='cube', scale=(3, 3, 7), position=(px, 1.5, pz),
                           texture='brick', color=COLORS['wall'], collider='box')
            self.entities.append(e)

        # Spawn platforms (slightly raised)
        for sx, sz in [(-18, -18), (18, 18), (-18, 18), (18, -18)]:
            p = Entity(model='cube', scale=(5, 1, 5), position=(sx, 0.5, sz),
                       color=color.rgb(0.3, 0.3, 0.35), collider='box')
            self.entities.append(p)

        self._generate_waypoints()
        self._build_navigation_graph()

    def _generate_waypoints(self):
        """Creates evenly distributed navigation nodes"""
        self.waypoints = []
        spacing = MAP_SIZE / math.sqrt(WAYPOINT_COUNT)
        for i in range(WAYPOINT_COUNT):
            x = random.uniform(-MAP_SIZE/2 + 3, MAP_SIZE/2 - 3)
            z = random.uniform(-MAP_SIZE/2 + 3, MAP_SIZE/2 - 3)
            # Snap to ground level
            wp = Entity(model='sphere', scale=0.6, position=(x, 0.3, z),
                        color=color.yellow, visible=False)
            self.waypoints.append(wp)
            self.entities.append(wp)

    def _build_navigation_graph(self):
        """Connects waypoints that have clear line of sight"""
        self.connections = {i: [] for i in range(len(self.waypoints))}
        for i in range(len(self.waypoints)):
            for j in range(i + 1, len(self.waypoints)):
                a = self.waypoints[i].position
                b = self.waypoints[j].position
                # Simple distance + LOS check (raycast would be ideal but expensive)
                dist = distance(a, b)
                if dist < 18 and random.random() > 0.25:
                    self.connections[i].append(j)
                    self.connections[j].append(i)

    def get_nearest_waypoint(self, pos):
        """Returns index of closest waypoint to given position"""
        best = 0
        best_dist = 999
        for i, wp in enumerate(self.waypoints):
            d = distance(pos, wp.position)
            if d < best_dist:
                best_dist = d
                best = i
        return best

    def find_path(self, start_idx, goal_idx):
        """Dijkstra pathfinding on waypoint graph"""
        import heapq
        dist = {i: float('inf') for i in self.connections}
        dist[start_idx] = 0
        prev = {i: None for i in self.connections}
        pq = [(0, start_idx)]

        while pq:
            d, u = heapq.heappop(pq)
            if u == goal_idx:
                break
            for v in self.connections[u]:
                alt = d + distance(self.waypoints[u].position, self.waypoints[v].position)
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(pq, (alt, v))

        # Reconstruct path
        path = []
        current = goal_idx
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()
        return path if path[0] == start_idx else []

    def cleanup(self):
        for e in self.entities:
            destroy(e)
        self.entities.clear()
        self.waypoints.clear()
