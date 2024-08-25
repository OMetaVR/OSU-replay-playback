import os
import pygame
import json
from pathlib import Path
from fuzzywuzzy import fuzz
import winreg
from osrparse import Replay, GameMode
import re
from enum import IntFlag, auto

class Mods(IntFlag):
    NoMod = 0
    NoFail = auto()
    Easy = auto()
    TouchDevice = auto()
    Hidden = auto()
    HardRock = auto()
    SuddenDeath = auto()
    DoubleTime = auto()
    Relax = auto()
    HalfTime = auto()
    Nightcore = auto()
    Flashlight = auto()
    Autoplay = auto()
    SpunOut = auto()
    Relax2 = auto()
    Perfect = auto()
    Key4 = auto()
    Key5 = auto()
    Key6 = auto()
    Key7 = auto()
    Key8 = auto()
    FadeIn = auto()
    Random = auto()
    Cinema = auto()
    Target = auto()
    Key9 = auto()
    KeyCoop = auto()
    Key1 = auto()
    Key3 = auto()
    Key2 = auto()
    ScoreV2 = auto()
    Mirror = auto()

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Beatmap:
    def __init__(self, file_path):
        self.file_path = file_path
        self.hit_objects = []
        self.parse_beatmap()

    def parse_beatmap(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        hit_objects_section = re.search(r'\[HitObjects\]([\s\S]*)', content)
        if hit_objects_section:
            hit_objects_data = hit_objects_section.group(1).strip().split('\n')
            print(f"Found {len(hit_objects_data)} hit object lines")
            for line in hit_objects_data:
                parts = line.split(',')
                if len(parts) >= 4:
                    x, y, time = map(int, parts[:3])
                    object_type = int(parts[3])
                    is_circle = object_type & 1
                    is_slider = object_type & 2
                    is_spinner = object_type & 8
                    if is_circle:
                        self.hit_objects.append({'type': 'circle', 'x': x, 'y': y, 'time': time})
                    elif is_slider:
                        curve_type = parts[5].split('|')[0]
                        curve_points = [list(map(int, point.split(':'))) for point in parts[5].split('|')[1:]]
                        repeat = int(parts[6])
                        pixel_length = float(parts[7])
                        self.hit_objects.append({'type': 'slider', 'x': x, 'y': y, 'time': time, 'curve_type': curve_type, 'curve_points': curve_points, 'repeat': repeat, 'pixel_length': pixel_length})
                    elif is_spinner:
                        end_time = int(parts[5])
                        self.hit_objects.append({'type': 'spinner', 'x': x, 'y': y, 'time': time, 'end_time': end_time})
                    print(f"Parsed object: type={object_type}, x={x}, y={y}, time={time}")
                else:
                    print(f"Skipped line due to insufficient parts: {line}")
        else:
            print("Could not find [HitObjects] section in the beatmap file")

        print(f"Parsed {len(self.hit_objects)} hit objects")
        if len(self.hit_objects) > 0:
            print(f"First hit object: {self.hit_objects[0]}")
            print(f"Last hit object: {self.hit_objects[-1]}")
        else:
            print("No hit objects were parsed")

class OSRPlayer:
    def __init__(self, display_width=800, display_height=600):
        self.display_width = display_width
        self.display_height = display_height
        self.osu_width = 512
        self.osu_height = 384
        self.scale_x = self.display_width / self.osu_width
        self.scale_y = self.display_height / self.osu_height
        self.replay_folder = self.get_replay_folder()
        self.replay_files = self.get_replay_files()
        self.replay = None
        self.beatmap = None
        self.active_mods = Mods.NoMod
        self.mod_buttons = []
        self.font = None

    def get_replay_folder(self):
        config_file = 'osr_player_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('replay_folder')

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\osu!") as key:
                osu_path = winreg.QueryValueEx(key, "InstallLocation")[0]
                replay_folder = os.path.join(osu_path, "Replays")
                if os.path.exists(replay_folder):
                    self.save_config(replay_folder)
                    return replay_folder
        except WindowsError:
            pass

        while True:
            folder = input("Enter the path to your osu! replay folder: ").strip()
            if os.path.exists(folder):
                self.save_config(folder)
                return folder
            print("Invalid folder path. Please try again.")

    def save_config(self, replay_folder):
        config = {'replay_folder': replay_folder}
        with open('osr_player_config.json', 'w') as f:
            json.dump(config, f)

    def get_replay_files(self):
        return [f for f in os.listdir(self.replay_folder) if f.endswith('.osr')]

    def list_replays(self):
        for i, replay in enumerate(self.replay_files, 1):
            print(f"{i}. {replay}")

    def fuzzy_match(self, query):
        matches = []
        for replay in self.replay_files:
            ratio = fuzz.partial_ratio(query.lower(), replay.lower())
            if ratio > 70:  
                matches.append((replay, ratio))
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def select_replay(self):
        self.list_replays()
        while True:
            choice = input("Enter the number or name of the replay you want to play: ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(self.replay_files):
                    return os.path.join(self.replay_folder, self.replay_files[index])
            else:
                matches = self.fuzzy_match(choice)
                if len(matches) == 1:
                    return os.path.join(self.replay_folder, matches[0][0])
                elif len(matches) > 1:
                    print("Multiple matches found:")
                    for i, (replay, _) in enumerate(matches, 1):
                        print(f"{i}. {replay}")
                    sub_choice = input("Enter the number of your choice: ").strip()
                    if sub_choice.isdigit():
                        index = int(sub_choice) - 1
                        if 0 <= index < len(matches):
                            return os.path.join(self.replay_folder, matches[index][0])
            print("Invalid selection. Please try again.")

    def load_replay(self, osr_file):
        try:
            self.replay = Replay.from_path(osr_file)
            print(f"Loaded replay: {self.replay.username} - Score: {self.replay.score}")
            print(f"Beatmap hash: {self.replay.beatmap_hash}")

            self.active_mods = Mods(self.replay.mods)
            print(f"Mods used: {self.active_mods}")

            # if your reading this, FUCK YOU!!! <3

            beatmap_path = self.find_beatmap(self.replay.beatmap_hash)
            if beatmap_path:
                print(f"Found beatmap at: {beatmap_path}")
                self.beatmap = Beatmap(beatmap_path)
                print(f"Loaded beatmap with {len(self.beatmap.hit_objects)} hit objects")
            else:
                print("Corresponding beatmap not found")
                print("Searched in:", os.path.join(os.path.dirname(self.replay_folder), 'Songs'))
        except Exception as e:
            print(f"Error loading replay file {osr_file}: {str(e)}")
            self.replay = None

    def find_beatmap(self, beatmap_hash):
        osu_folder = os.path.dirname(self.replay_folder)
        songs_folder = os.path.join(osu_folder, 'Songs')
        print(f"Searching for beatmap with hash: {beatmap_hash}")
        print(f"Searching in folder: {songs_folder}")

        cache_file = os.path.join(osu_folder, 'beatmap_cache.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                if beatmap_hash in cache:
                    file_path = cache[beatmap_hash]
                    if os.path.exists(file_path):
                        print(f"Found matching beatmap in cache: {file_path}")
                        return file_path

        for root, dirs, files in os.walk(songs_folder):
            for file in files:
                if file.endswith('.osu'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if beatmap_hash in content:
                                print(f"Found matching beatmap: {file_path}")
                                self.update_cache(beatmap_hash, file_path)
                                return file_path
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                content = f.read()
                                if beatmap_hash in content:
                                    print(f"Found matching beatmap: {file_path}")
                                    self.update_cache(beatmap_hash, file_path)
                                    return file_path
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")

        print("Beatmap not found automatically. Would you like to specify the file location manually? (y/n)")
        if input().lower() == 'y':
            return self.manual_beatmap_input()
        else:
            print("Beatmap not found")
            return None

    def update_cache(self, beatmap_hash, file_path):
        cache_file = os.path.join(os.path.dirname(self.replay_folder), 'beatmap_cache.json')
        cache = {}
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        cache[beatmap_hash] = file_path
        with open(cache_file, 'w') as f:
            json.dump(cache, f)

    def manual_beatmap_input(self):
        while True:
            file_path = input("Please enter the full path to the .osu file: ").strip()
            if os.path.exists(file_path) and file_path.endswith('.osu'):
                return file_path
            else:
                print("Invalid file path. Please try again.")

    def scale_position(self, x, y):
        return x * self.scale_x, y * self.scale_y

    def draw_hit_circle(self, screen, x, y, approach_rate=1, alpha=255):
        scaled_x, scaled_y = self.scale_position(x, y)
        radius = 25 * self.scale_x  
        circle_color = (255, 192, 0, alpha)
        border_color = (255, 255, 255, alpha)

        circle_surf = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(circle_surf, circle_color, (int(radius), int(radius)), int(radius))
        pygame.draw.circle(circle_surf, border_color, (int(radius), int(radius)), int(radius), 2)
        screen.blit(circle_surf, (int(scaled_x - radius), int(scaled_y - radius)))

        approach_radius = radius * (1 + approach_rate)
        approach_surf = pygame.Surface((int(approach_radius * 2), int(approach_radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(approach_surf, border_color, (int(approach_radius), int(approach_radius)), int(approach_radius), 2)
        screen.blit(approach_surf, (int(scaled_x - approach_radius), int(scaled_y - approach_radius)))

    def draw_slider(self, screen, slider, approach_rate=1, alpha=255):
        start_x, start_y = self.scale_position(slider['x'], slider['y'])
        slider_color = (255, 192, 0, alpha)
        border_color = (255, 255, 255, alpha)

        for i in range(len(slider['curve_points']) - 1):
            start = self.scale_position(slider['curve_points'][i][0], slider['curve_points'][i][1])
            end = self.scale_position(slider['curve_points'][i+1][0], slider['curve_points'][i+1][1])
            pygame.draw.line(screen, slider_color, start, end, int(25 * self.scale_x))

        circle_surf = pygame.Surface((int(50 * self.scale_x), int(50 * self.scale_x)), pygame.SRCALPHA)
        pygame.draw.circle(circle_surf, slider_color, (int(25 * self.scale_x), int(25 * self.scale_x)), int(25 * self.scale_x))
        screen.blit(circle_surf, (int(start_x - 25 * self.scale_x), int(start_y - 25 * self.scale_x)))

        approach_radius = 25 * self.scale_x * (1 + approach_rate)
        approach_surf = pygame.Surface((int(approach_radius * 2), int(approach_radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(approach_surf, border_color, (int(approach_radius), int(approach_radius)), int(approach_radius), 2)
        screen.blit(approach_surf, (int(start_x - approach_radius), int(start_y - approach_radius)))

    def draw_spinner(self, screen, spinner, current_time):
        center_x, center_y = self.scale_position(256, 192)  
        radius = min(self.display_width, self.display_height) * 0.3
        progress = min(1, (current_time - spinner['time']) / (spinner['end_time'] - spinner['time']))

        pygame.draw.circle(screen, (255, 192, 0), (int(center_x), int(center_y)), int(radius), 2)
        pygame.draw.arc(screen, (255, 255, 255), (center_x - radius, center_y - radius, radius * 2, radius * 2),
                        0, progress * 2 * 3.14159, int(radius * 0.1))

    def draw_debug_info(self, screen, font, current_time, visible_objects):
        debug_color = (255, 255, 255)  
        debug_info = [
            f"Current Time: {current_time:.2f}ms",
            f"Visible Objects: {visible_objects}",
            f"Active Mods: {self.active_mods}",
        ]
        for i, info in enumerate(debug_info):
            text_surface = font.render(info, True, debug_color)
            screen.blit(text_surface, (10, 10 + i * 20))

    def apply_mods(self, x, y, time):
        if Mods.HardRock in self.active_mods:
            y = 384 - y  
        if Mods.Mirror in self.active_mods:
            x = 512 - x  
        if Mods.DoubleTime in self.active_mods:
            time *= 2/3  
        elif Mods.HalfTime in self.active_mods:
            time *= 4/3  
        return x, y, time

    def create_mod_buttons(self):
        button_width = 100
        button_height = 30
        button_margin = 10
        start_x = 10
        start_y = self.display_height - button_height - 10

        self.mod_buttons = []
        for i, mod in enumerate([Mods.HardRock, Mods.Hidden, Mods.DoubleTime, Mods.Mirror, Mods.HalfTime]):
            x = start_x + (button_width + button_margin) * (i % 4)
            y = start_y - (button_height + button_margin) * (i 
            button = Button(x, y, button_width, button_height, mod.name, (100, 100, 100), (255, 255, 255), self.font)
            self.mod_buttons.append((mod, button))

    def toggle_mod(self, mod):
        if mod in self.active_mods:
            self.active_mods &= ~mod
        else:
            self.active_mods |= mod

    def handle_mod_button_click(self, pos):
        for mod, button in self.mod_buttons:
            if button.is_clicked(pos):
                self.toggle_mod(mod)
                return True
        return False

    def play_replay(self):
        if self.replay is None:
            print("No replay loaded.")
            return

        if self.replay.mode != GameMode.STD:
            print("This player currently only supports osu!standard mode replays.")
            return

        pygame.init()
        screen = pygame.display.set_mode((self.display_width, self.display_height))
        clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.create_mod_buttons()

        running = True
        playing = True
        frame_index = 0
        total_frames = len(self.replay.replay_data)
        current_time = 0

        print(f"Replay loaded with {total_frames} frames.")
        print("Controls: DELETE to pause/resume, ESC to stop")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE:
                        playing = not playing
                        print("Replay paused" if not playing else "Replay resumed")
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        print("Replay stopped")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.handle_mod_button_click(event.pos):
                        print(f"Active mods: {self.active_mods}")

            if playing and frame_index < total_frames:
                frame = self.replay.replay_data[frame_index]
                x, y, mod_time = self.apply_mods(frame.x, frame.y, current_time + frame.time_delta)
                x, y = self.scale_position(x, y)
                current_time = mod_time

                screen.fill((0, 0, 0))  

                visible_objects = 0

                if self.beatmap:
                    for hit_object in self.beatmap.hit_objects:
                        obj_x, obj_y, obj_time = self.apply_mods(hit_object['x'], hit_object['y'], hit_object['time'])
                        time_diff = obj_time - current_time
                        if -200 < time_diff < 1000:  
                            approach_rate = max(0, min(1, time_diff / 1000))
                            alpha = 255
                            if Mods.Hidden in self.active_mods:
                                if time_diff < 0:
                                    alpha = max(0, int(255 * (1 + time_diff / 200)))
                                else:
                                    alpha = min(255, int(255 * (1 - time_diff / 1000)))

                            if hit_object['type'] == 'circle':
                                self.draw_hit_circle(screen, obj_x, obj_y, approach_rate, alpha)
                            elif hit_object['type'] == 'slider':
                                self.draw_slider(screen, hit_object, approach_rate, alpha)
                            elif hit_object['type'] == 'spinner':
                                self.draw_spinner(screen, hit_object, current_time)
                            visible_objects += 1

                pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 5)

                self.draw_debug_info(screen, self.font, current_time, visible_objects)

                for mod, button in self.mod_buttons:
                    button.draw(screen)

                pygame.display.flip()

                if frame_index % 100 == 0:
                    print(f"Playing frame {frame_index}/{total_frames}, Time: {current_time:.2f}ms, Visible Objects: {visible_objects}")

                clock.tick(60)
                frame_index += 1
            elif frame_index >= total_frames:
                print("Replay finished")
                running = False
            else:
                clock.tick(30)

        pygame.quit()
        print("Playback window closed")

if __name__ == "__main__":
    player = OSRPlayer(display_width=1280, display_height=720)
    while True:
        selected_replay = player.select_replay()
        player.load_replay(selected_replay)
        player.play_replay()
        play_again = input("Do you want to play another replay? (y/n): ").strip().lower()
        if play_again != 'y':
            break
    print("Thank you for using the OSR Replay Player!")
