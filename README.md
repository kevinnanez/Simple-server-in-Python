#Proyecto de laboratorio N°1
##Redes y Sistemas Distribuidos- Grupo 05

###Introducción

Se implementó un servidor de archivos secuencial basado en protocolo HFPT. El programa cliente fue provisto por la cátedra. Servidor y cliente pueden correr en máquinas distintas sobre la misma red. Se utilizó lenguaje de programación Python siguiendo estilo de código PEP8.

###Server
El servidor crea un socket `s_socket` de familia AF_INET y tipo SOCK_STREAM. Gracias a la llamada de socketopt podemos utilizar sin problemas el puerto en sesiones consecutivas del servidor (fue necesaria por problemas especificos al armar el servidor luego de haberlo cerrado poco tiempo atras). `bind` asigna a `s_socket` el puerto port y dirección adr, luego especifica el número de conexiones de `s_socket` en 1. Asigna al atributo `self.directory` la direccion directory. port, addr y directory son constantes importadas de `constants.py` .
En la función `serve` se acepta la conexión con el  método accept() que crea un nuevo socket `conn_socket`, de igual familia y protocolo que `s_socket`, y devuelve la dirección del cliente en `client_ip`. En el atributo `self.connection` se crea la conexión creando un objeto Connection con conn_socket y directory. `self.connection.handle` ejecuta el loop principal del servidor.
La función `main`, que fue provista por la cátedra, parsea los argumentos y lanza el server.

###Conexión

####init
Se asignan `conn_socket` y directory a los atributos `client.socket` y `self.directory` respectivamente. Cream los atributos `current_state` para guardar el estado actual de la conexión y se asigna CODE_OK , `response` es la respuesta del servidor al cliente,`error_count` y `force_diconnection` se utilizaran en el manejo de excepciones, `force_send` y `client_is_here` son booleanos que se utilizaran para las respuestas forzadas y para el manejo de los errores. `wish` , `arguments` y `data` son  atributos que se utilizaran para el manejo e interpretación de comandos.

####handle
Es el loop principal del servidor. Decidimos guardar los comandos que envía el cliente en un buffer y dividirlos con `split` cuando aparezca el terminador `\r\n`, tuvimos que tener en cuenta que el terminador puede venir incompleto por lo que se implementaron las correspondientes excepciones. También decidimos guardar los argumentos de los comandos en una lista para facilitar su interpretación. Cierra la conexión cuando se ejecutan excepciones, errores fatales, desconexión del cliente o `quit`.

####error_notify
Solo notifica al servidor de errores de ejecución o comunicación con el cliente.

####respond
Maneja las respuestas al cliente, puede o no recibir argumentos además de los atributos.
Funcionamiento: Es aca donde se manejan las respuestas al cliente. Normalmente se la utiliza sin argumentos (solo atributos de la clase)    pero cuando es necesario es puede forzar una respuesta al cliente de la forma respond("Lorem ipsum"), para retornar datos al cliente de manera dinamica. Las respuestas exceptuando las forzadas van a notificar al cliente con el estado del funcionamiento, que en caso de ser 0, va enviar la respuesta que la clase tiene cargada en su atributo response.
    A veces, el cliente puede desconectarse sin anticiparnos con un quit. Esta función particularmente notificara a handle() de ese evento cuando
falle al intentar enviar datos al cliente, cancelando la conexión.

####quit
Cierra la sesión del cliente seteando `force_disconnection` en 1.

####react
Maneja los pedidos al servidor y determina el método a ejecutar. En `handle` guardamos el comando en `self.wish`, ahora lo interpretamos y verificamos que tanto el comando como sus argumentos sean válidos, si no lo son se ejecutan las excepciones correspondientes.

####get_file_listing
Con `os.listdir` accedemos al directorio y lo listamos, si hubo error ejecuta la excepción correspondiente.

####get_metada
Si el archivo solicitado por el cliente existe en el directorio devuelve su tamaño. En este método tuvimos que tener en cuenta si el archivo no existe o si hubo problema al listar los archivos.
Errores: Notificará de un error si
    a) no existe el archivo del pedido
    b) ocurre un error de tipo en el argumento (relatado en respond())
    d) el archivo no esta en el directorio
    e) ocurre un error al listar los archivos

####get_slice
Este método fue el más complicado. Primero nos fijamos si el archivo existe, si los argumentos son válidos y si la porción del archivo solicitada por el cliente es válida. Si lo son abrimos el archivo en modo lectura y nos paramos en el offset, si es necesario divide la porción en partes más chicas para poder enviarlo. La respuesta incluye el tamaño de la porción + la porción enviada, hasta terminar de enviar lo solicitado.


###Bibliografia

#####Librerías de Python:
https://docs.python.org/2/library/basehttpserver.html#module-BaseHTTPServer

#####Stackoverflow