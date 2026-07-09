import time
import requests
import urllib.parse
import sys
import os
import re
import threading 
import winreg 
import ctypes 
import io 
import json
import random
import base64
import uuid
import tkinter as tk
from tkinter import ttk
from pyaimp import Client, PlayBackState
from pypresence import Presence, ActivityType, StatusDisplayType
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from mutagen import File

# --- MULTI-INSTANCE PREVENTION ---
mutex_name = "AIMP_Bridge_Discord_Mutex"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
if ctypes.windll.kernel32.GetLastError() == 183: 
    sys.exit(0) 

# --- SECURITY: TOKEN DEOBFUSCATION ---
def decode_token(token_str):
    if token_str.startswith("ENC_REV_"):
        return token_str[8:][::-1]
    return token_str

# --- PATHS AND CONSTANTS ---
RAW_CLIENT_ID = "ENC_REV_5479661860780909841"
CLIENT_ID_DEFAULT = decode_token(RAW_CLIENT_ID)
REG_PATH_STARTUP = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_PATH_CONFIG = r"Software\AIMP_Bridge_Discord"
APP_NAME = "AIMP_Bridge_Discord"

app_data_dir = os.path.join(os.getenv('APPDATA'), APP_NAME)
locales_dir = os.path.join(app_data_dir, "locales")
path_local_covers_json = os.path.join(app_data_dir, "local_covers_db.json")
os.makedirs(app_data_dir, exist_ok=True)
os.makedirs(locales_dir, exist_ok=True)

sys.stderr = open(os.path.join(app_data_dir, "error_log.txt"), "a", encoding="utf-8")
sys.stdout = open(os.path.join(app_data_dir, "bridge_log.txt"), "a", encoding="utf-8")

def logger(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

# --- ANONYMOUS UUID INITIALIZATION ---
def get_or_create_user_uuid():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG, 0, winreg.KEY_READ)
        user_uuid, _ = winreg.QueryValueEx(key, "user_uuid")
        winreg.CloseKey(key)
        return user_uuid
    except WindowsError:
        new_uuid = str(uuid.uuid4())
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG)
            winreg.SetValueEx(key, "user_uuid", 0, winreg.REG_SZ, new_uuid)
            winreg.CloseKey(key)
        except: pass
        return new_uuid

USER_UUID = get_or_create_user_uuid()

# --- GITHUB DATABASE CONFIGURATION ---
RAW_GITHUB_TOKEN = "ENC_REV_WVOlPKMFBAUDHOS4EsdiWK0VZuy2qy0y6fVONDXqjmzs0KEfhXMr5mnKvxN_naHvHuW3OzPD0YR2A3JB11_tap_buhtig"
GITHUB_TOKEN = decode_token(RAW_GITHUB_TOKEN)
GITHUB_REPO = "Dryonefx01/Discord-Presence-Script-AIMP-"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/users_db/covers_{USER_UUID}.json"
GITHUB_KEYS_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/keys/imgbb.json"

global_covers_cache = {}
global_covers_sha = None

# Lista de reserva inicial (se sobreescribirá con lo que descargue de GitHub)
imgbb_api_keys = [decode_token('ENC_REV_50b7617d2ef33cd4f6e37ddd4d03e31e')]

if os.path.exists(path_local_covers_json):
    try:
        with open(path_local_covers_json, "r", encoding="utf-8") as f:
            global_covers_cache = json.load(f)
    except: pass

