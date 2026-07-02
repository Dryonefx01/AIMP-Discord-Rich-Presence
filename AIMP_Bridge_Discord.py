import time
import requests
import urllib.parse
import sys
import os
import re
import threading 
import winreg 
import ctypes 
import io # NUEVO: Para procesar imágenes en RAM
from pyaimp import Client, PlayBackState
from pypresence import Presence, ActivityType, StatusDisplayType

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from mutagen import File

# --- PREVENCIÓN DE MÚLTIPLES INSTANCIAS ---
mutex_name = "AIMP_Bridge_Discord_Mutex"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
if ctypes.windll.kernel32.GetLastError() == 183: 
    sys.exit(0) 

# --- CONFIGURACIÓN ---
client_id_discord = '1489090870681669745'
api_key_lastfm = 'c3a6e1f0b0724b9d59f8064c59958072'
API_KEY_IMGBB = 'e13e30d4ddd73e6f4dc33fe2d7167b05' 
REG_PATH_STARTUP = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_PATH_CONFIG = r"Software\AIMP_Bridge_Discord"
APP_NAME = "AIMP_Bridge_Discord"

# --- CORRECCIÓN ERROR DE PERMISOS ---
if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

sys.stderr = open(os.path.join(app_path, "error_log.txt"), "a")
sys.stdout = open(os.path.join(app_path, "bridge_log.txt"), "a")

def logger(mensaje):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}", flush=True)

http_session = requests.Session()
http_session.headers.update({'user-agent': 'AimpDiscordBridge/3.6'})

# Memoria Caché para no re-subir imágenes a ImgBB en la misma sesión
cache_portadas_imgbb = {}

# --- SISTEMA DE GUARDADO (REGISTRO DE WINDOWS) ---
def leer_registro_inicio():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_STARTUP, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except WindowsError:
        return False

def cargar_configuracion():
    config = {
        'mostrar_pausa': True,
        'fuente_caratula': "Archivo_Lastfm", # NUEVA VARIABLE: Prioridad Local
        'mostrar_linea': True,
        'icono_estado': "Dinamico", 
        'titulo_actividad': "Título",
        'tipo_texto': "AIMP"
    }
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG, 0, winreg.KEY_READ)
        config['mostrar_pausa'] = bool(winreg.QueryValueEx(key, "mostrar_pausa")[0])
        config['mostrar_linea'] = bool(winreg.QueryValueEx(key, "mostrar_linea")[0])
        config['icono_estado'] = winreg.QueryValueEx(key, "icono_estado")[0]
        config['titulo_actividad'] = winreg.QueryValueEx(key, "titulo_actividad")[0]
        config['tipo_texto'] = winreg.QueryValueEx(key, "tipo_texto")[0]
        
        # Manejo de la nueva variable que reemplaza el booleano antiguo
        try: config['fuente_caratula'] = winreg.QueryValueEx(key, "fuente_caratula")[0]
        except: pass
        
        winreg.CloseKey(key)
    except Exception:
        pass
    return config

def guardar_configuracion():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH_CONFIG)
        winreg.SetValueEx(key, "mostrar_pausa", 0, winreg.REG_DWORD, int(config_mostrar_pausa))
        winreg.SetValueEx(key, "fuente_caratula", 0, winreg.REG_SZ, config_fuente_caratula)
        winreg.SetValueEx(key, "mostrar_linea", 0, winreg.REG_DWORD, int(config_mostrar_linea))
        winreg.SetValueEx(key, "icono_estado", 0, winreg.REG_SZ, config_icono_estado)
        winreg.SetValueEx(key, "titulo_actividad", 0, winreg.REG_SZ, config_titulo_actividad)
        winreg.SetValueEx(key, "tipo_texto", 0, winreg.REG_SZ, config_tipo_texto)
        winreg.CloseKey(key)
    except Exception as e:
        logger(f"Error guardando configuración: {e}")

config_iniciar_windows = leer_registro_inicio()
cfg_cargada = cargar_configuracion()

