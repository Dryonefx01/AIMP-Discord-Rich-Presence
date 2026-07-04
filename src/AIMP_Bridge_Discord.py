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

# --- PATHS AND CONSTANTS ---
CLIENT_ID_DEFAULT = '1489090870681669745'
REG_PATH_STARTUP = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_PATH_CONFIG = r"Software\AIMP_Bridge_Discord"
APP_NAME = "AIMP_Bridge_Discord"

app_data_dir = os.path.join(os.getenv('APPDATA'), APP_NAME)
locales_dir = os.path.join(app_data_dir, "locales")
os.makedirs(app_data_dir, exist_ok=True)
os.makedirs(locales_dir, exist_ok=True)

sys.stderr = open(os.path.join(app_data_dir, "error_log.txt"), "a", encoding="utf-8")
sys.stdout = open(os.path.join(app_data_dir, "bridge_log.txt"), "a", encoding="utf-8")

def logger(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

# --- i18n (LANGUAGE SYSTEM) ---
GITHUB_LOCALES_URL = "https://raw.githubusercontent.com/Dryonefx01/AIMP-Discord-Rich-Presence/refs/heads/main/locales/"

# Fallback in case GitHub is unreachable during first run
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
    "menu_language": "Language",
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

current_locale_data = DEFAULT_EN_JSON

def download_language(lang_code):
    url = f"{GITHUB_LOCALES_URL}{lang_code}.json"
    local_path = os.path.join(locales_dir, f"{lang_code}.json")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            return True
    except: pass
    return False

def load_language(lang_code):
    global current_locale_data
    local_path = os.path.join(locales_dir, f"{lang_code}.json")
    
    if not os.path.exists(local_path):
        download_language(lang_code)
        
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                current_locale_data = json.load(f)
            return
        except Exception as e:
            logger(f"Error loading {lang_code}.json: {e}")
            
    current_locale_data = DEFAULT_EN_JSON

def _(key):
    return current_locale_data.get(key, key)

# --- INITIAL SETUP (FIRST RUN UI) ---
def is_first_run():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return False
    except WindowsError:
        return True

def run_first_setup_ui():
    root = tk.Tk()
    root.title("AIMP Bridge - Setup")
    root.geometry("320x150")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    root.iconbitmap(default='') # Hide default tkinter feather icon

    selected_lang = tk.StringVar(value="en")

    ttk.Label(root, text="Select your language:\nSelecciona tu idioma:", justify="center", font=("Arial", 10)).pack(pady=10)

    # Popular languages dictionary (Name to Code)
    langs = {
        "English": "en",
        "Español": "es",
        "Português": "pt",
        "Русский (Russian)": "ru",
        "中文 (Chinese)": "zh"
    }

    cb = ttk.Combobox(root, values=list(langs.keys()), state="readonly", font=("Arial", 10))
    cb.current(1) # Select Español by default since you are the dev
    cb.pack(pady=5)

    def on_confirm():
        selected_lang.set(langs[cb.get()])
        root.destroy()

    ttk.Button(root, text="Continue / Continuar", command=on_confirm).pack(pady=10)

    root.mainloop()
    return selected_lang.get()

# Trigger First Run UI if needed
first_run = is_first_run()
if first_run:
    initial_lang = run_first_setup_ui()
    # Create the base registry key
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG)
        winreg.SetValueEx(key, "language", 0, winreg.REG_SZ, initial_lang)
        winreg.CloseKey(key)
    except: pass

# --- JSON SYSTEMS (THEMES & CUSTOM TEXTS) ---
THEMES_DEFAULT = [
    {
        "nombre": "Default (AIMP)",
        "client_id": "default",
        "large_image": "logo",
        "small_play": "play",
        "small_pause": "pause"
    }
]

path_themes_json = os.path.join(app_data_dir, "themes.json")
path_custom_json = os.path.join(app_data_dir, "custom_texts.json")

