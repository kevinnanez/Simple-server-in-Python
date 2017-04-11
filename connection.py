# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
import os
from constants import *


class Request(object):

    def __init__(self, command, size):
        self.command = command
        self.size = size


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.client_socket = socket
        self.directory = directory
        self.current_state = CODE_OK
        self.response = ""
        self.error_count = 0
        self.force_disconnection = 0
        self.force_send = False
        self.client_is_here = True
        self.wish = ""
        self.arguments = ""
        self.data = ""

    def error_notify(self):
        """
        Funcionamiento: Desde aqui se notifica al servidor de los errores
    generados por el funcionamiento o la interacción con el cliente. Solo se
    envian notificaciones de errores, cualquier respuesta cargada al sistema
    por la ejecución de algún metodo sera eliminada.
        También, se resetea el estado del funcionamiento actual a 0 (CODE_OK)
        """
        if self.client_is_here:
            self.error_count = 0
            self.response = ""
            self.respond()
            self.current_state = CODE_OK
        else:
            return

    def respond(self, *args, **kwargs):
        """
        Funcionamiento: Es aca donde se manejan las respuestas al cliente.
    Normalmente se la utiliza sin argumentos (solo atributos de la clase)
    pero cuando es necesario es puede forzar una respuesta al cliente de la
    forma respond("Lorem ipsum"), para retornar datos al cliente de manera
    dinamica.
        Las respuestas exceptuando las forzadas van a notificar al cliente con
    el estado del funcionamiento, que en caso de ser 0, va enviar la respuesta
    que la clase tiene cargada en su atributo response.
        A veces, el cliente puede desconectarse sin anticiparnos con un quit.
    Esta función particularmente notificara a handle() de ese evento cuando
    falle al intentar enviar datos al cliente, cancelando la conexión.

        """
        if not args:
            try:
                status = str(self.current_state) + " " \
                                        + error_messages[self.current_state] \
                                        + EOL
                while status:
                    sent = self.client_socket.send(status)
                    assert sent > 0
                    status = status[sent:]

                sent = 0

                while self.response:
                    sent = self.client_socket.send(self.response)
                    assert sent > 0
                    self.response = self.response[sent:]

                sent = 0

            except IOError:
                self.error_count += 1
                self.force_disconnection = 1
                self.client_is_here = False
        else:
            forced_response = args[0]

            try:
                while forced_response:
                    sent = self.client_socket.send(forced_response)
                    assert sent > 0
                    forced_response = forced_response[sent:]

            except IOError:
                self.error_count += 1
                self.force_disconnection = 1
                self.client_is_here = False

    def quit(self):
        """
        Funcionamiento: Esta función caduca la sesión del cliente
        """
        self.force_disconnection = 1

    def react(self):
        """
        Funcionamiento: Aqui es donde los pedidos se manejan y se utilizan para
    determinar que metodo lanzar a ejecución
        Errores: Notificará de un error si
    a) El pedido esta mal formado
    b) Los argumentos son invalidos
    c) El comando no es un metodo valido
        """
        if self.wish == "get_file_listing":
            self.get_file_listing()
        elif self.wish == "get_metadata":
            if (len(self.data) != 1):
                self.current_state = BAD_REQUEST
                self.error_count += 1
                self.force_disconnection = 1
            elif (type(self.data[0]) == int):
                self.current_state = INVALID_ARGUMENTS
                self.error_count += 1
            else:
                self.get_metadata()
        elif self.wish == "get_slice":
            if (len(self.data) != 3):
                self.current_state = BAD_REQUEST
                self.error_count += 1
                self.force_disconnection = 1
            elif (type(self.data[0]) == int):
                self.current_state = INVALID_ARGUMENTS
                self.error_count += 1
            else:
                self.get_slice()
        elif self.wish == "quit":
            self.quit()
        else:
            self.current_state = INVALID_COMMAND
            self.error_count += 1

    def get_file_listing(self):
        """
        Funcionamiento: Esta función responde al cliente con el listado
    de archivos en el directorio
        Errores: Notificará de un error si
    *) Ocurre un error al listar los archivos en el directorio
        """
        try:
            files = os.listdir(self.directory)
            for file in files:
                self.response = file + EOL
        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count += 1
            self.force_disconnection = 1

    def get_metadata(self):
        """
        Funcionamiento: Esta función responde al cliente con el tamaño de
    un archivo
        Errores: Notificará de un error si
    a) no existe el archivo del pedido
    b) ocurre un error de tipo en el argumento (relatado en respond())
    d) el archivo no esta en el directorio
    e) ocurre un error al listar los archivos
        """
        file = self.data[0]
        try:
            files = os.listdir(self.directory)
            if file in files:
                try:
                    self.response = str(os.path.getsize(
                                    os.path.join(self.directory, file))) + EOL
                except OSError:
                    self.current_state = INTERNAL_ERROR
                    self.error_count += 1
                    self.force_disconnection = 1

            else:
                self.current_state = FILE_NOT_FOUND
                self.error_count += 1

        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count += 1
            self.force_disconnection = 1

    def get_slice(self):
        """
        Funcionamiento: Esta función responde al cliente con una porcion del
    archivo filename de tamaño size, comenzando desde offset.
        Errores: Notificará de un error si
    a) no existe el archivo del pedido
    b) ocurre un error de tipo en el argumento (relatado en respond() y aqui)
    c) ocurre un error al abrir (open()) el archivo
    d) el archivo no esta en el directorio
    e) no se cumple offset≤filesize<offset+size

        Notar que esta función tiene acceso a la ejecución de otras funciones
    como respond(), algo que no tienen otros metodos (de uso exclusivo del
    cliente), debido a que aqui son necesarias respuestas dinamicas al cliente.
        """
	if not ("" in self.data):

            filename, offset, size = self.data

            files = os.listdir(self.directory)
            if filename not in files:
                self.current_state = FILE_NOT_FOUND
                self.error_count += 1
            else:
                if (not offset.isdigit()) or (not size.isdigit()):
                    self.current_state = INVALID_ARGUMENTS
                    self.error_count += 1
                else:
                    offset = int(offset)
                    size = int(size)

                    size_of_file = os.path.getsize(
                        os.path.join(self.directory, filename))

                    if (offset >= size_of_file) or \
                    ((offset + size) > size_of_file) or not size_of_file:
                        self.current_state = BAD_OFFSET
                        self.error_count += 1
                    else:
                        try:
                            file = open(os.path.join(self.directory, filename),
                                        "r")
                            file.seek(offset)

                            self.respond(str(self.current_state) + " " +
                                         error_messages[self.current_state] +
                                         EOL)

                            while size and \
                            (not self.force_disconnection):
                                if 4096 > size:
                                    file_slice = file.read(size)
                                    size = 0
                                else:
                                    file_slice = file.read(4096)
                                    size -= 4096

                                file_slice_helper = file_slice.split("\n")
                                breaks_slice = file_slice.count("\n")
                                size += breaks_slice

                                if len(file_slice_helper) > 1:
                                    file_slice_first = file_slice_helper[0]
                                    file_slice_helper = file_slice_helper[1:]
                                    file_slice = ""
                                    for sli in file_slice_helper:
                                        if len(sli) != 0:
                                            file_slice += (EOL + str(len(sli)) +
                                                           " " + sli)

                                    file_slice = str(len(file_slice_first)) + \
                                        " " + file_slice_first + file_slice

                                else:
                                    file_slice = str(len(file_slice)) + " " + \
                                                 file_slice

                                if not self.force_disconnection:
                                    self.respond(file_slice + EOL)

                            if not self.force_disconnection:
                                self.respond(str(CODE_OK) + " " + EOL)
                                self.force_send = True
                            else:
                                return

                        except OSError:
                            self.current_state = INTERNAL_ERROR
                            self.error_count += 1
                            self.force_disconnection = 1
                            return
        else:
            self.current_state = BAD_REQUEST
            self.error_count += 1
            self.force_disconnection = 1
	    return

    def handle(self):
        """
        Funcionamiento: Loop principal del servidor. Es iniciado al comenzar
    una sesión y caduca al aparecer errores fatales, ejecutar un quit, o
    desconexion apresurada del cliente.
        Es aqui donde se checkean todos los request que llegan al servidor y se
    dividen en comandos y argumentos, para luego comenzar su ejecución.
        Al cerrarse el ciclo se desconecta el cliente.
        """
        socket_buffer = ""
        while not self.force_disconnection and self.client_is_here:
            self.partial_request = self.client_socket.recv(4096)
            socket_buffer = socket_buffer + self.partial_request

            if not socket_buffer:
                self.quit()

            if socket_buffer.count(EOL) > 0:

                request_command, socket_buffer = socket_buffer.split(EOL, 1)
                request_size = len(request_command)
                if request_size > 0:

                    if ('\n' in request_command) or ('\r' in request_command):
                        self.current_state = BAD_EOL
                        self.error_count += 1
                        self.force_disconnection = 1

                    arguments = request_command.split(BLANK)

                    if len(arguments) > 1:
                        self.wish = arguments[0]
                        self.data = arguments[1:]
                    else:
                        self.wish = arguments[0]

                    self.react()

                    if not self.error_count:
                        if not self.force_send:
                            self.respond()
                            if self.error_count:
                                self.error_notify()

                    else:
                        self.error_notify()

                    self.force_send = False

        self.client_socket.close()
