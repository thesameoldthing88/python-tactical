# main.py - Entry point, menus, game loop, full integration
from ursina import *
from config import *
from map_manager import MapManager
from player import Player
from weapon import Weapon
from bot import Bot
from game_modes import TeamDeathmatch, CaptureTheFlag, Domination, Demolition, FreeForAll
from hud import HUD
import random

app = Ursina(title='Project: Python-Tactical', borderless=False, vsync=True)
window.size = (1280, 720)
window.color = color.black

# Global state
current_mode = None
player = None
weapon = None
bots = []
map_manager = None
hud = None
game_state = 'menu'
menu_elements = []

def start_match(mode='tdm', bot_count=BOT_COUNT, difficulty=DEFAULT_DIFFICULTY):
    global current_mode, player, weapon, bots, map_manager, hud, game_state, menu_elements

    game_state = 'playing'
    for el in menu_elements:
        destroy(el)
    menu_elements.clear()

    map_manager = MapManager()
    map_manager.generate_arena()

    # Player - safe spawn above ground to avoid spawning inside objects
    player = Player()
    player.position = (0, 5, 0)
    player.gravity = 1.0
    player.jump_height = JUMP_HEIGHT
    weapon = Weapon('m4')
    player.add_script(weapon)   # attach weapon to player

    # Game Mode
    if mode == 'tdm':
        current_mode = TeamDeathmatch(map_manager=map_manager)
    elif mode == 'ctf':
        current_mode = CaptureTheFlag(map_manager=map_manager)
    elif mode == 'dom':
        current_mode = Domination(map_manager=map_manager)
    elif mode == 'demo':
        current_mode = Demolition(map_manager=map_manager)
    elif mode == 'ffa':
        current_mode = FreeForAll(map_manager=map_manager)

    # Bots - safe spawn above ground
    bots = []
    for i in range(bot_count):
        team = 'red' if i % 2 == 0 else 'blue'
        b = Bot(difficulty=difficulty, team=team, map_manager=map_manager)
        b.position = (random.uniform(-25, 25), 5, random.uniform(-25, 25))
        bots.append(b)

    hud = HUD()
    mouse.locked = True
    # Improve visuals - add sky and fog to fix horizon when looking down
    Sky()
    scene.fog_density = 0.035
    scene.fog_color = color.rgb(0.6, 0.7, 0.85)
    DirectionalLight(y=2, rotation=(45, -45, 45), shadows=True)
    AmbientLight(color=color.rgb(0.6, 0.6, 0.7))

def update():
    global game_state
    if game_state != 'playing':
        return

    # Simple win check
    winner = current_mode.update() if current_mode else None
    if winner:
        print(f'WINNER: {winner}')
        game_state = 'end'

    # HUD updates
    if hud and player and weapon:
        hud.update_health(player.health)
        hud.update_ammo(weapon.ammo, weapon.reserve)
        hud.update_score(f'{current_mode.mode.upper()} | {int(time.time() - current_mode.start_time)}s')

    # Input
    if held_keys['escape']:
        application.quit()
    if hud:
        if held_keys['tab']:
            player_list = [{'name': e.name, 'kills': getattr(e, 'kills', 0), 'deaths': getattr(e, 'deaths', 0)} for e in [player] + bots]
            hud.show_scoreboard(player_list, show=True)
        else:
            hud.show_scoreboard([], show=False)

    if game_state == 'end' and held_keys['r']:
        # Restart
        for b in bots:
            destroy(b)
        destroy(player)
        destroy(weapon)
        destroy(map_manager)
        game_state = 'menu'
        main_menu()

def input(key):
    global weapon, game_state
    if game_state == 'menu':
        input_menu(key)
        return

    if game_state != 'playing' or not weapon:
        return

    if key == 'left mouse down':
        if weapon.shoot():
            hud.show_hitmarker() if hud else None
    if key == 'r':
        weapon.reload()
    if key == 'right mouse down':
        weapon.start_ads()
    if key == 'right mouse up':
        weapon.stop_ads()
    if key == '1':
        weapon.switch_weapon('m4')
    if key == '2':
        weapon.switch_weapon('l96')
    if key == '3':
        weapon.switch_weapon('usp')

# === MAIN MENU (simple text for now) ===
def main_menu():
    global menu_elements
    title = Text('PROJECT: PYTHON-TACTICAL', scale=3, y=0.3, color=color.gold, origin=(0,0))
    inst = Text('Press 1 = TDM | 2 = CTF | 3 = Domination | 4 = Demolition | 5 = FFA', scale=1.2, y=0, origin=(0,0))
    quit_txt = Text('Q = Quit', scale=1, y=-0.2, origin=(0,0))
    menu_elements = [title, inst, quit_txt]

def input_menu(key):
    global game_state
    if key == '1':
        start_match('tdm')
    elif key == '2':
        start_match('ctf')
    elif key == '3':
        start_match('dom')
    elif key == '4':
        start_match('demo')
    elif key == '5':
        start_match('ffa')
    elif key == 'q':
        application.quit()

main_menu()
app.run()