def load_themes_list():
    if not os.path.exists(path_themes_json):
        try:
            with open(path_themes_json, "w", encoding="utf-8") as f:
                json.dump(THEMES_DEFAULT, f, indent=4, ensure_ascii=False)
            return THEMES_DEFAULT
        except: return THEMES_DEFAULT
    try:
        with open(path_themes_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return THEMES_DEFAULT

def load_custom_texts():
    default_data = {
        "_instrucciones": "Use {titulo}, {artista} and {album}. For rotation, use brackets like [\"text1\", \"text2\"].",
        "rotacion_segundos": 15,
        "name": ["AIMP"],
        "details": ["{titulo}", "{artista} - {album}"],
        "state": ["by {artista}"],
        "large_text": ["{album}"]
    }
    if not os.path.exists(path_custom_json):
        try:
            with open(path_custom_json, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
        except: pass
        return default_data
    try:
        with open(path_custom_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return default_data

themes_list = load_themes_list()

def get_theme_data(theme_name):
    for t in themes_list:
        if t["nombre"] == theme_name: return t
    return themes_list[0]

# --- API KEYS & SESSIONS ---
api_key_lastfm = 'c3a6e1f0b0724b9d59f8064c59958072'
API_KEY_IMGBB = 'e13e30d4ddd73e6f4dc33fe2d7167b05' 

http_session = requests.Session()
http_session.headers.update({'user-agent': 'AimpDiscordBridge/5.0'})
cache_covers_imgbb = {}

# --- REGISTRY LOAD/SAVE ---
def check_startup_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_STARTUP, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except WindowsError: return False

def load_config():
    config = {
        'show_pause': True,
        'cover_source': "file_lastfm",
        'show_timeline': True,
        'icon_state': "dynamic", 
        'theme_current': themes_list[0]["nombre"],
        'text_name': "aimp",         
        'text_details': "title",
        'text_state': "artist",
        'text_large': "album",
        'show_name': "auto",
        'show_details': "auto",
        'show_state': "auto",
        'show_large': "auto",
        'status_display': "details",
        'language': "en"
    }
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG, 0, winreg.KEY_READ)
        config['show_pause'] = bool(winreg.QueryValueEx(key, "show_pause")[0])
        config['show_timeline'] = bool(winreg.QueryValueEx(key, "show_timeline")[0])
        for param in ['cover_source', 'icon_state', 'theme_current', 'text_name', 'text_details', 
                      'text_state', 'text_large', 'show_name', 'show_details', 'show_state', 
                      'show_large', 'status_display', 'language']:
            try: config[param] = winreg.QueryValueEx(key, param)[0]
            except: pass
        winreg.CloseKey(key)
    except Exception: pass
    return config

def save_config():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG)
        winreg.SetValueEx(key, "show_pause", 0, winreg.REG_DWORD, int(cfg_show_pause))
        winreg.SetValueEx(key, "show_timeline", 0, winreg.REG_DWORD, int(cfg_show_timeline))
        for param_name, param_val in [
            ("cover_source", cfg_cover_source), ("icon_state", cfg_icon_state), 
            ("theme_current", cfg_theme_current), ("text_name", cfg_text_name),
            ("text_details", cfg_text_details), ("text_state", cfg_text_state), 
            ("text_large", cfg_text_large), ("show_name", cfg_show_name), 
            ("show_details", cfg_show_details), ("show_state", cfg_show_state), 
            ("show_large", cfg_show_large), ("status_display", cfg_status_display),
            ("language", cfg_language)
        ]:
            winreg.SetValueEx(key, param_name, 0, winreg.REG_SZ, param_val)
        winreg.CloseKey(key)
    except Exception as e: logger(f"Error saving config: {e}")

cfg = load_config()
cfg_startup = check_startup_registry()
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

# Load the dictionary immediately
load_language(cfg_language)

def get_config_state_tuple():
    return (cfg_show_pause, cfg_cover_source, cfg_show_timeline, 
            cfg_icon_state, cfg_theme_current, cfg_text_name, 
            cfg_text_details, cfg_text_state, cfg_text_large, 
            cfg_show_name, cfg_show_details, cfg_show_state, cfg_show_large,
            cfg_status_display, cfg_language)

# --- SYSTEM TRAY UI ---
def build_icon_image():
    img = Image.new('RGB', (64, 64), color=(255, 128, 0)) 
    draw = ImageDraw.Draw(img)
    draw.polygon([(32, 12), (52, 48), (12, 48)], fill=(255, 255, 255)) 
    return img

def toggle_startup(icon, item):
    global cfg_startup
    cfg_startup = not cfg_startup
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_STARTUP, 0, winreg.KEY_SET_VALUE)
        if cfg_startup:
            ruta = f'"{sys.executable}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, ruta)
        else:
            try: winreg.DeleteValue(key, APP_NAME)
            except: pass
        winreg.CloseKey(key)
    except: pass