config_mostrar_pausa = cfg_cargada['mostrar_pausa']
config_fuente_caratula = cfg_cargada['fuente_caratula']
config_mostrar_linea = cfg_cargada['mostrar_linea']
config_icono_estado = cfg_cargada['icono_estado']
config_titulo_actividad = cfg_cargada['titulo_actividad']
config_tipo_texto = cfg_cargada['tipo_texto']
ejecutando = True 

def get_config_state():
    return (config_mostrar_pausa, config_fuente_caratula, config_mostrar_linea, 
            config_icono_estado, config_titulo_actividad, config_tipo_texto)

# --- FUNCIONES DE LA INTERFAZ (TRAY UI) ---
def crear_icono_dinamico():
    imagen = Image.new('RGB', (64, 64), color=(255, 128, 0)) 
    draw = ImageDraw.Draw(imagen)
    draw.polygon([(32, 12), (52, 48), (12, 48)], fill=(255, 255, 255)) 
    return imagen

def toggle_iniciar_windows(icon, item):
    global config_iniciar_windows
    config_iniciar_windows = not config_iniciar_windows
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH_STARTUP, 0, winreg.KEY_SET_VALUE)
        if config_iniciar_windows:
            if getattr(sys, 'frozen', False): ruta = f'"{sys.executable}"' 
            else: ruta = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"' 
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, ruta)
        else:
            try: winreg.DeleteValue(key, APP_NAME)
            except: pass
        winreg.CloseKey(key)
    except Exception as e:
        logger(f"Error modificando auto-inicio: {e}")

def set_radio(var_name, valor):
    def setter(icon, item): 
        globals()[var_name] = valor
        guardar_configuracion()
    return setter

def check_radio(var_name, valor):
    return lambda item: globals()[var_name] == valor

def set_toggle(var_name):
    def toggler(icon, item): 
        globals()[var_name] = not globals()[var_name]
        guardar_configuracion()
    return toggler

def salir_programa(icon, item):
    global ejecutando
    logger("Cerrando AIMP Bridge...")
    ejecutando = False
    icon.stop()

menu_ui = pystray.Menu(
    item('Iniciar con Windows', toggle_iniciar_windows, checked=lambda i: config_iniciar_windows),
    
    item('Título de la Actividad', pystray.Menu(
        item('Título', set_radio('config_titulo_actividad', 'Título'), checked=check_radio('config_titulo_actividad', 'Título'), radio=True),
        item('Artista', set_radio('config_titulo_actividad', 'Artista'), checked=check_radio('config_titulo_actividad', 'Artista'), radio=True),
        item('Álbum', set_radio('config_titulo_actividad', 'Álbum'), checked=check_radio('config_titulo_actividad', 'Álbum'), radio=True),
        item('AIMP', set_radio('config_titulo_actividad', 'AIMP'), checked=check_radio('config_titulo_actividad', 'AIMP'), radio=True)
    )),
    
    item('Tipo de Actividad', pystray.Menu(
        item('Título', set_radio('config_tipo_texto', 'Título'), checked=check_radio('config_tipo_texto', 'Título'), radio=True),
        item('Artista', set_radio('config_tipo_texto', 'Artista'), checked=check_radio('config_tipo_texto', 'Artista'), radio=True),
        item('Álbum', set_radio('config_tipo_texto', 'Álbum'), checked=check_radio('config_tipo_texto', 'Álbum'), radio=True),
        item('AIMP', set_radio('config_tipo_texto', 'AIMP'), checked=check_radio('config_tipo_texto', 'AIMP'), radio=True)
    )),

    item('Estado de Reproducción', pystray.Menu(
        item('Mostrar Estado en Pausa', set_toggle('config_mostrar_pausa'), checked=lambda i: config_mostrar_pausa),
        item('Mostrar Línea de Tiempo', set_toggle('config_mostrar_linea'), checked=lambda i: config_mostrar_linea),
        
        # --- NUEVA LISTA REEMPLAZANDO EL VIEJO TOGGLE ---
        item('Carátula del Álbum', pystray.Menu(
            item('Usar Desde el Archivo', set_radio('config_fuente_caratula', 'Archivo'), checked=check_radio('config_fuente_caratula', 'Archivo'), radio=True),
            item('Extraer del Archivo o de Last.fm', set_radio('config_fuente_caratula', 'Archivo_Lastfm'), checked=check_radio('config_fuente_caratula', 'Archivo_Lastfm'), radio=True),
            item('Extraer de Last.fm o del Archivo', set_radio('config_fuente_caratula', 'Lastfm_Archivo'), checked=check_radio('config_fuente_caratula', 'Lastfm_Archivo'), radio=True),
            item('No Mostrar', set_radio('config_fuente_caratula', 'Ninguna'), checked=check_radio('config_fuente_caratula', 'Ninguna'), radio=True)
        )),
        
        item('Ícono de Estado', pystray.Menu(
            item('Dinámico (Play/Pausa)', set_radio('config_icono_estado', 'Dinamico'), checked=check_radio('config_icono_estado', 'Dinamico'), radio=True),
            item('Solo Logo', set_radio('config_icono_estado', 'Solo Logo'), checked=check_radio('config_icono_estado', 'Solo Logo'), radio=True),
            item('No Mostrar', set_radio('config_icono_estado', 'No Mostrar'), checked=check_radio('config_icono_estado', 'No Mostrar'), radio=True)
        ))
    )),
    
    item('Tema', pystray.Menu(
        item('(Próximamente)', lambda icon, item: None, enabled=False)
    )),
    
    item('Salir', salir_programa)
)

