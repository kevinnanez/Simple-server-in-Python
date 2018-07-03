# Redes y Sistemas Distribuidos
#Laboratorio Nº1: Aplicación Servidor

## Server
El servidor, crea y atiende el socket en la dirección y puerto especificados donde se reciben nuevas conexiones de clientes. Se acepta una conexión a la vez y se espera a que concluya antes de seguir. La conexión comienza a ejecutarse en el handle de `connection.py`

## Connection

### Handle
En handle creamos un buffer para que se vaya llenando con datos que recibe el socket, esto es, las instrucciones del cliente.Con un loop nos aseguramos que el cliente sigue ahi con client_online, si el buffer esta vacío el servidor se cierra.
Creamos una clase request para procesar lo que entra al buffer. Separamos cada instrucción por EOL que aparece y guardamos su tamaño. Separamos el request por espacios, la primera celda va ser la función y las demas (si las hay) son argumentos.
La decisión de crear un diccionario para definir el comportamiento segun el comando fue la más  importante, porque nos ahorro bastantes lineas de código y funciones anidadas.
Si el comando no existe tira error, si existe se fija la cantidad de argumentos y aca es donde entra a los métodos:
+ `files`: devuelve lista de archivos del directorio.
+ `get_file_listing`: hace un join con EOL de los archivos del directorio y los muestra al cliente.
+ `get_metadata`: si el archivo existe calcula el tamaño del directorio. Con `os.path.getsize` lo pasamos a string para imprimir en pantalla.
+ `get_slice`: si el archivo existe calcula su tamaño, para que no haya problemas con el offset se fija que la suma del offset y el size de lo que queremos leer no sea mayor al tamaño del archivo. Si no hay problemas. abre el archivo, se para en un determinado byte con `seek` y lee la cantidad de bytes (size) con `read`.
+ `quit`: cierra la conexión.

## ¿Qué estrategias existen para poder implementar este mismo servidor pero con capacidad de atender múltiples clientes simultáneamente?
Para que el servidor pueda atender a mas de un cliente habría que editar el init de la clase `server`, especificamente `listen(x)` donde x es el numero máximo de clientes simultáneos, después habría que guardar en una lista los clientes activos y aplicar alguna politica para ver que cliente atiendo primero y durante cuanto tiempo para que los atienda a todos equitativamente.
## ¿Qué dificultades nos encontramos?
Al principio nos costó generar un buffer y llenarlo con el stream entrante, ademas que tuvimos muchas dificultades procesando los saltos de lineas. Por ultimo tambien tuvimos problemas al manejar los directorios dentro de del DEFAULT_DIR usado
