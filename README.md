# AIMP-Discord-Bridge-Presence

Este script de Python es solo y exclusivamente usable para los usuarios de AIMP. Solo está en el idioma español, pero si es necesario otro idioma lo agregaré a su tiempo (cabe recalcar que este es mi primer proyecto serio).

El script usa las librerías de [pyAIMP](https://epocdotfr.github.io/pyaimp/) y [pypresence](github.com/qwertyquerty/pypresence) principalmente, pero también para la mini UI se hace uso de [pystray](https://github.com/moses-palmer/pystray).

Se hace uso tanto de la API de [imgBB](https://7tlf4b88q.imgbb.com/) como la de [Last.fm](https://www.last.fm/user/Dryonex) para obtener las miniaturas de las canciones. La API de imgBB puede extraer/subir imágenes y la de Last.fm obtener datos de las canciones que estés reproduciendo.

<img width="450" height="198" alt="imagen" src="https://github.com/user-attachments/assets/de7f748a-0589-44f4-9968-c6c47804db00" />

La mini UI para configurar la actividad en Discord se encuentra en el área de notificaciones de Windows. <img width="48" height="21" alt="Sin título" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" />

En ella encontrará las siguientes configuraciones:

<img width="261" height="186" alt="imagen" src="https://github.com/user-attachments/assets/ac5e020c-fe19-44e9-b347-071c9e4c4813" />

**"Título de la Actividad"** se refiere a lo que aparecerá en tu usuario en la lista de usuarios:

<img width="441" height="72" alt="imagen" src="https://github.com/user-attachments/assets/dc0b3525-c287-43ee-b83b-638e4e653a10" />

**"Tipo de Actividad"** se refiere a lo que aparecerá en el título de la actividad estando dentro de la información del usuario (es muy parecido a "Título de la Actividad", nada más que le puse "tipo" por razones de claridad):

<img width="558" height="122" alt="imagen" src="https://github.com/user-attachments/assets/cb960bf2-d6b5-4072-a941-99cf465ed7ae" />

Estas dos listas tienen el mismo abanico de opciones. Puedes mostrar entre el álbum de la canción, artista de la canción, título de la canción o, si te quieres poner la camiseta de la app, está la opción de mostrar el nombre de la aplicación.

En **"Estado de Reproducción"** 💀 aparecen las siguientes opciones:

<img width="435" height="98" alt="imagen" src="https://github.com/user-attachments/assets/5dcb83f1-b8c4-44c7-ba50-25cd98a0d735" />

**"Mostrar Estado en Pausa"** se refiere a que la actividad no desaparece cuando la canción que se está reproduciendo en AIMP es pausada. Si la opción se encuentra desactivada, la actividad desaparecerá cuando pausees la canción.

**"Mostrar Línea de Tiempo"** <img width="48" height="21" alt="Sin título" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" /> se refiere a mostrar esa línea de tiempo que indica cuánto tiempo lleva reproduciéndose la canción y cuánto tiempo le queda.

<img width="282" height="124" alt="imagen" src="https://github.com/user-attachments/assets/d08d4aa0-93bd-45ee-9774-81799dcb2798" />

¿Ves eso? ¡Eso es lo que generaste! Eso es lo que ganas al tener tal opción tan servicial 💥.

Dentro de la lista **"Carátula del Álbum"** tenemos las siguientes opciones:

<img width="477" height="122" alt="imagen" src="https://github.com/user-attachments/assets/911c20e7-871d-4f8e-ba2d-dbb65ffcbdaf" />

Esas opciones eligen a qué servicio darle prioridad para obtener la portada. Si te es más rápido uno en vez del otro, le activas esa opción. Si le das a la opción de "No Mostrar", simplemente aparecerá un fondo gris en su lugar.

Dentro de la lista **"Ícono de Estado"** se encuentran las siguientes opciones:

<img width="431" height="79" alt="imagen" src="https://github.com/user-attachments/assets/3af8ef3f-078c-4b10-b104-f064b7ffa048" />

Es como va a salir en el mini logo al frente derecho inferior de la imagen de la actividad.

Si activas **"Dinámico (Play/Pausa)"** saldrá así:

<img width="270" height="107" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" /><img width="265" height="107" alt="imagen" src="https://github.com/user-attachments/assets/87152bb1-9ad5-4ef5-88da-5f8dad192b34" />



Si le das a **"Solo Logo"**, este mostrará ese logo, ah... ese logo tan característico de AIMP:

<img width="264" height="107" alt="imagen" src="https://github.com/user-attachments/assets/fcdf1077-f505-4170-8b0d-db5741ac3ece" />

Y si activas la opción **"No Mostrar"**, desactiva directamente los iconos que aparecen ahí:

<img width="268" height="100" alt="imagen" src="https://github.com/user-attachments/assets/1d9de9b6-e276-4881-9a28-5d79f5132476" />

Volviendo al inicio de la UI, en la lista **"Tema"** se encuentra deshabilitada por el momento (en ese apartado se va a configurar cómo se verán los iconos en la actividad y, si es posible, también en la UI).

En el mismo inicio se encuentra la opción de **"Iniciar con Windows"**, este registra una clave de registro en el registro de Windows para que se pueda activar o desactivar en las aplicaciones de inicio de Windows.