def set_radio(var_name, value):
    def setter(icon, item): 
        globals()[var_name] = value
        guardar_config_y_actualizar()
    return setter

def check_radio(var_name, value):
    return lambda item: globals()[var_name] == value

def set_toggle(var_name):
    def toggler(icon, item): 
        globals()[var_name] = not globals()[var_name]
        guardar_config_y_actualizar()
    return toggler

def guardar_config_y_actualizar():
    save_config()
    if sys._getframe(1).f_code.co_name == 'setter' and 'cfg_language' in globals():
        # If language changed, reload dict and rebuild menu
        load_language(cfg_language)
        icon.menu = build_dynamic_menu()

def exit_app(icon, item):
    global is_running
    logger("Closing AIMP Bridge...")
    is_running = False
    icon.stop()

def build_text_menu(var_text, var_show):
    return pystray.Menu(
        item(_('opt_show'), pystray.Menu(
            item(_('opt_always'), set_radio(var_show, 'always'), checked=check_radio(var_show, 'always'), radio=True),
            item(_('opt_auto'), set_radio(var_show, 'auto'), checked=check_radio(var_show, 'auto'), radio=True),
            item(_('opt_never'), set_radio(var_show, 'never'), checked=check_radio(var_show, 'never'), radio=True)
        )),
        item(_('opt_title'), set_radio(var_text, 'title'), checked=check_radio(var_text, 'title'), radio=True),
        item(_('opt_artist'), set_radio(var_text, 'artist'), checked=check_radio(var_text, 'artist'), radio=True),
        item(_('opt_album'), set_radio(var_text, 'album'), checked=check_radio(var_text, 'album'), radio=True),
        item(_('opt_aimp'), set_radio(var_text, 'aimp'), checked=check_radio(var_text, 'aimp'), radio=True),
        item(_('opt_custom'), set_radio(var_text, 'custom'), checked=check_radio(var_text, 'custom'), radio=True)
    )

def set_theme_ui(theme_name):
    def setter(icon, item):
        global cfg_theme_current, discord_connected, last_rpc_song, last_playback_state
        if cfg_theme_current != theme_name:
            cfg_theme_current = theme_name
            save_config()
            try: RPC.clear()
            except: pass
            discord_connected = False 
            last_rpc_song = ""
            last_playback_state = None
    return setter

def check_theme_ui(theme_name):
    return lambda item: cfg_theme_current == theme_name

