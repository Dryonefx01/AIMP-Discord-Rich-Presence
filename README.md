# AIMP-Discord-Bridge-Presence
Este script de Python es sola y exclusivamente usable para los usuarios de AIMP, solo esta en el idioma español pero si es necesario otro idioma lo agregare a su tiempo(cabe recalcar que este es mi primer codigo publicado y esta hecho a base del uso de una IA como la de Gemini de google y por el momento es funcional) si tienes alguna duda no dudes en comunicarte/abrir un commit/MD en discord/instagram/Youtube/lo que sea.  
  
El Script usa las librerias de [pyAIMP](https://epocdotfr.github.io/pyaimp/) y [pypresence](github.com/qwertyquerty/pypresence) principalmente pero tambien para la mini UI se hace uso de [pystray](https://github.com/moses-palmer/pystray)

Se hace uso tanto de la api de [imgBB](https://7tlf4b88q.imgbb.com/) como la de [Last.fm](https://www.last.fm/user/Dryonex) para obtener las Miniaturas de las canciones, la api de imgBB puede extraer/postear las miniaturas sacadas directamente de los archivos usando su base de datos de por medio para poder usarla en la actividad de discord sin tener que abrir ningun puerto extraño en la PC o usar un servidor externo o interno, y la de Last.fm puede extraer las miniaturas pero solamente las que estan posteadas en su pagina web es como un salvavidas interno pero medio inservible porque no deje programado ningun escaneo desde el mismo nombre del archivo de la cancion o de los metadatos si es que este mismo no contiene una portada(btw).  
<img width="450" height="198" alt="imagen" src="https://github.com/user-attachments/assets/de7f748a-0589-44f4-9968-c6c47804db00" /> 


La mini UI para configurar la actividad en discord se encuentra en el area de notificaciones de windows<img width="48" height="21" alt="Sin títulso" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" /> este mismo aparece con este icono <img width="22" height="21" alt="imagen" src="https://github.com/user-attachments/assets/03f830e9-43f0-4341-b5a3-b7f3355df7d7" /> y contiene
las siguientes configuraciones:  
<img width="261" height="186" alt="imagen" src="https://github.com/user-attachments/assets/ac5e020c-fe19-44e9-b347-071c9e4c4813" />

"Título de la Actividad" se refiere a lo que aparecera en tu user en la lista de usuarios:  
<img width="441" height="72" alt="imagen" src="https://github.com/user-attachments/assets/dc0b3525-c287-43ee-b83b-638e4e653a10" />  
"Tipo de Actividad" se refiere a lo que aparecera en el titulo de la actividad estando dentro de la info del usuario(es muy parecido a "Titulo de la Actividad" nada mas que le puse "tipo" por razones misteriosas☄):  
<img width="558" height="122" alt="imagen" src="https://github.com/user-attachments/assets/cb960bf2-d6b5-4072-a941-99cf465ed7ae" />  
estas 2 listas tienen el mismo abanico de opciones puedes mostrar entre el album de la cancion, artista de la cancion, titulo de la cancion o si te quieres poner la camiseta de la app esta la opcion de simplemente AIMP💎(Proximamente actualizare eso para poder poner un mensaje custom tambien permitiendo el cambio directamente del id de discord pero por el momento escribiendo esto descubri lo de imgBB asi que ya se me acabaron los tokens... digo las ganas👀).  


En "Estado de Reproducción"💀 aparecen las siguientes opciones:  
<img width="435" height="98" alt="imagen" src="https://github.com/user-attachments/assets/5dcb83f1-b8c4-44c7-ba50-25cd98a0d735" />  
"Mostrar Estado en Pausa" se refiere a que la actividad no desaparece cuando la cancion que se esta reprocuciendo en AIMP es pausada y si la opcion se encuentra desactivada, la actividad desaparecera hasta que vuelvas a reproducir.  
"Mostrar Línea de Tiempo"<img width="48" height="21" alt="Sin títulso" src="https://github.com/user-attachments/assets/a5e0d3b8-0233-4876-8598-edbe4fd10455" /> se refiere a mostrar esa linea de tiempo tan caracteristica de este script, si la opcion es desactivada la actividad quedara esteticamente arruinada y se vera mas vacio que un vaso de agua en africa😭  
<img width="282" height="124" alt="imagen" src="https://github.com/user-attachments/assets/d08d4aa0-93bd-45ee-9774-81799dcb2798" />   
ves eso?! eso es lo que generaste!, eso es lo que ganas al tener tal opcion tan servicial💥.  

Dentro de la lista "Carátula del Álbum" tenemos las siguientes opciones:  
<img width="477" height="122" alt="imagen" src="https://github.com/user-attachments/assets/911c20e7-871d-4f8e-ba2d-dbb65ffcbdaf" />   
Esas opciones eligen a que servicio darle prioridad para obtener la portada, si te es mas rapido uno en vez del otro le activas esa opcion y si le das a la opcion de "No Mostrar" simplemente aparecera el logo de AIMP deidad(esta parte se me hace complicada de explicar no se porque xd).  

Dentro de la lista "ícono de Estado" se encuentran las siguientes opciones:  
<img width="431" height="79" alt="imagen" src="https://github.com/user-attachments/assets/3af8ef3f-078c-4b10-b104-f064b7ffa048" />
Es como va a salir en el mini logo al frente derecho inferior de la imagen de la actividad.   
Si activas "Dinámico (Play/Pausa)" saldra asi:  
<img width="270" height="107" alt="imagen" src="https://github.com/user-attachments/assets/c42cc25a-0c45-47f5-b0cd-2749727a1c6e" /><img width="271" height="114" alt="imagen" src="https://github.com/user-attachments/assets/7923c646-8979-4872-b91c-1975c704979b" />  
Si le das a "Solo Logo" este mostrara ese logo ahh.. ese logo tan caracteristico de AIMP:  
<img width="264" height="107" alt="imagen" src="https://github.com/user-attachments/assets/fcdf1077-f505-4170-8b0d-db5741ac3ece" />  
Y si activas la opcion "No Mostrar" desactiva directamente los iconos que aparecen ahi:  
<img width="268" height="100" alt="imagen" src="https://github.com/user-attachments/assets/1d9de9b6-e276-4881-9a28-5d79f5132476" />  

Volviendo al inicio de la UI en la lista "Tema" se encuentra deshabilitada por el momento(en ese apartado se va a configurar en como se veran los iconos en la actividad y si es posible tambien en la ui pero por el momento queda asi hasta nuevo aviso) tambien se tiene pensado en agregar una lista de idiomas tanto para la interfaz como en la misma actividad de discord pero creo que por mantener el script lo mas ligero posible se tendra que reescribir todo el bendito script en distintos idiomas porque para rematar no se de que lado de la cama se levanto Gemini pero escribio gran parte de todo el frigolero codigo al español osea eso que man pero en fin.   

En el mismo inicio se encuentra la opcion de "Iniciar con Windows" este registra una clave de registro en el registro de windows para que se pueda activar o desactivar en las aplicaciones de inicio en el administrador de tareas y ya con esto tambien se crea otra ruta en el registro para guardar los cambios de las configuraciones del script(rutas que ya ni recuerdo cuales eran pero estan escritas en el script si quieres checkear).  
