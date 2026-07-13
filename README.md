# AIMP Discord Rich Presence Bridge <img width="38" height="38" alt="Sin título" src="https://github.com/user-attachments/assets/2d9d86d0-f60a-4fd0-999a-b6a933a13869" />


Elevate your Discord profile by seamlessly syncing your AIMP music player activity in real-time. 

This standalone Python application acts as a bridge between AIMP and Discord, providing a highly customizable Rich Presence experience. It goes beyond simple playback status by allowing you to display album art, track timelines, dynamic status icons, and custom animated themes directly on your Discord profile.

[Activity.webm](https://github.com/user-attachments/assets/f53b6220-945e-4400-866e-fb00ebc6078b)

## ✨ Key Features

* **Ultra-Low Latency:** Optimized internal loop (0.5s refresh rate) ensures near-instant synchronization when changing tracks, pausing, or resuming.
* **System Tray GUI:** Fully configurable via a native Windows system tray menu (built with `pystray` and `Tkinter`). No need to edit code or configuration files manually.
* **Advanced Metadata Retrieval:** Smart priority system that fetches high-quality album art using the Last.fm API or directly from your local audio files (temporarily uploaded via ImgBB API).
* **Start with Windows:** Seamless registry integration allows the script to boot silently in the background alongside your OS.
* **Secure & Stable:** Includes native token obfuscation, robust error handling for abrupt disconnects, and single-instance locks (`Mutex`) to prevent duplicate processes.
* **Multi-Language Support:** Localized interface generated automatically via JSON files in the `locales` folder.

---

## 🚀 Installation & Setup

1. Go to the [Releases](https://github.com/Dryonefx01/AIMP-Discord-Rich-Presence/releases) page and download the latest `.exe` file.
2. Place the executable in a dedicated folder.
3. Run the application. A small AIMP icon will appear in your Windows System Tray (bottom right corner of your screen).

⚠️ **Upgrading from v1.0 or v2.0?**
If you are upgrading from an older version, please download and run the [`clean_legacy.bat`](https://github.com/Dryonefx01/AIMP-Discord-Rich-Presence/releases/download/v3.0-m-Complete_Edition/clean_legacy.bat) script included in the release first. This will safely wipe old corrupted Windows Registry entries and outdated configuration files from your `AppData` folder to ensure a clean installation for v3.0.

---

## ⚙️ Configuration Guide

All settings can be accessed by right-clicking the AIMP Bridge icon in your Windows notification area (System Tray)<img width="22" height="19" alt="imagen" src="https://github.com/user-attachments/assets/4b1e874d-6b25-429f-9a69-3e65044aa1d5" />
.

<img width="444" height="195" alt="imagen" src="https://github.com/user-attachments/assets/ff28ac02-c02b-44e5-a7f5-213aaba4503a" />  


### 1. Activity Display Options
Configure exactly what information is shown on the first and second lines of your Discord status.
* **Activity Title (Top Line):** Choose to display the Song Title, Artist, Album, or the App Name.
* **Activity Type (Bottom Line):** Choose the secondary information to display. 

### 2. Playback State Settings
* **Show Paused State:** If enabled, your Rich Presence will remain visible but indicate that the song is paused. If disabled, the presence disappears from Discord entirely when AIMP is paused.
* **Show Timeline:** Displays a live progress bar showing elapsed time and total track duration.

<img width="442" height="188" alt="imagen" src="https://github.com/user-attachments/assets/cdbce116-681a-4474-89b3-8dd3f6d58615" />  <img width="444" height="182" alt="imagen" src="https://github.com/user-attachments/assets/0f9b6d52-ca52-4f84-ba89-450991c216a6" />



### 3. Album Cover Source Priority
The script requires a way to display images on Discord. You can configure the priority:
* **Extract from File -> Last.fm:** Tries to get the local cover art via ImgBB first. If it fails, falls back to Last.fm.
* **Last.fm -> Extract from File:** Tries to fetch metadata globally from Last.fm first.
* **Do Not Show:** Displays the `"large_image"` of `themes.json` background instead of album art.

<img width="418" height="182" alt="imagen" src="https://github.com/user-attachments/assets/bbdf693e-e64f-425d-8e2f-2a6cfb99312b" />  


### 4. Status Icons
This controls the small circular badge that appears in the bottom right corner of your main album cover.
* **Dynamic (Play/Pause):** Shows a "Play" or "Pause" icon depending on AIMP's current state.
* **Just Logo:** Always displays the `"large_image"` of `themes.json`.
* **Do Not Show:** Hides the small badge completely.

<img width="417" height="157" alt="imagen" src="https://github.com/user-attachments/assets/b554248c-de42-4357-b298-5ee5076f203e" />  

<img width="124" height="168" alt="imagen" src="https://github.com/user-attachments/assets/793578ae-1902-4805-9a10-1f5ac49cf53f" />  <img width="123" height="168" alt="imagen" src="https://github.com/user-attachments/assets/d150ba8b-1a61-484e-96c7-e52f5a9cf30f" />  <img width="122" height="169" alt="imagen" src="https://github.com/user-attachments/assets/331b1dca-1507-4b0d-b04b-6a3aeccbf6e5" />

### 5. Displayed Texts Detailed Options
Inside the "Activity Title" and "Activity Type" menus, you have full control over what text is actively pulled from AIMP. You can select any of the following "Show" options for either line:
* **Show Song Title:** Displays the name of the track currently playing.
* **Show Artist:** Displays the artist of the current track.
* **Show Album:** Displays the album name.
* **Show App Name:** Displays a static text (e.g., "AIMP") to let people know what player you are using.

<img width="453" height="160" alt="imagen" src="https://github.com/user-attachments/assets/6e8e9808-6055-46c6-aab0-b4bb757127e4" />  <img width="389" height="140" alt="imagen" src="https://github.com/user-attachments/assets/bd269e2c-9f1f-489d-82e6-9afe4768e314" />  <img width="388" height="160" alt="imagen" src="https://github.com/user-attachments/assets/06597bd2-06a5-4b83-be83-43b78eadcc44" />  <img width="410" height="115" alt="imagen" src="https://github.com/user-attachments/assets/0bfe44a3-7e43-4594-bab3-65a64df8165e" />

### 6. Start with Windows (Autostart)
* **Start with Windows:** Found at the top of the GUI menu, enabling this option creates a safe Windows Registry key that automatically launches the AIMP Bridge in the background every time you turn on your PC.

<img width="237" height="165" alt="imagen" src="https://github.com/user-attachments/assets/23d63fcf-1e3a-4cf5-8959-8171e8d8fbfd" />

---

## 🎨 Themes & Custom Animations (GIF Support)

One of the most powerful features of AIMP Bridge is the Theme Engine. You are not limited to static images! 

Through the `themes` configuration, **you can add animated images (GIFs)** to your Discord Presence for a truly unique look. You can customize how icons and buttons appear both in the Rich Presence and within the application's GUI.

For a detailed example of how to structure your theme file to include GIFs and custom assets, please check the default theme template here:
👉[themes.json](https://github.com/Dryonefx01/AIMP-Discord-Rich-Presence/blob/main/Themes/themes.json)

---

## 📂 Advanced Customization (AppData JSON Files)

When you run AIMP Bridge for the first time, it automatically generates a configuration folder located at `%APPDATA%\AIMP_Bridge_Discord`. 

While your standard GUI preferences (like showing the timeline or chosen text options) are saved directly and safely to your Windows Registry, the script generates several `.json` files in this folder for **Advanced Customization**. You can edit these files with any text editor (like Notepad) to unlock powerful features.

### 1. `custom_texts.json` (Animated & Custom Status Text)
This file controls the text displayed when you select the **"Custom (JSON)"** option in the GUI under the *Displayed Texts* or *Friend List Text* menus.
* **How it links to the UI:** Right-click the tray icon ➔ `Displayed Texts` ➔ `...` ➔ `Custom (JSON)`.
* **Features:** It allows you to create rotating text animations and use dynamic variables.
* **Keys & Values:**
    * `name`, `details`, `state`, `large_text`, `friend_list`: These arrays correspond to different lines on your Discord presence. 
    * `text`: The string to display. You can use variables that the script will auto-replace: `{title}` (Song name), `{artist}` (Artist name), and `{album}` (Album name).
    * `time`: The amount of time (in seconds) that specific text will be displayed before rotating to the next one in the bracket `[]`.

**Example:**
```json
"details": [
    {"text": "🎧 Listening to {title}", "time": 5},
    {"text": "👤 By {artist}", "time": 5}
]
```
*(This will make your second line swap between the song name and the artist every 5 seconds!)*

### 2. `themes.json` (Visuals & Animations)
This file is the core of the **Theme Engine**. It allows you to define exactly what images or animated GIFs are displayed on your Discord profile.
* **How it links to the UI:** The themes defined in this file automatically populate the **"Theme"** dropdown list in the GUI. 
* **Keys & Values:**
    * `name`: The name of the theme as it will appear in your tray menu.
    * `client_id`: The Discord Developer Application ID. Leave as `"default"` to use the script's built-in App ID, or paste your own if you want a custom Application Name.
    * `large_image`: The default fallback cover image. You can paste a direct Imgur link or a Discord attachment link (including `.gif`!).
    * `small_play` / `small_pause`: The links or asset names for the dynamic status icons (bottom right corner of the cover).

<img width="474" height="239" alt="imagen" src="https://github.com/user-attachments/assets/bcd98173-3717-4189-8637-5357b8f2ead2" />

### 3. `auto_themes.json` (Smart Theme Switching)
Want your theme to change based on what you are listening to? This file handles dynamic theme swapping.
* **How it links to the UI:** Select **"Custom (Auto-Switch)"** or **"Automatic (Random Theme)"** in the `Theme` menu. You can quickly edit this file by clicking `Custom Theme Rules` ➔ `Edit auto_themes.json`.
* **Keys & Values:**
    * `fallback_theme`: The name of the theme to use if no rules match.
    * `timer_rotation_enabled`: (`true`/`false`) Enables switching themes based on time.
    * `timer_rotation`: An array of themes and the `time` (in seconds) they should remain active before switching.
    * `file_rules`: The most powerful feature. It checks the song's file path or track name against the `match` string. If it matches, it applies the specified `theme`. (e.g., If `match` is "C:\\Vocaloid", apply the "Hatsune Miku" theme). Use `"__AUTOMATIC__"` as the theme value to pick a random theme from your `themes.json`.

<img width="445" height="199" alt="imagen" src="https://github.com/user-attachments/assets/d7af4916-86cd-4c14-8467-111b5ffdeb2e" />


### 4. `filters.json` (Privacy & Auto-Hide)
Sometimes you don't want Discord to broadcast what you are doing. This file acts as a smart privacy filter.
* **How it links to the UI:** Right-click the tray icon ➔ `Smart Filters / Auto-Disable` ➔ `Open filters.json`.
* **Keys & Values:**
    * `timeout_minutes`: (Number) If set to `10`, the script will automatically hide your Discord presence if you leave music playing (or paused) and walk away from your PC for 10 minutes. Set to `0` to disable.
    * `time_range`: (String) Provide a 24-hour window like `"02:00-08:00"`. The script will automatically hide your presence during these hours (perfect for sleeping!).
    * `blacklist`: (Array of strings) Add folder paths or specific words here (e.g., `["C:\\Private_Podcasts", "ASMR"]`). If the track name or file path contains these words, the script instantly hides your Discord status.

<img width="406" height="160" alt="imagen" src="https://github.com/user-attachments/assets/c7b4c0fa-c0f6-4755-b7e5-7ae99c6c9751" />  

### 5. `local_covers_db.json` (Internal Cache - Do Not Edit)
This file is automatically managed by the script. To prevent getting IP-banned by image hosting APIs (like ImgBB), the script temporarily uploads your local album art and saves the generated URL here. The next time you play the same song, it pulls the link instantly from this file instead of re-uploading it. 

### 6. `locales/` folder (Translations)
This folder contains language files (e.g., `es.json`, `en.json`). It dictates the text displayed within the application's GUI.
* **How it links to the UI:** The available `.json` files in this folder automatically populate the **"Language"** list at the bottom of the GUI.
* **Usage:** Want to translate the app to French or Portuguese? Simply copy `en.json`, rename it (e.g., `fr.json`), translate the text values inside the file, and restart the app. Your new language will appear in the GUI!

<img width="376" height="228" alt="imagen" src="https://github.com/user-attachments/assets/c40780cf-97f3-4c51-8e8c-d0bbd517f955" />

---

## 🛠️ Under the Hood (For Developers)

This project relies on several fantastic libraries:
* [`pyaimp`](https://epocdotfr.github.io/pyaimp/) - For reading local AIMP player states.
* [`pypresence`](https://qwertyquerty.github.io/pypresence/html/index.html) - For connecting and sending data to the Discord IPC.
* `pystray` & `Tkinter` - For handling the GUI and system tray logic.
* `requests` - For handling ImgBB and Last.fm API calls.

If you encounter any silent crashes, the script automatically logs critical errors. You can check the `error_log.txt` generated in the app's directory to diagnose the issue.