def build_dynamic_menu():
    themes_menu_items = [item(t["nombre"], set_theme_ui(t["nombre"]), checked=check_theme_ui(t["nombre"]), radio=True) for t in themes_list]
    
    available_langs = [("English", "en"), ("Español", "es"), ("Português", "pt"), ("Русский", "ru"), ("中文", "zh")]
    lang_menu_items = [item(name, set_radio('cfg_language', code), checked=check_radio('cfg_language', code), radio=True) for name, code in available_langs]

    return pystray.Menu(
        item(_('menu_startup'), toggle_startup, checked=lambda i: cfg_startup),
        
        item(_('menu_displayed_texts'), pystray.Menu(
            item(_('menu_main_text'), build_text_menu('cfg_text_name', 'cfg_show_name')),
            item(_('menu_top_line'), build_text_menu('cfg_text_details', 'cfg_show_details')),
            item(_('menu_bottom_line'), build_text_menu('cfg_text_state', 'cfg_show_state')),
            item(_('menu_cover_tooltip'), build_text_menu('cfg_text_large', 'cfg_show_large')),
            item(_('menu_friend_list'), pystray.Menu(
                item(_('opt_name'), set_radio('cfg_status_display', 'name'), checked=check_radio('cfg_status_display', 'name'), radio=True),
                item(_('opt_details'), set_radio('cfg_status_display', 'details'), checked=check_radio('cfg_status_display', 'details'), radio=True),
                item(_('opt_state'), set_radio('cfg_status_display', 'state'), checked=check_radio('cfg_status_display', 'state'), radio=True)
            ))
        )),
        
        item(_('menu_playback_state'), pystray.Menu(
            item(_('menu_show_paused'), set_toggle('cfg_show_pause'), checked=lambda i: cfg_show_pause),
            item(_('menu_show_timeline'), set_toggle('cfg_show_timeline'), checked=lambda i: cfg_show_timeline),
            item(_('menu_album_cover'), pystray.Menu(
                item(_('opt_file'), set_radio('cfg_cover_source', 'file'), checked=check_radio('cfg_cover_source', 'file'), radio=True),
                item(_('opt_file_lastfm'), set_radio('cfg_cover_source', 'file_lastfm'), checked=check_radio('cfg_cover_source', 'file_lastfm'), radio=True),
                item(_('opt_lastfm_file'), set_radio('cfg_cover_source', 'lastfm_file'), checked=check_radio('cfg_cover_source', 'lastfm_file'), radio=True),
                item(_('opt_none'), set_radio('cfg_cover_source', 'none'), checked=check_radio('cfg_cover_source', 'none'), radio=True)
            )),
            item(_('menu_status_icon'), pystray.Menu(
                item(_('opt_dynamic'), set_radio('cfg_icon_state', 'dynamic'), checked=check_radio('cfg_icon_state', 'dynamic'), radio=True),
                item(_('opt_logo_only'), set_radio('cfg_icon_state', 'logo'), checked=check_radio('cfg_icon_state', 'logo'), radio=True),
                item(_('opt_none'), set_radio('cfg_icon_state', 'none'), checked=check_radio('cfg_icon_state', 'none'), radio=True)
            ))
        )),
        item(_('menu_theme'), pystray.Menu(*themes_menu_items)),
        item(_('menu_language'), pystray.Menu(*lang_menu_items)),
        item(_('menu_exit'), exit_app)
    )

icon = pystray.Icon("AIMP Bridge", build_icon_image(), "AIMP Discord Bridge", build_dynamic_menu())

# --- CORE FUNCTIONS ---
def connect_aimp():
    while is_running:
        try: return Client()
        except: time.sleep(3)

def is_valid_client_id(cid):
    return bool(cid and str(cid).isdigit() and len(str(cid)) >= 15)

def connect_discord_core(cid, max_retries=3):
    rpc = Presence(cid)
    for _ in range(max_retries):
        if not is_running: return None
        try:
            rpc.connect()
            logger(f"Connected to Discord ID: {cid}")
            return rpc
        except: time.sleep(2)
    return None

def connect_discord_safe(requested_cid):
    id_str = str(requested_cid).strip().lower()
    if not id_str or id_str == "default" or id_str == "none":
        return connect_discord_core(CLIENT_ID_DEFAULT), CLIENT_ID_DEFAULT
    if not is_valid_client_id(requested_cid):
        logger(f"Invalid Client ID '{requested_cid}'. Using default.")
        return connect_discord_core(CLIENT_ID_DEFAULT), CLIENT_ID_DEFAULT
    rpc = connect_discord_core(requested_cid)
    if rpc: return rpc, requested_cid
    logger(f"Failed to connect '{requested_cid}'. Using default.")
    return connect_discord_core(CLIENT_ID_DEFAULT), CLIENT_ID_DEFAULT

def extract_main_artist(raw_artist):
    parts = re.split(r'[;/,]| & | feat\. | ft\. | vs\. ', raw_artist, flags=re.IGNORECASE)
    return parts[0].strip()

# --- TEXT FORMATTING ---
def format_rpc_text(json_field, cfg_option, show_mode, info_dict, custom_data):
    if show_mode == "never": return None

    if cfg_option != "custom":
        map_dict = {"title": info_dict['titulo'], "artist": info_dict['artista'], "album": info_dict['album'], "aimp": "AIMP"}
        final_text = map_dict.get(cfg_option, "AIMP")
    else:
        text_list = custom_data.get(json_field, [""])
        if not text_list: return None
        
        rotation = max(5, custom_data.get("rotacion_segundos", 15))
        idx = int(time.time() / rotation) % len(text_list)
        chosen_text = str(text_list[idx])
        
        chosen_text = chosen_text.replace("{titulo}", info_dict['titulo'])
        chosen_text = chosen_text.replace("{artista}", info_dict['artista'])
        chosen_text = chosen_text.replace("{album}", info_dict['album'])
        final_text = chosen_text

    if not final_text or not str(final_text).strip(): return None

    if show_mode == "auto":
        empty_filters = [_("unknown_track"), _("unknown_artist"), _("unknown_album"), "Sencillo/Desconocido", "Artista Desconocido", "Pista Desconocida"]
        for f in empty_filters:
            if f in final_text: return None

    return final_text