# --- IMGBB LOAD BALANCER (ANTI-BAN SYSTEM) ---
def fetch_imgbb_keys():
    global imgbb_api_keys
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(GITHUB_KEYS_API_URL, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            keys_data = json.loads(content)
            if "keys" in keys_data and isinstance(keys_data["keys"], list) and len(keys_data["keys"]) > 0:
                imgbb_api_keys = keys_data["keys"]
                logger(f"Loaded {len(imgbb_api_keys)} ImgBB API keys from GitHub pool.")
        elif r.status_code == 404:
            # Si el archivo no existe, crea una plantilla en GitHub para que el usuario la llene manualmente
            initial_data = {
                "_instructions": "Agrega tus API keys de ImgBB dentro de la lista 'keys' separadas por comas.",
                "keys": [imgbb_api_keys[0], "AGREGA_TU_SEGUNDA_API_KEY_AQUI", "AGREGA_TU_TERCERA_API_KEY_AQUI"]
            }
            content_str = json.dumps(initial_data, indent=4)
            b64_content = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
            payload = {"message": "Create ImgBB keys pool", "content": b64_content}
            requests.put(GITHUB_KEYS_API_URL, headers=headers, json=payload, timeout=10)
            logger("Created keys/imgbb.json pool in GitHub.")
    except Exception as e:
        logger(f"Failed to fetch ImgBB keys: {e}")

# --- GITHUB DATABASE SYNC ---
def sync_covers_db():
    global global_covers_cache, global_covers_sha
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            global_covers_sha = data['sha']
            content = base64.b64decode(data['content']).decode('utf-8')
            remote_cache = json.loads(content)
            global_covers_cache.update(remote_cache)
            with open(path_local_covers_json, "w", encoding="utf-8") as f:
                json.dump(global_covers_cache, f, indent=4, ensure_ascii=False)
            logger(f"Isolated Covers DB Synced for User {USER_UUID[:8]}... Items: {len(global_covers_cache)}")
        elif r.status_code == 404:
            push_covers_db()
        elif r.status_code == 401:
            logger("GitHub API: 401 Unauthorized. The token is invalid or expired.")
    except Exception as e:
        logger(f"Failed to sync isolated Covers DB: {e}")

def push_covers_db(retry=True):
    global global_covers_cache, global_covers_sha
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        with open(path_local_covers_json, "w", encoding="utf-8") as f:
            json.dump(global_covers_cache, f, indent=4, ensure_ascii=False)

        content_str = json.dumps(global_covers_cache, indent=4)
        b64_content = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
        payload = {"message": f"Auto-update isolated covers DB for {USER_UUID[:8]}", "content": b64_content}
        
        if global_covers_sha: 
            payload["sha"] = global_covers_sha
        
        r = requests.put(GITHUB_API_URL, headers=headers, json=payload, timeout=10)
        
        if r.status_code in [200, 201]:
            global_covers_sha = r.json()['content']['sha']
        elif r.status_code == 409 and retry:
            logger("SHA Conflict (409) detected. Resyncing and retrying push...")
            sync_covers_db() 
            push_covers_db(retry=False) 
        elif r.status_code == 401:
            logger("GitHub API: 401 Unauthorized. The token is invalid or expired.")
        else:
            logger(f"Failed to push with status code: {r.status_code}")
            
    except Exception as e:
        logger(f"Failed to push isolated Covers DB: {e}")

# Iniciar ambos hilos al arrancar
threading.Thread(target=sync_covers_db, daemon=True).start()
threading.Thread(target=fetch_imgbb_keys, daemon=True).start()

# --- DYNAMIC LOCALES SYSTEM (i18n) ---
GITHUB_LOCALES_BASE = "https://raw.githubusercontent.com/Dryonefx01/AIMP-Discord-Rich-Presence/refs/heads/main/locales/"
GITHUB_LOCALES_INDEX = f"{GITHUB_LOCALES_BASE}index.json"

cached_locales = {"en": "English", "es": "Español"}

def fetch_locales_index():
    global cached_locales
    try:
        response = requests.get(GITHUB_LOCALES_INDEX, timeout=5)
        if response.status_code == 200: cached_locales = response.json()
    except Exception as e: logger(f"Could not fetch locales index. {e}")

fetch_locales_index()

DEFAULT_EN_JSON = {
    "menu_startup": "Start with Windows",
    "menu_displayed_texts": "Displayed Texts",
    "menu_main_text": "Main Text (Listening to...)",
    "menu_top_line": "Top Line (Details)",
    "menu_bottom_line": "Bottom Line (State)",
    "menu_cover_tooltip": "Cover Tooltip",
    "menu_friend_list": "Friend List Text",
    "menu_playback_state": "Playback State",
    "menu_show_paused": "Show Paused State",
    "menu_show_timeline": "Show Timeline",
    "menu_album_cover": "Album Cover",
    "menu_status_icon": "Status Icon",
    "menu_theme": "Theme",
    "theme_auto_random": "Automatic (Random Theme)",
    "menu_language": "Language",
    "menu_filters": "Smart Filters / Auto-Disable",
    "opt_open_filters": "Open filters.json",
    "menu_auto_themes": "Custom Theme Rules",
    "opt_open_auto_themes": "Edit auto_themes.json",
    "menu_exit": "Exit",
    "opt_show": "Show...",
    "opt_always": "Always",
    "opt_auto": "Automatic",
    "opt_never": "Never",
    "opt_title": "Title",
    "opt_artist": "Artist",
    "opt_album": "Album",
    "opt_aimp": "AIMP",
    "opt_custom": "Custom (JSON)",
    "opt_custom_auto": "Custom (Auto-Switch)",
    "opt_file": "From File",
    "opt_file_lastfm": "File then Last.fm",
    "opt_lastfm_file": "Last.fm then File",
    "opt_none": "Do not show",
    "opt_dynamic": "Dynamic (Play/Pause)",
    "opt_logo_only": "Logo Only",
    "opt_name": "App Name (NAME)",
    "opt_details": "Details (DETAILS)",
    "opt_state": "State (STATE)",
    "status_playing": "Playing",
    "status_paused": "Paused",
    "unknown_track": "Unknown Track",
    "unknown_artist": "Unknown Artist",
    "unknown_album": "Unknown Single/Album",
    "by_artist": "by {artist}"
}

current_locale_data = DEFAULT_EN_JSON.copy()

def download_language(lang_code):
    url = f"{GITHUB_LOCALES_BASE}{lang_code}.json"
    local_path = os.path.join(locales_dir, f"{lang_code}.json")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f: f.write(response.text)
            return True
    except: pass
    return False

def load_language(lang_code):
    global current_locale_data
    local_path = os.path.join(locales_dir, f"{lang_code}.json")
    if not os.path.exists(local_path): download_language(lang_code)
    current_locale_data = DEFAULT_EN_JSON.copy()
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                current_locale_data.update(loaded_data)
        except: pass

def _(key): return current_locale_data.get(key, key)

# --- SYSTEM TRAY UI ---
def build_icon_image():
    img = Image.new('RGB', (64, 64), color=(255, 128, 0)) 
    draw = ImageDraw.Draw(img)
    draw.polygon([(32, 12), (52, 48), (12, 48)], fill=(255, 255, 255)) 
    return img

# --- FIRST RUN UI ---
def is_first_run():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "language")
        winreg.CloseKey(key)
        return False
    except WindowsError: return True

def run_first_setup_ui():
    root = tk.Tk()
    root.title("AIMP Bridge - Setup")
    root.geometry("300x120")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    try:
        icon_path = os.path.join(app_data_dir, "temp_icon.ico")
        build_icon_image().save(icon_path, format="ICO")
        root.iconbitmap(icon_path)
    except: pass

    selected_lang = tk.StringVar()
    
    def on_close(): sys.exit(0)
    root.protocol("WM_DELETE_WINDOW", on_close)

    ttk.Label(root, text="Select your language:", justify="center", font=("Arial", 10)).pack(pady=10)

    cb = ttk.Combobox(root, values=list(cached_locales.values()), state="readonly", font=("Arial", 10))
    if "English" in cached_locales.values(): cb.current(list(cached_locales.values()).index("English"))
    elif len(cached_locales) > 0: cb.current(0)
    cb.pack(pady=5)

    def on_confirm():
        val_to_key = {v: k for k, v in cached_locales.items()}
        selected_lang.set(val_to_key.get(cb.get(), "en"))
        root.destroy()

    ttk.Button(root, text="Continue", command=on_confirm).pack(pady=10)
    root.mainloop()
    return selected_lang.get()

