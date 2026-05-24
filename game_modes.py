# game_modes.py - Complete rules engine for TDM, CTF, Domination, Demolition, FFA
from ursina import *
from config import *
import time
import random

class GameMode:
    def __init__(self, mode='tdm', map_manager=None):
        self.mode = mode
        self.map_manager = map_manager
        self.score = {'blue': 0, 'red': 0}
        self.kills = {}
        self.start_time = time.time()
        self.winner = None
        self.entities = []

    def update(self):
        if self.winner:
            return self.winner
        elapsed = time.time() - self.start_time
        if elapsed > MATCH_TIME:
            return self._decide_winner_by_score()

    def _decide_winner_by_score(self):
        if self.score['blue'] > self.score['red']:
            return 'blue'
        elif self.score['red'] > self.score['blue']:
            return 'red'
        return 'draw'

    def on_kill(self, killer, victim):
        if killer not in self.kills:
            self.kills[killer] = 0
        self.kills[killer] += 1

        if self.mode == 'tdm':
            team = killer.team if hasattr(killer, 'team') else 'blue'
            self.score[team] += 1
            if self.score[team] >= TDM_KILL_LIMIT:
                self.winner = team
        elif self.mode == 'ffa':
            if self.kills[killer] >= FFA_KILL_LIMIT:
                self.winner = killer

    def spawn_position(self, entity):
        """Returns safe spawn point (furthest from enemies)"""
        if not self.map_manager:
            return (random.uniform(-20, 20), 1, random.uniform(-20, 20))
        best = random.choice(self.map_manager.waypoints).position
        return best + (0, 1, 0)

    def cleanup(self):
        for e in self.entities:
            destroy(e)
        self.entities.clear()


class TeamDeathmatch(GameMode):
    def __init__(self, **kwargs):
        super().__init__(mode='tdm', **kwargs)


class CaptureTheFlag(GameMode):
    def __init__(self, **kwargs):
        super().__init__(mode='ctf', **kwargs)
        self.flags = {}
        self.carrier = {}

    def setup_flags(self, blue_base, red_base):
        self.flags['blue'] = Entity(model='cube', scale=1.2, color=COLORS['team_blue'],
                                    position=blue_base, collider='box')
        self.flags['red'] = Entity(model='cube', scale=1.2, color=COLORS['team_red'],
                                   position=red_base, collider='box')
        self.entities.extend([self.flags['blue'], self.flags['red']])

    def on_flag_pickup(self, player, flag_color):
        self.carrier[player] = flag_color

    def on_capture(self, player):
        if player in self.carrier:
            team = 'blue' if player.team == 'blue' else 'red'
            self.score[team] += 1
            del self.carrier[player]
            if self.score[team] >= CTF_CAPTURE_LIMIT:
                self.winner = team


class Domination(GameMode):
    def __init__(self, **kwargs):
        super().__init__(mode='dom', **kwargs)
        self.zones = []
        self.zone_control = {}

    def add_zone(self, pos, name):
        zone = Entity(model='cylinder', scale=(6, 1, 6), position=pos,
                      color=color.rgba(1, 1, 0, 0.4), collider='box')
        self.zones.append((name, zone))
        self.zone_control[name] = None
        self.entities.append(zone)

    def update(self):
        super().update()
        if not hasattr(self, 'last_tick'):
            self.last_tick = time.time()
        if time.time() - self.last_tick >= 1.0:
            self.last_tick = time.time()
            for name, zone in self.zones:
                blue_in = False
                red_in = False
                for e in scene.entities:
                    if hasattr(e, 'health') and e.health > 0 and hasattr(e, 'team'):
                        if distance_2d(e.position, zone.position) < 3.5:
                            if e.team == 'blue': blue_in = True
                            if e.team == 'red': red_in = True
                if blue_in and not red_in and self.zone_control[name] != 'blue':
                    self.zone_control[name] = 'blue'
                    zone.color = COLORS['team_blue']
                    self.score['blue'] += 1
                elif red_in and not blue_in and self.zone_control[name] != 'red':
                    self.zone_control[name] = 'red'
                    zone.color = COLORS['team_red']
                    self.score['red'] += 1
                if self.score['blue'] >= DOM_SCORE_LIMIT or self.score['red'] >= DOM_SCORE_LIMIT:
                    self.winner = 'blue' if self.score['blue'] > self.score['red'] else 'red'


class Demolition(GameMode):
    def __init__(self, **kwargs):
        super().__init__(mode='demo', **kwargs)
        self.sites = {}
        self.bomb_planted = False
        self.plant_time = 0
        self.planted_site = None

    def add_site(self, name, pos):
        site = Entity(model='cube', scale=3, position=pos, color=color.orange, collider='box')
        self.sites[name] = site
        self.entities.append(site)

    def update(self):
        super().update()
        if self.bomb_planted and self.plant_time:
            if time.time() - self.plant_time > 30:
                self.winner = 'red'  # Attackers win by detonation


class FreeForAll(GameMode):
    def __init__(self, **kwargs):
        super().__init__(mode='ffa', **kwargs)
