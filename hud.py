# hud.py - Modern tactical HUD (radar, killfeed, hitmarkers, scoreboard)
from ursina import *
from config import COLORS, KILLFEED_SIZE, RADAR_RANGE
import time

class HUD:
    def __init__(self):
        self.killfeed = []
        self.hitmarker = None
        self.radar = None
        self.score_text = None
        self.ammo_text = None
        self.health_bar = None
        self.scoreboard_panel = None
        self.scoreboard_text = None

        self._create_elements()

    def _create_elements(self):
        # Top-center score / objective
        self.score_text = Text(text='', position=(0, 0.45), scale=1.2,
                               color=COLORS['accent'], origin=(0, 0))

        # Bottom-right ammo
        self.ammo_text = Text(text='30 / 120', position=(0.75, -0.45), scale=1.1,
                              color=COLORS['ammo'], origin=(1, 0))

        # Bottom-left health
        self.health_bar = Entity(parent=camera.ui, model='quad',
                                 scale=(0.25, 0.03), position=(-0.6, -0.45),
                                 color=COLORS['health'])

        # Radar (top-left)
        self.radar = Entity(parent=camera.ui, model='circle', scale=0.18,
                            position=(-0.75, 0.35), color=color.rgba(0, 0, 0, 0.6))

        # Hitmarker (center)
        self.hitmarker = Entity(parent=camera.ui, model='quad', scale=0.04,
                                color=COLORS['hitmarker'], visible=False)

        # Scoreboard panel (hidden by default)
        self.scoreboard_panel = Entity(parent=camera.ui, model='quad', scale=(0.65, 0.7),
                                       color=color.rgba(0, 0, 0, 0.85), visible=False, z=1)
        self.scoreboard_text = Text(parent=self.scoreboard_panel, text='', position=(-0.45, 0.4),
                                    scale=1.4, color=color.white, origin=(-0.5, 0.5))

    def update_score(self, text):
        self.score_text.text = text

    def update_ammo(self, current, reserve):
        self.ammo_text.text = f'{current} / {reserve}'

    def update_health(self, hp):
        self.health_bar.scale_x = 0.25 * (hp / 100)

    def show_hitmarker(self):
        self.hitmarker.visible = True
        invoke(lambda: setattr(self.hitmarker, 'visible', False), delay=0.12)

    def add_killfeed(self, text):
        self.killfeed.append(text)
        if len(self.killfeed) > KILLFEED_SIZE:
            self.killfeed.pop(0)
        # Simple text display (expand with proper Text entities)
        print('[KILLFEED]', text)   # placeholder for full UI

    def show_scoreboard(self, players, show=True):
        self.scoreboard_panel.visible = show
        if show and players:
            text_str = "SCOREBOARD\n\nNAME         KILLS    DEATHS\n" + "="*35 + "\n"
            for p in players:
                text_str += f"{p.get('name','?'):<12} {p.get('kills',0):<8} {p.get('deaths',0)}\n"
            self.scoreboard_text.text = text_str
        elif not show:
            self.scoreboard_text.text = ''

    def cleanup(self):
        for e in [self.score_text, self.ammo_text, self.health_bar,
                  self.radar, self.hitmarker, self.scoreboard_panel, self.scoreboard_text]:
            if e:
                destroy(e)