# --- IMAGE FETCHING (MUTAGEN & LAST.FM) ---
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
        
        if hasattr(audio, 'pictures') and audio.pictures: 
            return audio.pictures[0].data
            
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
                        if 'image' in mime or frame_id in ['APIC', 'PIC']:
                            return tag_obj.data
            
            if hasattr(tags, 'keys'):
                for key in tags.keys():
                    if key.startswith("APIC") or key.startswith("PIC") or "cover" in key.lower() or key == "metadata_block_picture": 
                        return tags[key].data
    except: pass
    return None

def upload_to_imgbb(img_bytes):
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != 'RGB': img = img.convert('RGB')
        img.thumbnail((512, 512), Image.Resampling.LANCZOS) 
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        response = http_session.post("https://api.imgbb.com/1/upload", data={"key": API_KEY_IMGBB, "expiration": 604800}, files={"image": ("cover.jpg", output.getvalue(), "image/jpeg")}, timeout=10)
        if response.json().get("success"): return response.json()["data"]["url"]
    except: pass
    return None

force_cover_update = False
def async_cover_search(raw_artist, target_track, target_album, file_path, source_cfg, fallback_img):
    global current_cover, force_cover_update, cache_covers_imgbb
    final_url = fallback_img
    main_artist = extract_main_artist(raw_artist)

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
            if file_path in cache_covers_imgbb: return cache_covers_imgbb[file_path]
            img_bytes = extract_local_cover(file_path)
            if img_bytes:
                url_imgbb = upload_to_imgbb(img_bytes)
                if url_imgbb:
                    cache_covers_imgbb[file_path] = url_imgbb
                    return url_imgbb
        return None

    if source_cfg == "file": final_url = try_file() or fallback_img
    elif source_cfg == "file_lastfm": final_url = try_file() or try_lastfm() or fallback_img
    elif source_cfg == "lastfm_file": final_url = try_lastfm() or try_file() or fallback_img
    
    if target_track == last_rpc_song:
        current_cover = final_url
        force_cover_update = True

# --- MAIN EXECUTION ---
icon.run_detached()

current_theme_data = get_theme_data(cfg_theme_current)
requested_cid = current_theme_data.get("client_id", "default")

RPC, active_client_id = connect_discord_safe(requested_cid)
discord_connected = RPC is not None
aimp = connect_aimp()
aimp_connected = True

last_rpc_song = ""
last_discord_song = ""
last_playback_state = None
last_aimp_pos = 0
current_cover = current_theme_data.get("large_image", "logo")
last_discord_update = time.time() 
last_evaluated_texts = ("", "", "", "")
last_config_state = get_config_state_tuple()