if is_first_run():
    initial_lang = run_first_setup_ui()
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG)
        winreg.SetValueEx(key, "language", 0, winreg.REG_SZ, initial_lang)
        winreg.CloseKey(key)
    except: pass

# --- JSON SYSTEMS & DEFAULT DATA ---
DEFAULT_FILTERS = {
    "_instructions": "timeout_minutes: 0 to disable. time_range: HH:MM-HH:MM (24h format). blacklist: list of song titles or file paths.",
    "timeout_minutes": 0, "time_range": "", "blacklist": []
}

DEFAULT_AUTO_THEMES = {
    "_instructions": "fallback_theme is used when filters are inactive. Set timer_rotation_enabled to false to disable timer rotation.",
    "fallback_theme": "Default (AIMP)",
    "timer_rotation_enabled": True,
    "file_rules": [
        {"match": "C:\\Secret_Folder", "theme": "__AUTOMATIC__"}
    ],
    "timer_rotation": [
        {"theme": "Default (AIMP)", "time": 3600}
    ]
}

def load_json_file_safe(path, default_data):
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
            return default_data
        except: return default_data
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            raw_text = raw_text.replace('\\\\', '\\').replace('\\', '\\\\')
            return json.loads(raw_text)
    except Exception as e:
        logger(f"Error parsing JSON {path}: {e}")
        return default_data

path_themes_json = os.path.join(app_data_dir, "themes.json")
path_custom_json = os.path.join(app_data_dir, "custom_texts.json")
path_filters_json = os.path.join(app_data_dir, "filters.json")
path_auto_themes_json = os.path.join(app_data_dir, "auto_themes.json")

def load_themes_list():
    return load_json_file_safe(path_themes_json, [{
        "name": "Default (AIMP)", "client_id": "default", "large_image": "logo", "small_play": "play", "small_pause": "pause"
    }])

def load_custom_texts():
    default_data = {
        "_instructions": "Format: [{'text': '{title}', 'time': 5}, ...]. 'time' is in seconds.",
        "name": [{"text": "AIMP", "time": 10}],
        "details": [{"text": "{title}", "time": 5}, {"text": "{artist} - {album}", "time": 8}],
        "state": [{"text": "by {artist}", "time": 10}],
        "large_text": [{"text": "{album}", "time": 10}],
        "friend_list": [{"text": "details", "time": 10}, {"text": "state", "time": 10}]
    }
    return load_json_file_safe(path_custom_json, default_data)

def load_filters():
    return load_json_file_safe(path_filters_json, DEFAULT_FILTERS)

def load_auto_themes():
    return load_json_file_safe(path_auto_themes_json, DEFAULT_AUTO_THEMES)

themes_list = load_themes_list()

def get_theme_data(theme_name):
    for t in themes_list:
        if t.get("name") == theme_name: return t
    return themes_list[0] if themes_list else {"name": "Fallback", "client_id": "default"}

# --- AUTO THEME ENGINE ---
current_random_theme = None
random_theme_song = ""

def determine_active_theme(cfg_theme, track_name, file_path):
    global current_random_theme, random_theme_song
    
    def process_assignment(assigned_theme):
        global current_random_theme, random_theme_song
        if assigned_theme == '__AUTOMATIC__':
            if random_theme_song != track_name or not current_random_theme:
                valid_themes = [t.get("name") for t in themes_list]
                current_random_theme = random.choice(valid_themes) if valid_themes else "Default (AIMP)"
                random_theme_song = track_name
            return current_random_theme
        return assigned_theme

    if cfg_theme == '__AUTOMATIC__': return process_assignment('__AUTOMATIC__')
    if cfg_theme != '__CUSTOM_AUTO__': return cfg_theme
    
    auto_data = load_auto_themes()
    fallback = auto_data.get("fallback_theme", themes_list[0].get("name", "Default"))
    track_lower = track_name.lower()
    path_lower = str(file_path).lower() if file_path else ""
    
    for rule in auto_data.get("file_rules", []):
        m_val = str(rule.get("match", "")).lower()
        if m_val and (m_val in track_lower or m_val in path_lower):
            return process_assignment(rule.get("theme", fallback))
            
    if auto_data.get("timer_rotation_enabled", True):
        rotation = auto_data.get("timer_rotation", [])
        if rotation:
            total_time = sum(max(1, item.get("time", 60)) for item in rotation)
            if total_time > 0:
                c_mod = time.time() % total_time
                acc = 0
                for item in rotation:
                    acc += max(1, item.get("time", 60))
                    if c_mod < acc: return process_assignment(item.get("theme", fallback))
            
    return process_assignment(fallback)

# --- SMART FILTERS ENGINE ---
playing_start_time = None
def is_filtered(track_name, file_path, is_playing):
    global playing_start_time
    f_data = load_filters()
    
    track_lower = track_name.lower()
    path_lower = str(file_path).lower() if file_path else ""
    for b_item in f_data.get("blacklist", []):
        b_lower = str(b_item).lower()
        if b_lower and (b_lower in track_lower or b_lower in path_lower): return True

    tr = f_data.get("time_range", "").strip()
    if "-" in tr:
        try:
            start_s, end_s = tr.split("-")
            sh, sm = map(int, start_s.split(":"))
            eh, em = map(int, end_s.split(":"))
            now = time.localtime()
            now_mins = now.tm_hour * 60 + now.tm_min
            start_mins = sh * 60 + sm
            end_mins = eh * 60 + em
            if start_mins < end_mins:
                if start_mins <= now_mins <= end_mins: return True
            else:
                if now_mins >= start_mins or now_mins <= end_mins: return True
        except: pass

    timeout = f_data.get("timeout_minutes", 0)
    if timeout > 0:
        if is_playing:
            if playing_start_time is None: playing_start_time = time.time()
            elif (time.time() - playing_start_time) / 60 >= timeout: return True
        else: playing_start_time = None
    else: playing_start_time = None

    return False

