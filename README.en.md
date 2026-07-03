# AIMP-Discord-Bridge-Presence

This Python script is solely and exclusively usable for AIMP users. It is currently only available in Spanish, but if another language is needed I will add it in time (it should be noted that this is my first serious project).

The script uses the libraries of [pyAIMP](https://epocdotfr.github.io/pyaimp/) and [pypresence](github.com/qwertyquerty/pypresence) mainly, but also for the mini UI it uses [pystray](https://github.com/moses-palmer/pystray).

Both the [imgBB](https://7tlf4b88q.imgbb.com/) API and the [Last.fm](https://www.last.fm/user/Dryonex) API are used to obtain song thumbnails. The imgBB API can extract/upload images and Last.fm API obtains data from the songs you are playing.

<img width="450" height="198" alt="imagen" src="https://github.com/user-attachments/assets/de7f748a-0589-44f4-9968-c6c47804db00" />

The mini UI to configure the Discord activity is found in the Windows notifications area. <img width="48" height="21" alt="Sin título" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" />

In it you will find the following configurations:

<img width="261" height="186" alt="imagen" src="https://github.com/user-attachments/assets/ac5e020c-fe19-44e9-b347-071c9e4c4813" />

**"Activity Title"** refers to what will appear on your user in the user list:

<img width="441" height="72" alt="imagen" src="https://github.com/user-attachments/assets/dc0b3525-c287-43ee-b83b-638e4e653a10" />

**"Activity Type"** refers to what will appear in the title of the activity within the user information (it is very similar to "Activity Title", just that I called it "type" for clarity reasons):

<img width="558" height="122" alt="imagen" src="https://github.com/user-attachments/assets/cb960bf2-d6b5-4072-a941-99cf465ed7ae" />

These two lists have the same range of options. You can display the song's album, song's artist, song's title or, if you want to put on the app's shirt, there's the option to display the application name.

In **"Playback Status"** 💀 the following options appear:

<img width="435" height="98" alt="imagen" src="https://github.com/user-attachments/assets/5dcb83f1-b8c4-44c7-ba50-25cd98a0d735" />

**"Show Paused Status"** refers to the fact that the activity does not disappear when the song being played in AIMP is paused. If the option is disabled, the activity will disappear when you pause the song.

**"Show Timeline"** <img width="48" height="21" alt="Sin título" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" /> refers to displaying that timeline that indicates how long the song has been playing and how much time is left.

<img width="282" height="124" alt="imagen" src="https://github.com/user-attachments/assets/d08d4aa0-93bd-45ee-9774-81799dcb2798" />

See that?! That's what you generated! That's what you get for having such a helpful option 💥.

Within the **"Album Cover"** list we have the following options:

<img width="477" height="122" alt="imagen" src="https://github.com/user-attachments/assets/911c20e7-871d-4f8e-ba2d-dbb65ffcbdaf" />

Those options choose which service to prioritize to obtain the cover. If one is faster for you instead of the other, you activate that option. If you choose the "Do Not Show" option, a gray background will simply appear instead.

Within the **"Status Icon"** list are the following options:

<img width="431" height="79" alt="imagen" src="https://github.com/user-attachments/assets/3af8ef3f-078c-4b10-b104-f064b7ffa048" />

It's how it will appear in the mini logo at the front lower right of the activity image.

If you activate **"Dynamic (Play/Pause)"** it will look like this:

<img width="270" height="107" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" /><img width="271" height="114" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" />

If you choose **"Logo Only"**, it will display that logo, ah... that characteristic AIMP logo:

<img width="264" height="107" alt="imagen" src="https://github.com/user-attachments/assets/fcdf1077-f505-4170-8b0d-db5741ac3ece" />

And if you activate the **"Do Not Show"** option, it directly disables the icons that appear there:

<img width="268" height="100" alt="imagen" src="https://github.com/user-attachments/assets/1d9de9b6-e276-4881-9a28-5d79f5132476" />

Going back to the beginning of the UI, in the **"Theme"** list it is currently disabled (in that section you will be able to configure how the icons will look in the activity and, if possible, also in the UI).

In the same beginning there is the **"Start with Windows"** option, this registers a registry key in the Windows registry so that it can be activated or deactivated in Windows startup applications.