while is_running:
    current_config_state = get_config_state_tuple()
    config_changed = current_config_state != last_config_state
    
    current_theme_data = get_theme_data(cfg_theme_current)
    requested_cid = current_theme_data.get("client_id", "default")
    processed_req_id = CLIENT_ID_DEFAULT if (not requested_cid or str(requested_cid).lower() == "default") else requested_cid
    
    if processed_req_id != active_client_id and discord_connected:
        if RPC:
            try:
                RPC.clear()
                RPC.close() 
            except: pass
        discord_connected = False 

    # Reconnection Engine
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
            time.sleep(2)
            continue
    
    if not aimp_connected:
        aimp = connect_aimp()
        aimp_connected = True

    try:
        aimp.detect_aimp() 
        p_state = aimp.get_playback_state()
        info = aimp.get_current_track_info()
        live_custom_data = load_custom_texts()

        if info and p_state != PlayBackState.Stopped:
            if p_state == PlayBackState.Paused and not cfg_show_pause:
                if last_playback_state != PlayBackState.Stopped or config_changed:
                    try: RPC.clear()
                    except: pass
                    last_playback_state = PlayBackState.Stopped
                    last_discord_song = "" 
                last_config_state = current_config_state
                time.sleep(2)
                continue

            track_name = info.get('title', _('unknown_track')) or _('unknown_track')
            album_name = info.get('album', _('unknown_album')) or _('unknown_album')
            artist_name = info.get('artist', _('unknown_artist')) or _('unknown_artist')
            file_path = info.get('filename', '')
            pos_sec = int(aimp.get_player_position() / 1000)
            duration_sec = int(info['duration'] / 1000)

            theme_fallback_img = current_theme_data.get("large_image", "logo")

            if track_name != last_rpc_song:
                last_rpc_song = track_name
                current_cover = theme_fallback_img
                if cfg_cover_source != "none":
                    threading.Thread(target=async_cover_search, args=(artist_name, track_name, album_name, file_path, cfg_cover_source, theme_fallback_img), daemon=True).start()
                else: force_cover_update = True

            jump_offset = abs(pos_sec - (last_aimp_pos + 2))
            did_seek = jump_offset > 3 

            if p_state == PlayBackState.Playing:
                v_start = int(time.time()) - pos_sec
                v_end = v_start + duration_sec
                v_small_icon = current_theme_data.get("small_play", "play")
                v_txt_state = _('status_playing')
            else:
                v_start = None; v_end = None
                v_small_icon = current_theme_data.get("small_pause", "pause")
                v_txt_state = _('status_paused')

            # ----------------- TEXT PROCESSING -----------------
            dict_info = {"titulo": track_name, "artista": artist_name, "album": album_name}
            
            t_name = format_rpc_text("name", cfg_text_name, cfg_show_name, dict_info, live_custom_data)
            t_details = format_rpc_text("details", cfg_text_details, cfg_show_details, dict_info, live_custom_data)
            t_state = format_rpc_text("state", cfg_text_state, cfg_show_state, dict_info, live_custom_data)
            t_large = format_rpc_text("large_text", cfg_text_large, cfg_show_large, dict_info, live_custom_data)

            # Pad short strings to avoid Discord crash
            t_name = (t_name + " ") if (t_name is not None and len(t_name) < 2) else t_name
            t_details = (t_details + " ") if (t_details is not None and len(t_details) < 2) else t_details
            t_state = (t_state + " ") if (t_state is not None and len(t_state) < 2) else t_state
            t_large = (t_large + " ") if (t_large is not None and len(t_large) < 2) else t_large

            current_texts = (t_name, t_details, t_state, t_large)
            texts_rotated = current_texts != last_evaluated_texts
            force_timer = (time.time() - last_discord_update) > 5

            if (track_name != last_discord_song or p_state != last_playback_state or did_seek or force_timer or config_changed or force_cover_update or texts_rotated):
                
                img_send = theme_fallback_img if cfg_cover_source == "none" else current_cover
                time_start = v_start if cfg_show_timeline else None
                time_end = v_end if cfg_show_timeline else None
                
                if cfg_icon_state == "logo": s_img = theme_fallback_img; s_txt = "AIMP"
                elif cfg_icon_state == "none": s_img = None; s_txt = None
                else: s_img = v_small_icon; s_txt = v_txt_state

                search_artist = extract_main_artist(artist_name)
                q_str = urllib.parse.quote(f"{search_artist} {track_name}")
                
                type_display = StatusDisplayType.DETAILS
                if cfg_status_display == 'name': type_display = StatusDisplayType.NAME
                elif cfg_status_display == 'state': type_display = StatusDisplayType.STATE
                
                try:
                    RPC.update(
                        name=t_name[:128] if t_name else None, 
                        details=t_details[:128] if t_details else None, 
                        state=t_state[:128] if t_state else None, 
                        large_image=img_send, 
                        large_text=t_large[:128] if t_large else None, 
                        small_image=s_img, 
                        small_text=s_txt,
                        start=time_start, 
                        end=time_end,
                        buttons=[{"label": "Spotify", "url": f"https://open.spotify.com/search/{q_str}"}, {"label": "YouTube", "url": f"https://www.youtube.com/results?search_query={q_str}"}],
                        activity_type=ActivityType.LISTENING, 
                        status_display_type=type_display
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
    
    time.sleep(2)

if RPC:
    try:
        RPC.clear()
        RPC.close()
    except: pass
sys.exit(0)