# --- CONFIG & REGISTRY ---
api_key_lastfm = decode_token('ENC_REV_27085995c4608f95d9b4270b0f1e6a3c')

http_session = requests.Session()
http_session.headers.update({'user-agent': 'AimpDiscordBridge/6.1'})

def is_startup_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_STARTUP, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except: return False

def load_config():
    config = {
        'show_pause': True, 'cover_source': "file_lastfm", 'show_timeline': True,
        'icon_state': "dynamic", 'theme_current': themes_list[0].get("name", "Default"),
        'text_name': "aimp", 'text_details': "title", 'text_state': "artist",
        'text_large': "album", 'show_name': "auto", 'show_details': "auto",
        'show_state': "auto", 'show_large': "auto", 'status_display': "details", 'language': "en"
    }
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG, 0, winreg.KEY_READ)
        for param in config.keys():
            try:
                val = winreg.QueryValueEx(key, param)[0]
                if param in ['show_pause', 'show_timeline']: config[param] = bool(val)
                else: config[param] = str(val)
            except: pass
        winreg.CloseKey(key)
    except: pass
    return config

def save_config():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG)
        winreg.SetValueEx(key, "show_pause", 0, winreg.REG_DWORD, int(cfg_show_pause))
        winreg.SetValueEx(key, "show_timeline", 0, winreg.REG_DWORD, int(cfg_show_timeline))
        params = [
            ("cover_source", cfg_cover_source), ("icon_state", cfg_icon_state), 
            ("theme_current", cfg_theme_current), ("text_name", cfg_text_name),
            ("text_details", cfg_text_details), ("text_state", cfg_text_state), 
            ("text_large", cfg_text_large), ("show_name", cfg_show_name), 
            ("show_details", cfg_show_details), ("show_state", cfg_show_state), 
            ("show_large", cfg_show_large), ("status_display", cfg_status_display),
            ("language", cfg_language)
        ]
        for name, val in params: winreg.SetValueEx(key, name, 0, winreg.REG_SZ, val)
        winreg.CloseKey(key)
    except: pass

cfg = load_config()
cfg_startup = is_startup_enabled()
cfg_show_pause = cfg['show_pause']
cfg_show_timeline = cfg['show_timeline']
cfg_cover_source = cfg['cover_source']
cfg_icon_state = cfg['icon_state']
cfg_theme_current = cfg['theme_current']
cfg_text_name = cfg['text_name']
cfg_text_details = cfg['text_details']
cfg_text_state = cfg['text_state']
cfg_text_large = cfg['text_large']
cfg_show_name = cfg['show_name']
cfg_show_details = cfg['show_details']
cfg_show_state = cfg['show_state']
cfg_show_large = cfg['show_large']
cfg_status_display = cfg['status_display']
cfg_language = cfg['language']

is_running = True 
load_language(cfg_language)

def get_config_state_tuple():
    return (cfg_show_pause, cfg_cover_source, cfg_show_timeline, cfg_icon_state, cfg_theme_current, 
            cfg_text_name, cfg_text_details, cfg_text_state, cfg_text_large, cfg_show_name, 
            cfg_show_details, cfg_show_state, cfg_show_large, cfg_status_display, cfg_language)

# --- MENUS ---
def toggle_startup(icon, item):
    global cfg_startup
    enabled = is_startup_enabled()
    cfg_startup = not enabled
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_STARTUP, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            winreg.DeleteValue(key, APP_NAME)
        else:
            exe_path = sys.argv[0]
            if not exe_path.endswith('.exe'):
                exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        logger(f"Startup toggle error: {e}")

def set_radio(var_name, value):
    def setter(icon, item): 
        globals()[var_name] = value
        guardar_config_y_actualizar()
    return setter

def check_radio(var_name, value): return lambda item: globals()[var_name] == value

def set_toggle(var_name):
    def toggler(icon, item): 
        globals()[var_name] = not globals()[var_name]
        guardar_config_y_actualizar()
    return toggler

def guardar_config_y_actualizar():
    save_config()
    if sys._getframe(1).f_code.co_name == 'setter' and 'cfg_language' in globals():
        load_language(cfg_language)
        icon.menu = build_dynamic_menu()

def exit_app(icon, item):
    global is_running
    is_running = False
    icon.stop()

def build_text_menu(var_text, var_show):
    return pystray.Menu(
        item(lambda t: _('opt_show'), pystray.Menu(
            item(lambda t: _('opt_always'), set_radio(var_show, 'always'), checked=check_radio(var_show, 'always'), radio=True),
            item(lambda t: _('opt_auto'), set_radio(var_show, 'auto'), checked=check_radio(var_show, 'auto'), radio=True),
            item(lambda t: _('opt_never'), set_radio(var_show, 'never'), checked=check_radio(var_show, 'never'), radio=True)
        )),
        item(lambda t: _('opt_title'), set_radio(var_text, 'title'), checked=check_radio(var_text, 'title'), radio=True),
        item(lambda t: _('opt_artist'), set_radio(var_text, 'artist'), checked=check_radio(var_text, 'artist'), radio=True),
        item(lambda t: _('opt_album'), set_radio(var_text, 'album'), checked=check_radio(var_text, 'album'), radio=True),
        item(lambda t: _('opt_aimp'), set_radio(var_text, 'aimp'), checked=check_radio(var_text, 'aimp'), radio=True),
        item(lambda t: _('opt_custom'), set_radio(var_text, 'custom'), checked=check_radio(var_text, 'custom'), radio=True)
    )

def set_theme_ui(theme_name):
    def setter(icon, item):
        global cfg_theme_current, discord_connected, last_rpc_song, last_playback_state, last_resolved_theme
        if cfg_theme_current != theme_name:
            cfg_theme_current = theme_name
            save_config()
            last_rpc_song = "" 
            last_resolved_theme = "" 
    return setter