icon = pystray.Icon("AIMP Bridge", crear_icono_dinamico(), "AIMP Discord Bridge", menu_ui)

# --- FUNCIONES CORE ---
def conectar_aimp():
    while ejecutando:
        try: return Client()
        except Exception: time.sleep(3)

def conectar_discord():
    rpc = Presence(client_id_discord)
    while ejecutando:
        try: rpc.connect(); return rpc
        except: time.sleep(3)

def extraer_artista_principal(artista_raw):
    partes = re.split(r'[;/,]| & | feat\. | ft\. | vs\. ', artista_raw, flags=re.IGNORECASE)
    return partes[0].strip()

# --- FUNCIONES DE IMÁGENES (LAST.FM, LOCAL, IMGBB) ---
def get_album_art_lastfm(artist, track, album_name):
    track_clean = track.replace(".flac", "").replace(".mp3", "").strip()
    album_target = album_name.lower().strip() if album_name else ""
    try:
        url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key_lastfm}&artist={urllib.parse.quote(artist)}&track={urllib.parse.quote(track_clean)}&format=json"
        data = http_session.get(url, timeout=5).json()
        if 'track' in data and 'album' in data['track']:
            img = data['track']['album']['image'][-1]['#text']
            if img and (data['track']['album'].get('title', "").lower().strip() == album_target or album_target in ["", "album", "sencillo/desconocido"]):
                return img
    except: pass
    try:
        if album_target and album_target not in ["", "album", "sencillo/desconocido"]:
            url_album = f"http://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={api_key_lastfm}&artist={urllib.parse.quote(artist)}&album={urllib.parse.quote(album_name)}&format=json"
            data_album = http_session.get(url_album, timeout=5).json()
            if 'album' in data_album:
                img_album = data_album['album']['image'][-1]['#text']
                if img_album: return img_album
    except: pass
    return None

def extraer_portada_local(ruta_archivo):
    try:
        if not os.path.exists(ruta_archivo): return None
        audio = File(ruta_archivo)
        if audio is None: return None
        if "APIC:" in audio: return audio["APIC:"].data
        for key in audio.keys():
            if key.startswith("APIC"): return audio[key].data
        if hasattr(audio, 'pictures') and audio.pictures: return audio.pictures[0].data
        if "covr" in audio: return audio["covr"][0]
    except Exception as e:
        logger(f"Error extrayendo carátula local: {e}")
    return None

def optimizar_y_subir_imgbb(bytes_imagen):
    """NUEVO: Comprime la imagen en memoria antes de subirla para que sea instantáneo"""
    try:
        # Optimización
        img = Image.open(io.BytesIO(bytes_imagen))
        if img.mode != 'RGB': img = img.convert('RGB')
        img.thumbnail((512, 512), Image.Resampling.LANCZOS) # Discord no necesita más que 512px
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        bytes_optimizados = output.getvalue()
        
        # Subida
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": API_KEY_IMGBB, "expiration": 604800}
        files = {"image": ("cover.jpg", bytes_optimizados, "image/jpeg")}
        
        response = http_session.post(url, data=payload, files=files, timeout=10)
        data = response.json()
        
        if data.get("success"):
            return data["data"]["url"]
    except Exception as e:
        logger(f"Error optimizando/subiendo a ImgBB: {e}")
    return None


