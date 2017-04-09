# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from os import listdir
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
        # FALTA: Inicializar atributos de Connection
        self.client_socket = socket
        self.directory = directory
        self.current_state = CODE_OK # Es necesario tener una constancia
        self.response = ""              # del estado (funcional o erroneo)
        self.error_count = 0
        self.force_disconnection = 0

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # FALTA: Manejar recepciones y envíos hasta desconexión
        socket_buffer = ""

        while not force_disconnection: 
            self.partial_request = self.client_socket.recv()
            socket_buffer = socket_buffer + self.partial_request
            # Si no hay pedidos, esperarlos
            if not socket_buffer: # socket_buffer esta vacio -> el cliente 
                continue          # no ha hablado
                
            # EOL request?
            if socket_buffer.count(EOL) > 0:
                # Toma solo un comando, sin importar cuantos han sido enviados
                request_command, socket_buffer = socket_buffer.split(EOL, 1)
                request_size = len(request)
                self.request = Request(request_command, request_size)
                if not self.request.size: # check request no esta vacio 
                                          # (caso split(EOL)."\r\n" -> ["",""] )
                    if ('\n' in self.request.command) or \
                        ('\r' in self.request.command):
                        self.current_state = BAD_EOL
                        self.error_count++
                        self.force_disconnection = 1

                    self.arguments = self.request.command.split(BLANK) 
                    """ 
                    Si habia multiples argumentos, self.arguments los guarda en 
                    un arreglo, si habia uno, devuelve un arreglo con ese unico
                    argumento
                    """ 
                    self.wish = self.arguments[:1]
                    self.data = self.arguments[1:]
                    
                    self.react()

            # Despues de todo, habla con el cliente
            if not self.error_count:            
                self.respond()
                if self.error_count: 
                    self.error()
            else:
                self.error()





   
    def error(self):
        self.error_count = 0
        self.response = ("{0} {1}", % self.current_state, \
                        error_messages[self.current_state])


    def quit(self):
        self.response = ("{0} {1}", % CODE_OK, error_messages[CODE_OK] + EOL)
        self.force_disconnection = 1

    def respond(self):
        """
         Que pasa si el cliente se desconecta sin enviar quit? Entonces send
         devuelve una excepción.
        """

        try:
            self.client_socket.send(self.current_state + " " \
                                    + error_messages[self.current_state] + EOL)
            self.client_socket.send(self.response)
        except IOError:
            self.error_count++
            self.force_disconnection = 1


    def get_file_listing(self):
        try:
            files = os.listdir(self.directory) 
            for file in files:
                self.response = self.response + EOL
        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count++
            self.force_disconnection = 1

    def react(self):
        if self.wish in execute:
            execute[self.wish]()
        else:
            self.current_state = INVALID_COMMAND
            self.error_count++

    def get_metadata(self):
        """
        El unico metadato actual es el tamaño.  Solo pueden obtenerse los 
        metadatos de los archivos que serían devueltos por get file listing
        """
        try:
            files = os.listdir(self.directory) 
            if self.data in files
                try:
                    self.response = os.path.getsize(self.data) + EOL
                except OSError:
                    self.current_state = FILE_NOT_FOUND
                    self.error_count++
            else
                self.current_state = FILE_NOT_FOUND
                self.error_count++

        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count++
            self.force_disconnection = 1
        

    def get_slice(self):


        filename, offset, size = self.data.split(BLANK)
        try:
            file = open(self.data[:2], "rb")
            slices = split(file, self.data[2:]) + ""
            for i in slices:
                self.response = len(slices[i]) + BLANK + slices[i] + EOL
            file.close()
        except OSError:
            self.current_state = FILE_NOT_FOUND
            self.error_count++

        



        