def check_theme_ui(theme_name): return lambda item: cfg_theme_current == theme_name

def toggle_special_theme(theme_name):
    def toggler(icon, item):
        global cfg_theme_current, discord_connected, last_rpc_song, last_playback_state, last_resolved_theme
        if cfg_theme_current == theme_name:
            cfg_theme_current = themes_list[0].get("name", "Default")
        else:
            cfg_theme_current = theme_name
        save_config()
        last_rpc_song = ""
        last_resolved_theme = ""
        icon.menu = build_dynamic_menu()
    return toggler

def open_file(path, default_data_dict):
    def opener(icon, item):
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default_data_dict, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger(f"Error creating file {path}: {e}")
                return
        try: os.startfile(path)
        except: pass
    return opener

def build_dynamic_menu():
    def is_theme_enabled(item_instance):
        return cfg_theme_current not in ['__CUSTOM_AUTO__', '__AUTOMATIC__']

    themes_menu_items = [
        item(t.get("name", "Unknown"), 
             set_theme_ui(t.get("name")), 
             checked=check_theme_ui(t.get("name")), 
             radio=True, 
             enabled=is_theme_enabled) 
        for t in themes_list
    ]
    
    themes_menu_items.append(pystray.Menu.SEPARATOR)
    themes_menu_items.append(item(lambda t: _('opt_custom_auto'), toggle_special_theme('__CUSTOM_AUTO__'), checked=check_theme_ui('__CUSTOM_AUTO__')))
    themes_menu_items.append(item(lambda t: _('theme_auto_random'), toggle_special_theme('__AUTOMATIC__'), checked=check_theme_ui('__AUTOMATIC__')))
    themes_menu_items.append(pystray.Menu.SEPARATOR)
    themes_menu_items.append(item(lambda t: _('menu_auto_themes'), pystray.Menu(
        item(lambda t: _('opt_open_auto_themes'), open_file(path_auto_themes_json, DEFAULT_AUTO_THEMES))
    )))
    
    lang_menu_items = [item(name, set_radio('cfg_language', code), checked=check_radio('cfg_language', code), radio=True) for code, name in cached_locales.items()]

    return pystray.Menu(
        item(lambda t: _('menu_startup'), toggle_startup, checked=lambda item: is_startup_enabled()),
        item(lambda t: _('menu_displayed_texts'), pystray.Menu(
            item(lambda t: _('menu_main_text'), build_text_menu('cfg_text_name', 'cfg_show_name')),
            item(lambda t: _('menu_top_line'), build_text_menu('cfg_text_details', 'cfg_show_details')),
            item(lambda t: _('menu_bottom_line'), build_text_menu('cfg_text_state', 'cfg_show_state')),
            item(lambda t: _('menu_cover_tooltip'), build_text_menu('cfg_text_large', 'cfg_show_large')),
            item(lambda t: _('menu_friend_list'), pystray.Menu(
                item(lambda t: _('opt_name'), set_radio('cfg_status_display', 'name'), checked=check_radio('cfg_status_display', 'name'), radio=True),
                item(lambda t: _('opt_details'), set_radio('cfg_status_display', 'details'), checked=check_radio('cfg_status_display', 'details'), radio=True),
                item(lambda t: _('opt_state'), set_radio('cfg_status_display', 'state'), checked=check_radio('cfg_status_display', 'state'), radio=True),
                item(lambda t: _('opt_custom'), set_radio('cfg_status_display', 'custom'), checked=check_radio('cfg_status_display', 'custom'), radio=True)
            ))
        )),
        item(lambda t: _('menu_playback_state'), pystray.Menu(
            item(lambda t: _('menu_show_paused'), set_toggle('cfg_show_pause'), checked=lambda i: cfg_show_pause),
            item(lambda t: _('menu_show_timeline'), set_toggle('cfg_show_timeline'), checked=lambda i: cfg_show_timeline),
            item(lambda t: _('menu_album_cover'), pystray.Menu(
                item(lambda t: _('opt_file'), set_radio('cfg_cover_source', 'file'), checked=check_radio('cfg_cover_source', 'file'), radio=True),
                item(lambda t: _('opt_file_lastfm'), set_radio('cfg_cover_source', 'file_lastfm'), checked=check_radio('cfg_cover_source', 'file_lastfm'), radio=True),
                item(lambda t: _('opt_lastfm_file'), set_radio('cfg_cover_source', 'lastfm_file'), checked=check_radio('cfg_cover_source', 'lastfm_file'), radio=True),
                item(lambda t: _('opt_none'), set_radio('cfg_cover_source', 'none'), checked=check_radio('cfg_cover_source', 'none'), radio=True)
            )),
            item(lambda t: _('menu_status_icon'), pystray.Menu(
                item(lambda t: _('opt_dynamic'), set_radio('cfg_icon_state', 'dynamic'), checked=check_radio('cfg_icon_state', 'dynamic'), radio=True),
                item(lambda t: _('opt_logo_only'), set_radio('cfg_icon_state', 'logo'), checked=check_radio('cfg_icon_state', 'logo'), radio=True),
                item(lambda t: _('opt_none'), set_radio('cfg_icon_state', 'none'), checked=check_radio('cfg_icon_state', 'none'), radio=True)
            ))
        )),
        item(lambda t: _('menu_filters'), pystray.Menu(
            item(lambda t: _('opt_open_filters'), open_file(path_filters_json, DEFAULT_FILTERS))
        )),
        item(lambda t: _('menu_theme'), pystray.Menu(*themes_menu_items)),
        item(lambda t: _('menu_language'), pystray.Menu(*lang_menu_items)),
        item(lambda t: _('menu_exit'), exit_app)
    )

icon = pystray.Icon("AIMP Bridge", build_icon_image(), "AIMP Discord Bridge", build_dynamic_menu())

