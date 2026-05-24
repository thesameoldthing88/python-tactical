# weapon.py - Weapon system with ADS, procedural recoil, sway, reload
from ursina import *
from config import WEAPONS, COLORS
import time
import random

class Weapon(Entity):
    def __init__(self, weapon_id='m4', **kwargs):
        super().__init__(**kwargs)
        self.weapon_id = weapon_id
        self.stats = WEAPONS[weapon_id]
        self.ammo = self.stats['mag_size']
        self.reserve = self.stats['reserve']
        self.is_reloading = False
        self.last_shot = 0
        self.ads = False
        self.recoil_offset = Vec3(0)
        self.sway_offset = Vec3(0)

        # Visual model (low-poly stylized)
        self.model = 'cube'
        self.scale = (0.3, 0.4, 1.8) if weapon_id != 'l96' else (0.25, 0.35, 2.4)
        self.color = color.rgb(0.15, 0.15, 0.18)
        self.parent = camera
        self.position = (0.6, -0.4, 1.2)

    def update(self):
        self._handle_sway()
        self._handle_recoil_recovery()

    def _handle_sway(self):
        # Mouse drag inertia + walk sway
        target_sway = Vec3(mouse.velocity.x * 0.8, mouse.velocity.y * -0.6, 0)
        self.sway_offset = lerp(self.sway_offset, target_sway, 12 * time.dt)
        self.rotation = self.sway_offset * 3

        # Gentle walk bob
        if not self.ads:
            bob = math.sin(time.time() * 8) * 0.02
            self.y = -0.4 + bob
        else:
            self.y = lerp(self.y, -0.35, 10 * time.dt)

    def _handle_recoil_recovery(self):
        # Smooth recoil recovery (counter the upward kick)
        self.recoil_offset = lerp(self.recoil_offset, Vec3(0), 15 * time.dt)
        camera.rotation_x += self.recoil_offset.y * 18 * time.dt  # Positive to bring aim back down

    def shoot(self):
        if self.is_reloading or self.ammo <= 0:
            if self.ammo <= 0:
                self.reload()
            return False

        now = time.time()
        if now - self.last_shot < self.stats['fire_rate']:
            return False
        self.last_shot = now
        self.ammo -= 1

        # Procedural recoil
        pitch = self.stats['recoil_pitch'] * (0.7 if self.ads else 1.0)
        yaw = random.uniform(-self.stats['recoil_yaw'], self.stats['recoil_yaw'])
        self.recoil_offset += Vec3(yaw, pitch, 0)
        camera.rotation_x -= pitch * 0.6

        # Visual kick (ADS-aware)
        target_z = 0.9 if self.ads else 1.2
        self.z = target_z - 0.15
        invoke(lambda s=self, tz=target_z: setattr(s, 'z', tz), delay=0.08)

        # Raycast shooting
        hit_info = raycast(camera.world_position, camera.forward, distance=self.stats['range'], ignore=(self, camera))
        if hit_info.hit:
            Entity(model='sphere', scale=0.12, position=hit_info.point, color=color.orange, time_to_live=0.4)
            if hasattr(hit_info.entity, 'take_damage'):
                hit_info.entity.take_damage(self.stats['damage'])
                return 'hit'
        return True

    def start_ads(self):
        self.ads = True
        target_pos = (0, -0.35, 0.9)
        self.animate_position(target_pos, duration=0.12, curve=curve.out_quad)
        camera.animate('fov', self.stats['ads_fov'], duration=0.12)

    def stop_ads(self):
        self.ads = False
        target_pos = (0.6, -0.4, 1.2)
        self.animate_position(target_pos, duration=0.15, curve=curve.out_quad)
        camera.animate('fov', 75, duration=0.15)

    def reload(self):
        if self.is_reloading or self.reserve <= 0 or self.ammo == self.stats['mag_size']:
            return
        self.is_reloading = True

        # Animation: pull down, rotate, push up
        self.animate_position((0.6, -1.2, 1.2), duration=0.25)
        invoke(self._finish_reload, delay=self.stats['reload_time'])

    def _finish_reload(self):
        needed = self.stats['mag_size'] - self.ammo
        take = min(needed, self.reserve)
        self.ammo += take
        self.reserve -= take
        self.is_reloading = False
        self.position = (0.6, -0.4, 1.2)
        self.rotation = (0, 0, 0)

    def switch_weapon(self, new_id):
        self.stop_ads()
        self.weapon_id = new_id
        self.stats = WEAPONS[new_id]
        self.ammo = self.stats['mag_size']
        self.reserve = self.stats['reserve']
        self.scale = (0.3, 0.4, 1.8) if new_id != 'l96' else (0.25, 0.35, 2.4)
        self.position = (0.6, -0.4, 1.2)
