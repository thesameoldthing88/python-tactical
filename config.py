# config.py - Central constants, weapon database, AI params, game rules
# Optimized for low-end hardware (toaster mode)

import math
from ursina import color

# === RENDER / PERFORMANCE ===
TOASTER_MODE = True          # Staggered AI, simple colliders, no heavy effects
TARGET_FPS = 60
FOV_DEFAULT = 75
MOUSE_SENSITIVITY = 1.5

# === COLORS (Stylized low-poly tactical palette) ===
# Using proper Ursina color objects so Entity() accepts them
COLORS = {
    'player':      color.rgb(0.2, 0.6, 1.0),
    'team_blue':   color.rgb(0.1, 0.4, 0.9),
    'team_red':    color.rgb(0.9, 0.2, 0.2),
    'wall':        color.rgb(0.35, 0.35, 0.38),
    'crate':       color.rgb(0.45, 0.38, 0.25),
    'sandbag':     color.rgb(0.55, 0.45, 0.3),
    'accent':      color.gold,
    'crosshair':   color.white,
    'hitmarker':   color.rgb(1, 0.9, 0.3),
    'health':      color.rgb(0.2, 0.9, 0.3),
    'ammo':        color.rgb(1.0, 0.9, 0.3),
}

# === WEAPONS DATABASE ===
WEAPONS = {
    'm4': {
        'name': 'M4A1',
        'damage': 28,
        'mag_size': 30,
        'reserve': 120,
        'fire_rate': 0.09,          # seconds between shots
        'reload_time': 1.8,
        'ads_fov': 50,
        'spread_hip': 0.08,
        'spread_ads': 0.02,
        'recoil_pitch': 1.4,
        'recoil_yaw': 0.4,
        'range': 80,
    },
    'l96': {
        'name': 'L96',
        'damage': 100,
        'mag_size': 5,
        'reserve': 15,
        'fire_rate': 1.4,
        'reload_time': 2.8,
        'ads_fov': 15,
        'spread_hip': 0.30,
        'spread_ads': 0.0,
        'recoil_pitch': 4.2,
        'recoil_yaw': 0.8,
        'range': 200,
    },
    'usp': {
        'name': 'USP',
        'damage': 34,
        'mag_size': 12,
        'reserve': 36,
        'fire_rate': 0.22,
        'reload_time': 1.1,
        'ads_fov': 65,
        'spread_hip': 0.04,
        'spread_ads': 0.01,
        'recoil_pitch': 0.7,
        'recoil_yaw': 0.2,
        'range': 50,
    }
}

# === AI DIFFICULTIES ===
DIFFICULTIES = {
    'recruit':    {'reaction': 1.2, 'accuracy': 0.15, 'speed': 3.5, 'name': 'Recruit'},
    'regular':    {'reaction': 0.6, 'accuracy': 0.35, 'speed': 4.2, 'name': 'Regular'},
    'hardened':   {'reaction': 0.3, 'accuracy': 0.55, 'speed': 5.0, 'name': 'Hardened'},
    'veteran':    {'reaction': 0.1, 'accuracy': 0.75, 'speed': 5.8, 'name': 'Veteran'},
}

# === GAME RULES ===
GAME_MODES = ['tdm', 'ctf', 'dom', 'demo', 'ffa']
DEFAULT_MODE = 'tdm'
MATCH_TIME = 300              # 5 minutes
TDM_KILL_LIMIT = 30
FFA_KILL_LIMIT = 20
DOM_SCORE_LIMIT = 200
CTF_CAPTURE_LIMIT = 3
DEMO_ROUNDS = 3

BOT_COUNT = 8
DEFAULT_DIFFICULTY = 'regular'

# === PHYSICS / MOVEMENT ===
PLAYER_SPEED = 6.0
SPRINT_MULTIPLIER = 1.65
CROUCH_SPEED = 3.0
JUMP_HEIGHT = 5.5
SLIDE_DURATION = 0.75
STAMINA_MAX = 100
STAMINA_DRAIN = 25
STAMINA_REGEN = 18

HEALTH_MAX = 100
HEALTH_REGEN_DELAY = 4.0
HEALTH_REGEN_RATE = 25

# === MAP ===
MAP_SIZE = 120
WAYPOINT_COUNT = 48

# === HUD ===
KILLFEED_SIZE = 5
RADAR_RANGE = 35