# --- CORE FUNCTIONS ---
def connect_aimp():
    while is_running:
        try: return Client()
        except: time.sleep(3)

def is_valid_client_id(cid): return bool(cid and str(cid).isdigit() and len(str(cid)) >= 15)

def connect_discord_core(cid, max_retries=3):
    rpc = Presence(cid)
    for _ in range(max_retries):
        if not is_running: return None
        try:
            rpc.connect()
            return rpc
        except: time.sleep(0.5)
    return None

def connect_discord_safe(requested_cid):
    id_str = str(requested_cid).strip().lower()
    if not id_str or id_str == "default" or id_str == "none":
        return connect_discord_core(CLIENT_ID_DEFAULT), CLIENT_ID_DEFAULT
    if not is_valid_client_id(requested_cid):
        return connect_discord_core(CLIENT_ID_DEFAULT), CLIENT_ID_DEFAULT
    rpc = connect_discord_core(requested_cid)
    if rpc: return rpc, requested_cid
    return connect_discord_core(CLIENT_ID_DEFAULT), CLIENT_ID_DEFAULT

def extract_main_artist(raw_artist):
    parts = re.split(r'[;/,]| & | feat\. | ft\. | vs\. ', raw_artist, flags=re.IGNORECASE)
    return parts[0].strip()

# --- TEXT FORMATTING ---
def format_rpc_text(json_field, cfg_option, show_mode, info_dict, custom_data):
    if show_mode == "never": return None

    if cfg_option != "custom":
        mapped_artist = _('by_artist').replace("{artist}", info_dict['artist'])
        map_dict = {
            "title": info_dict['title'], 
            "artist": mapped_artist, 
            "album": info_dict['album'], 
            "aimp": "AIMP"
        }
        final_text = map_dict.get(cfg_option, "AIMP")
    else:
        items = custom_data.get(json_field, [])
        if not items: return None
        
        if isinstance(items[0], str):
            idx = int(time.time() / 15) % len(items)
            chosen_text = str(items[idx])
        else:
            total_time = sum(max(1, i.get("time", 5)) for i in items)
            c_mod = time.time() % total_time
            acc = 0
            chosen_text = items[-1].get("text", "")
            for i in items:
                acc += max(1, i.get("time", 5))
                if c_mod < acc:
                    chosen_text = i.get("text", "")
                    break
        
        chosen_text = chosen_text.replace("{title}", info_dict['title'])
        chosen_text = chosen_text.replace("{artist}", info_dict['artist'])
        chosen_text = chosen_text.replace("{album}", info_dict['album'])
        final_text = chosen_text

    if not final_text or not str(final_text).strip(): return None

    if show_mode == "auto":
        empty_filters = [_("unknown_track"), _("unknown_artist"), _("unknown_album"), "Sencillo/Desconocido", "Artista Desconocido", "Pista Desconocida"]
        for f in empty_filters:
            if f in final_text: return None

    return final_text

# --- IMAGE FETCHING (MUTAGEN & LAST.FM & CACHE) ---
def fetch_lastfm_cover(artist, track, album_name):
    track_clean = track.replace(".flac", "").replace(".mp3", "").strip()
    album_target = album_name.lower().strip() if album_name else ""
    try:
        url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key_lastfm}&artist={urllib.parse.quote(artist)}&track={urllib.parse.quote(track_clean)}&format=json"
        data = http_session.get(url, timeout=5).json()
        if 'track' in data and 'album' in data['track']:
            img = data['track']['album']['image'][-1]['#text']
            if img and (data['track']['album'].get('title', "").lower().strip() == album_target or album_target in ["", "album", _("unknown_album").lower()]): return img
    except: pass
    try:
        if album_target and album_target not in ["", "album", _("unknown_album").lower(), "sencillo/desconocido"]:
            url_album = f"http://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={api_key_lastfm}&artist={urllib.parse.quote(artist)}&album={urllib.parse.quote(album_name)}&format=json"
            data_album = http_session.get(url_album, timeout=5).json()
            if 'album' in data_album:
                img_album = data_album['album']['image'][-1]['#text']
                if img_album: return img_album
    except: pass
    return None

def extract_local_cover(file_path):
    try:
        if not os.path.exists(file_path): return None
        audio = File(file_path)
        if not audio: return None
        if hasattr(audio, 'pictures') and audio.pictures: return audio.pictures[0].data
        if "covr" in audio: 
            covr_data = audio["covr"][0]
            return covr_data if isinstance(covr_data, bytes) else bytes(covr_data)
        tags = getattr(audio, 'tags', audio)
        if tags is not None:
            if hasattr(tags, 'values'):
                for tag_obj in tags.values():
                    if hasattr(tag_obj, 'data'):
                        mime = getattr(tag_obj, 'mime', '').lower()
                        frame_id = getattr(tag_obj, 'FrameID', '')
                        if 'image' in mime or frame_id in ['APIC', 'PIC']: return tag_obj.data
            if hasattr(tags, 'keys'):
                for key in tags.keys():
                    if key.startswith("APIC") or key.startswith("PIC") or "cover" in key.lower() or key == "metadata_block_picture": return tags[key].data
    except: pass
    return None

def upload_to_imgbb(img_bytes):
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != 'RGB': img = img.convert('RGB')
        img.thumbnail((512, 512), Image.Resampling.LANCZOS) 
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        
        # Elegir una API key aleatoria del pool descargado de GitHub
        selected_key = random.choice(imgbb_api_keys)
        
        response = http_session.post("https://api.imgbb.com/1/upload", data={"key": selected_key, "expiration": 604800}, files={"image": ("cover.jpg", output.getvalue(), "image/jpeg")}, timeout=10)
        
        if response.status_code == 200 and response.json().get("success"): 
            return response.json()["data"]["url"]
        else:
            logger(f"ImgBB upload error with key {selected_key[:4]}... -> Code: {response.status_code}")
    except Exception as e: 
        logger(f"ImgBB exception: {e}")
    return None