# --- CONTROLADOR DEL HILO ASÍNCRONO MULTI-OPCIÓN ---
forzar_update_portada = False

def buscar_portada_async(artista_raw, cancion_objetivo, album_objetivo, ruta_archivo, fuente_config):
    global portada_actual, forzar_update_portada, cache_portadas_imgbb
    
    url_final = "logo"
    artista_principal = extraer_artista_principal(artista_raw)

    def intentar_lastfm():
        url_lfm = get_album_art_lastfm(artista_raw, cancion_objetivo, album_objetivo)
        if not url_lfm and artista_principal != artista_raw:
            url_lfm = get_album_art_lastfm(artista_principal, cancion_objetivo, album_objetivo)
        
        if url_lfm:
            try:
                if http_session.head(url_lfm, timeout=3).status_code == 200:
                    return url_lfm
            except: pass
        return None

    def intentar_archivo():
        if ruta_archivo and os.path.exists(ruta_archivo):
            # Check rápido de caché
            if ruta_archivo in cache_portadas_imgbb:
                return cache_portadas_imgbb[ruta_archivo]
                
            bytes_foto = extraer_portada_local(ruta_archivo)
            if bytes_foto:
                url_imgbb = optimizar_y_subir_imgbb(bytes_foto)
                if url_imgbb:
                    cache_portadas_imgbb[ruta_archivo] = url_imgbb # Guardamos para la próxima vez
                    return url_imgbb
        return None

    # LÓGICA DE PRIORIDADES
    if fuente_config == "Archivo":
        url_final = intentar_archivo() or "logo"
        
    elif fuente_config == "Archivo_Lastfm":
        url_final = intentar_archivo()
        if not url_final:
            url_final = intentar_lastfm() or "logo"
            
    elif fuente_config == "Lastfm_Archivo":
        url_final = intentar_lastfm()
        if not url_final:
            url_final = intentar_archivo() or "logo"
    
    # Validamos que no se haya cambiado de canción durante los procesos web
    if cancion_objetivo == ultima_cancion_rpc:
        portada_actual = url_final
        forzar_update_portada = True
        if url_final != "logo": logger(f"Portada resuelta vía {fuente_config}: {url_final}")
# --------------------------------------------------

# --- INICIO ---
icon.run_detached()

RPC = conectar_discord()
aimp = conectar_aimp()

discord_conectado = True
aimp_conectado = True

ultima_cancion_rpc = ""
ultima_cancion_en_discord = ""
ultimo_estado = None
ultima_posicion_aimp = 0
portada_actual = "logo"
ultimo_update_discord = time.time() 

ultimo_estado_config = get_config_state()

