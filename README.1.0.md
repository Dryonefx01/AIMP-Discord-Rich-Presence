# AIMP-Discord-Bridge-Presence
Este script de Python es sola y exclusivamente usable para los usuarios de AIMP, solo esta en el idioma español pero si es necesario otro idioma lo agregare a su tiempo(cabe recalcar que este es mi primer proyecto serio).
  
El Script usa las librerias de [pyAIMP](https://epocdotfr.github.io/pyaimp/) y [pypresence](github.com/qwertyquerty/pypresence) principalmente pero tambien para la mini UI se hace uso de [pystray](https://github.com/moses-palmer/pystray).

Se hace uso tanto de la api de [imgBB](https://7tlf4b88q.imgbb.com/) como la de [Last.fm](https://www.last.fm/user/Dryonex) para obtener las Miniaturas de las canciones, la api de imgBB puede extraer/subir imagenes y la de Last.fm obtener datos de las canciones que estes reproduciendo.
<img width="450" height="198" alt="imagen" src="https://github.com/user-attachments/assets/de7f748a-0589-44f4-9968-c6c47804db00" /> 


La mini UI para configurar la actividad en discord se encuentra en el area de notificaciones de windows<img width="48" height="21" alt="Sin títulso" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" />
las siguientes configuraciones:  
<img width="261" height="186" alt="imagen" src="https://github.com/user-attachments/assets/ac5e020c-fe19-44e9-b347-071c9e4c4813" />

"Título de la Actividad" se refiere a lo que aparecera en tu user en la lista de usuarios:  
<img width="441" height="72" alt="imagen" src="https://github.com/user-attachments/assets/dc0b3525-c287-43ee-b83b-638e4e653a10" />  
"Tipo de Actividad" se refiere a lo que aparecera en el titulo de la actividad estando dentro de la info del usuario(es muy parecido a "Titulo de la Actividad" nada mas que le puse "tipo" por razones de claridad):
<img width="558" height="122" alt="imagen" src="https://github.com/user-attachments/assets/cb960bf2-d6b5-4072-a941-99cf465ed7ae" />  
estas 2 listas tienen el mismo abanico de opciones puedes mostrar entre el album de la cancion, artista de la cancion, titulo de la cancion o si te quieres poner la camiseta de la app esta la opcion de mostrar el nombre de la aplicacion.


En "Estado de Reproducción"💀 aparecen las siguientes opciones:  
<img width="435" height="98" alt="imagen" src="https://github.com/user-attachments/assets/5dcb83f1-b8c4-44c7-ba50-25cd98a0d735" />  
"Mostrar Estado en Pausa" se refiere a que la actividad no desaparece cuando la cancion que se esta reprocuciendo en AIMP es pausada y si la opcion se encuentra desactivada, la actividad desaparecera cuando pausees la cancion.
"Mostrar Línea de Tiempo"<img width="48" height="21" alt="Sin títulso" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" /> se refiere a mostrar esa linea de tiempo que indica cuanto tiempo lleva reproduciendose la cancion y cuanto tiempo le queda.
<img width="282" height="124" alt="imagen" src="https://github.com/user-attachments/assets/d08d4aa0-93bd-45ee-9774-81799dcb2798" />   
ves eso?! eso es lo que generaste!, eso es lo que ganas al tener tal opcion tan servicial💥.  

Dentro de la lista "Carátula del Álbum" tenemos las siguientes opciones:  
<img width="477" height="122" alt="imagen" src="https://github.com/user-attachments/assets/911c20e7-871d-4f8e-ba2d-dbb65ffcbdaf" />   
Esas opciones eligen a que servicio darle prioridad para obtener la portada, si te es mas rapido uno en vez del otro le activas esa opcion y si le das a la opcion de "No Mostrar" simplemente aparecera un fondo gris en su lugar.

Dentro de la lista "ícono de Estado" se encuentran las siguientes opciones:  
<img width="431" height="79" alt="imagen" src="https://github.com/user-attachments/assets/3af8ef3f-078c-4b10-b104-f064b7ffa048" />
Es como va a salir en el mini logo al frente derecho inferior de la imagen de la actividad.   
Si activas "Dinámico (Play/Pausa)" saldra asi:  
<img width="270" height="107" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" /><img width="271" height="114" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" />
Si le das a "Solo Logo" este mostrara ese logo ahh.. ese logo tan caracteristico de AIMP:  
<img width="264" height="107" alt="imagen" src="https://github.com/user-attachments/assets/fcdf1077-f505-4170-8b0d-db5741ac3ece" />  
Y si activas la opcion "No Mostrar" desactiva directamente los iconos que aparecen ahi:  
<img width="268" height="100" alt="imagen" src="https://github.com/user-attachments/assets/1d9de9b6-e276-4881-9a28-5d79f5132476" />  

Volviendo al inicio de la UI en la lista "Tema" se encuentra deshabilitada por el momento(en ese apartado se va a configurar en como se veran los iconos en la actividad y si es posible tambien en la UI).

En el mismo inicio se encuentra la opcion de "Iniciar con Windows" este registra una clave de registro en el registro de windows para que se pueda activar o desactivar en las aplicaciones de inicio de windows.