force_cover_update = False
cover_thread_counter = 0

def async_cover_search(raw_artist, target_track, target_album, file_path, source_cfg, fallback_img, thread_id):
    global current_cover, force_cover_update, global_covers_cache, cover_thread_counter
    
    if thread_id != cover_thread_counter: return

    final_url = fallback_img
    main_artist = extract_main_artist(raw_artist)

    clean_album = target_album.lower().strip()
    is_unknown_album = clean_album in ["", "album", _("unknown_album").lower(), "sencillo/desconocido", "unknown single/album"]
    db_key = f"{main_artist} - {target_track}" if is_unknown_album else f"{main_artist} - {target_album}"

    if db_key in global_covers_cache:
        cached_url = global_covers_cache[db_key]
        
        if thread_id == cover_thread_counter:
            current_cover = cached_url
            force_cover_update = True
            
        link_dead = False
        try:
            test_resp = http_session.head(cached_url, timeout=2.5)
            if test_resp.status_code == 404:
                link_dead = True
        except:
            pass 
            
        if not link_dead:
            return
        else:
            logger(f"Expired link detected for '{db_key}'. Removing from DB to re-upload.")
            del global_covers_cache[db_key]

    def try_lastfm():
        url_lfm = fetch_lastfm_cover(raw_artist, target_track, target_album)
        if not url_lfm and main_artist != raw_artist: url_lfm = fetch_lastfm_cover(main_artist, target_track, target_album)
        if url_lfm:
            try:
                if http_session.head(url_lfm, timeout=3).status_code == 200: return url_lfm
            except: pass
        return None

    def try_file():
        if file_path and os.path.exists(file_path):
            img_bytes = extract_local_cover(file_path)
            if img_bytes:
                if thread_id != cover_thread_counter: return None 
                url_imgbb = upload_to_imgbb(img_bytes)
                if url_imgbb: return url_imgbb
        return None

    if source_cfg == "file": final_url = try_file() or fallback_img
    elif source_cfg == "file_lastfm": final_url = try_file() or try_lastfm() or fallback_img
    elif source_cfg == "lastfm_file": final_url = try_lastfm() or try_file() or fallback_img
    
    if thread_id != cover_thread_counter: return

    if final_url != fallback_img:
        global_covers_cache[db_key] = final_url
        threading.Thread(target=push_covers_db, daemon=True).start()

    if target_track == last_rpc_song:
        current_cover = final_url
        force_cover_update = True

# --- MAIN EXECUTION ---
icon.run_detached()

last_resolved_theme = ""
RPC = None
active_client_id = ""
discord_connected = False
aimp = connect_aimp()
aimp_connected = True

last_rpc_song = ""
last_discord_song = ""
last_playback_state = None
last_aimp_pos = 0
current_cover = "logo"
last_discord_update = time.time() 
last_evaluated_texts = ("", "", "", "")
last_config_state = get_config_state_tuple()

# VARIABLES PARA EL FIX DE LA LÍNEA DE TIEMPO
last_v_start = None
last_v_end = None