while ejecutando:
    if not discord_conectado:
        RPC = conectar_discord()
        discord_conectado = True
        ultimo_update_discord = time.time()
    
    if not aimp_conectado:
        aimp = conectar_aimp()
        aimp_conectado = True

    try:
        aimp.detect_aimp() 
        estado_aimp = aimp.get_playback_state()
        info = aimp.get_current_track_info()
        
        estado_config_actual = get_config_state()
        config_cambiada = estado_config_actual != ultimo_estado_config

        if info and estado_aimp != PlayBackState.Stopped:
            
            if estado_aimp == PlayBackState.Paused and not config_mostrar_pausa:
                if ultimo_estado != PlayBackState.Stopped or config_cambiada:
                    try: RPC.clear()
                    except: pass
                    ultimo_estado = PlayBackState.Stopped
                    ultima_cancion_en_discord = "" 
                ultimo_estado_config = estado_config_actual
                time.sleep(2)
                continue

            cancion = info.get('title', 'Pista Desconocida') or "Pista Desconocida"
            album = info.get('album', 'Sencillo/Desconocido') or "Sencillo/Desconocido"
            artista_raw = info.get('artist', 'Artista Desconocido') or "Artista Desconocido"
            ruta_cancion_actual = info.get('filename', '')

            posicion_actual = int(aimp.get_player_position() / 1000)
            duracion_total = int(info['duration'] / 1000)

            if cancion != ultima_cancion_rpc:
                ultima_cancion_rpc = cancion
                portada_actual = "logo" 
                
                if config_fuente_caratula != "Ninguna":
                    logger(f"Procesando: {cancion}")
                    threading.Thread(
                        target=buscar_portada_async, 
                        args=(artista_raw, cancion, album, ruta_cancion_actual, config_fuente_caratula), 
                        daemon=True
                    ).start()
                else:
                    forzar_update_portada = True # Activa el logo directo

            desfase = abs(posicion_actual - (ultima_posicion_aimp + 2))
            hizo_salto = desfase > 3 

            if estado_aimp == PlayBackState.Playing:
                v_start = int(time.time()) - posicion_actual
                v_end = v_start + duracion_total
                v_small_default = "play"; txt_estado = "Reproduciendo"
            else:
                v_start = None; v_end = None
                v_small_default = "pause"; txt_estado = "Pausado"

            forzar_update = (time.time() - ultimo_update_discord) > 5

            if (cancion != ultima_cancion_en_discord or 
                estado_aimp != ultimo_estado or 
                hizo_salto or 
                forzar_update or 
                config_cambiada or 
                forzar_update_portada):
                
                mapa_textos = {"Título": cancion, "Artista": artista_raw, "Álbum": album, "AIMP": "AIMP"}
                
                txt_details = mapa_textos.get(config_titulo_actividad, cancion)
                txt_name = mapa_textos.get(config_tipo_texto, "AIMP")
                
                txt_details = txt_details + " " if len(txt_details) < 2 else txt_details
                txt_name = txt_name + " " if len(txt_name) < 2 else txt_name

                # Aplicar la decisión final de la portada
                img_enviar = "logo" if config_fuente_caratula == "Ninguna" else portada_actual
                
                t_start_enviar = v_start if config_mostrar_linea else None
                t_end_enviar = v_end if config_mostrar_linea else None
                
                if config_icono_estado == "Solo Logo":
                    s_img_enviar = "logo"; s_txt_enviar = "AIMP"
                elif config_icono_estado == "No Mostrar":
                    s_img_enviar = None; s_txt_enviar = None
                else: 
                    s_img_enviar = v_small_default; s_txt_enviar = txt_estado

                artista_busqueda = extraer_artista_principal(artista_raw)
                q = urllib.parse.quote(f"{artista_busqueda} {cancion}")
                
                try:
                    RPC.update(
                        name=txt_name[:128], 
                        details=txt_details[:128], 
                        state=f"de {artista_raw[:100]}", 
                        large_image=img_enviar, 
                        large_text=album[:128],
                        small_image=s_img_enviar, 
                        small_text=s_txt_enviar,
                        start=t_start_enviar, 
                        end=t_end_enviar,
                        buttons=[
                            {"label": "Spotify", "url": f"https://open.spotify.com/search/{q}"},
                            {"label": "YouTube", "url": f"https://www.youtube.com/results?search_query={q}"}
                        ],
                        activity_type=ActivityType.LISTENING,
                        status_display_type=StatusDisplayType.DETAILS
                    )
                    ultima_cancion_en_discord = cancion
                    ultimo_estado = estado_aimp
                    ultimo_update_discord = time.time()
                    ultimo_estado_config = estado_config_actual
                    forzar_update_portada = False 
                    
                except Exception:
                    discord_conectado = False
                    ultimo_estado = None 
                
            ultima_posicion_aimp = posicion_actual
        else:
            if ultimo_estado != PlayBackState.Stopped:
                aimp.detect_aimp() 
                try: RPC.clear()
                except: pass
                ultima_cancion_rpc = ""
                ultima_cancion_en_discord = ""
                ultimo_estado = PlayBackState.Stopped

    except (RuntimeError, Exception):
        aimp_conectado = False
        ultima_cancion_rpc = ""
        ultima_cancion_en_discord = ""
        ultimo_estado = None
        try: RPC.clear()
        except: pass
    
    time.sleep(2)

try: RPC.clear()
except: pass
sys.exit(0)