while is_running:
    current_config_state = get_config_state_tuple()
    config_changed = current_config_state != last_config_state
    
    if not aimp_connected:
        aimp = connect_aimp()
        aimp_connected = True

    try:
        aimp.detect_aimp() 
        p_state = aimp.get_playback_state()
        info = aimp.get_current_track_info()
        live_custom_data = load_custom_texts()

        if info and p_state != PlayBackState.Stopped:
            track_name = info.get('title', _('unknown_track')) or _('unknown_track')
            file_path = info.get('filename', '')
            
            resolved_theme_name = determine_active_theme(cfg_theme_current, track_name, file_path)
            current_theme_data = get_theme_data(resolved_theme_name)
            requested_cid = current_theme_data.get("client_id", "default")
            processed_req_id = CLIENT_ID_DEFAULT if (not requested_cid or str(requested_cid).lower() == "default") else requested_cid
            
            if resolved_theme_name != last_resolved_theme:
                last_resolved_theme = resolved_theme_name
                last_rpc_song = "" 
                if processed_req_id != active_client_id and discord_connected:
                    if RPC:
                        try: RPC.clear(); RPC.close() 
                        except: pass
                    discord_connected = False 

            if not discord_connected:
                new_rpc, connected_id = connect_discord_safe(requested_cid)
                if new_rpc:
                    RPC = new_rpc
                    active_client_id = connected_id
                    discord_connected = True
                    last_discord_update = time.time()
                    last_discord_song = ""
                    current_cover = current_theme_data.get("large_image", "logo")
                else:
                    time.sleep(0.5)
                    continue

            if is_filtered(track_name, file_path, p_state == PlayBackState.Playing):
                if last_playback_state != PlayBackState.Stopped:
                    try: RPC.clear()
                    except: pass
                    last_playback_state = PlayBackState.Stopped
                    last_discord_song = ""
                time.sleep(0.5)
                continue

            if p_state == PlayBackState.Paused and not cfg_show_pause:
                if last_playback_state != PlayBackState.Stopped or config_changed:
                    try: RPC.clear()
                    except: pass
                    last_playback_state = PlayBackState.Stopped
                    last_discord_song = "" 
                last_config_state = current_config_state
                time.sleep(0.5)
                continue

            album_name = info.get('album', _('unknown_album')) or _('unknown_album')
            artist_name = info.get('artist', _('unknown_artist')) or _('unknown_artist')
            pos_sec = int(aimp.get_player_position() / 1000)
            duration_sec = int(info['duration'] / 1000)

            theme_fallback_img = current_theme_data.get("large_image", "logo")

            if track_name != last_rpc_song:
                last_rpc_song = track_name
                current_cover = theme_fallback_img
                cover_thread_counter += 1
                if cfg_cover_source != "none":
                    threading.Thread(target=async_cover_search, args=(artist_name, track_name, album_name, file_path, cfg_cover_source, theme_fallback_img, cover_thread_counter), daemon=True).start()
                else: force_cover_update = True

            # --- FIX: CÁLCULO ESTABLE DE LÍNEA DE TIEMPO Y PREVENCIÓN DE CARRERAS ---
            if p_state == PlayBackState.Playing:
                # Si cambió la canción pero la posición reportada sigue siendo alta, es el residuo
                # de la canción anterior que AIMP no limpió a tiempo en su API. Lo forzamos a 0.
                if track_name != last_discord_song and last_discord_song != "" and pos_sec > 3:
                    pos_sec = 0

                # Doble seguridad para evitar que la posición supere la duración máxima
                if duration_sec > 0 and pos_sec > duration_sec:
                    pos_sec = duration_sec

                current_v_start = int(time.time()) - pos_sec
                current_v_end = current_v_start + duration_sec
                
                # Si es una nueva canción, reanuda, o detecta que adelantaste (diferencia mayor a 2s)
                if track_name != last_discord_song or p_state != last_playback_state or last_v_start is None or abs(current_v_start - last_v_start) > 2:
                    last_v_start = current_v_start
                    last_v_end = current_v_end
                    did_seek = True 
                else:
                    did_seek = False

                v_start = last_v_start
                v_end = last_v_end
                v_small_icon = current_theme_data.get("small_play", "play")
                v_txt_state = _('status_playing')
            else:
                v_start = None; v_end = None
                last_v_start = None; last_v_end = None # Reseteamos al pausar
                did_seek = False
                v_small_icon = current_theme_data.get("small_pause", "pause")
                v_txt_state = _('status_paused')

            dict_info = {"title": track_name, "artist": artist_name, "album": album_name}
            
            t_name = format_rpc_text("name", cfg_text_name, cfg_show_name, dict_info, live_custom_data)
            t_details = format_rpc_text("details", cfg_text_details, cfg_show_details, dict_info, live_custom_data)
            t_state = format_rpc_text("state", cfg_text_state, cfg_show_state, dict_info, live_custom_data)
            t_large = format_rpc_text("large_text", cfg_text_large, cfg_show_large, dict_info, live_custom_data)

            t_name = (t_name + " ") if (t_name is not None and len(t_name) < 2) else t_name
            t_details = (t_details + " ") if (t_details is not None and len(t_details) < 2) else t_details
            t_state = (t_state + " ") if (t_state is not None and len(t_state) < 2) else t_state
            t_large = (t_large + " ") if (t_large is not None and len(t_large) < 2) else t_large

            current_texts = (t_name, t_details, t_state, t_large)
            texts_rotated = current_texts != last_evaluated_texts
            force_timer = (time.time() - last_discord_update) > 5

            type_display = StatusDisplayType.DETAILS
            status_mode = cfg_status_display
            
            if status_mode == 'custom':
                fl_items = live_custom_data.get("friend_list", [])
                if fl_items:
                    if isinstance(fl_items[0], str): 
                        status_str = fl_items[int(time.time() / 15) % len(fl_items)]
                    else:
                        tot_t = sum(max(1, i.get("time", 10)) for i in fl_items)
                        c_mod = time.time() % tot_t
                        acc = 0
                        status_str = fl_items[-1].get("text", "details")
                        for i in fl_items:
                            acc += max(1, i.get("time", 10))
                            if c_mod < acc:
                                status_str = i.get("text", "details")
                                break
                    status_mode = status_str.lower()
                    
            if status_mode == 'name': type_display = StatusDisplayType.NAME
            elif status_mode == 'state': type_display = StatusDisplayType.STATE

            if (track_name != last_discord_song or p_state != last_playback_state or did_seek or force_timer or config_changed or force_cover_update or texts_rotated):
                
                img_send = theme_fallback_img if cfg_cover_source == "none" else current_cover
                time_start = v_start if (cfg_show_timeline and duration_sec > 0) else None
                time_end = v_end if (cfg_show_timeline and duration_sec > 0) else None
                
                if cfg_icon_state == "logo": s_img = theme_fallback_img; s_txt = "AIMP"
                elif cfg_icon_state == "none": s_img = None; s_txt = None
                else: s_img = v_small_icon; s_txt = v_txt_state

                search_artist = extract_main_artist(artist_name)
                q_str = urllib.parse.quote(f"{search_artist} {track_name}")
                
                try:
                    if track_name != last_discord_song:
                        logger(f"Activity Updated -> {track_name} by {artist_name} | Path: {file_path}")

                    RPC.update(
                        name=t_name[:128] if t_name else None, 
                        details=t_details[:128] if t_details else None, 
                        state=t_state[:128] if t_state else None, 
                        large_image=img_send, large_text=t_large[:128] if t_large else None, 
                        small_image=s_img, small_text=s_txt,
                        start=time_start, end=time_end,
                        buttons=[{"label": "Spotify", "url": f"https://open.spotify.com/search/{q_str}"}, {"label": "YouTube", "url": f"https://www.youtube.com/results?search_query={q_str}"}],
                        activity_type=ActivityType.LISTENING, status_display_type=type_display
                    )
                    last_discord_song = track_name
                    last_playback_state = p_state
                    last_discord_update = time.time()
                    last_config_state = current_config_state
                    last_evaluated_texts = current_texts
                    force_cover_update = False 
                    
                except Exception:
                    discord_connected = False
                    last_playback_state = None 
                
            last_aimp_pos = pos_sec
        else:
            if last_playback_state != PlayBackState.Stopped:
                aimp.detect_aimp() 
                try: RPC.clear()
                except: pass
                last_rpc_song = ""
                last_discord_song = ""
                last_playback_state = PlayBackState.Stopped

    except (RuntimeError, Exception):
        aimp_connected = False
        last_rpc_song = ""
        last_discord_song = ""
        last_playback_state = None
        try: RPC.clear()
        except: pass
    
    time.sleep(0.5)

if RPC:
    try: RPC.clear(); RPC.close()
    except: pass
sys.exit(0)
