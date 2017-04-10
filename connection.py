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
        self.force_send = False
        self.client_is_here = True

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # FALTA: Manejar recepciones y envíos hasta desconexión
        socket_buffer = ""

        while not self.force_disconnection: 
            self.partial_request = self.client_socket.recv(4096)
            socket_buffer = socket_buffer + self.partial_request
            # Si no hay pedidos, esperarlos
            if not socket_buffer: # socket_buffer esta vacio -> el cliente 
                continue          # no ha hablado
                
            # EOL request?
            if socket_buffer.count(EOL) > 0:
                # Toma solo un comando, sin importar cuantos han sido enviados
                request_command, socket_buffer = socket_buffer.split(EOL, 1)
                request_size = len(request_command)
                self.request = Request(request_command, request_size)
                if not self.request.size: # check request no esta vacio 
                                          # (caso split(EOL)."\r\n" -> ["",""] )
                    if ('\n' in self.request.command) or \
                        ('\r' in self.request.command):
                        self.current_state = BAD_EOL
                        self.error_count+=1
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
                        if not self.force_send:            
                            self.respond()
                            if self.error_count: 
                                self.error()

                    else:
                        self.error()

                    self.force_send = False



   
    def error(self):
        if client_is_here:
            self.error_count = 0
            self.response = (("{0} {1}" % self.current_state), \
                            error_messages[self.current_state])
        else:
            return


    def quit(self):
        self.response = (("{0} {1}" % CODE_OK, error_messages[CODE_OK]) + EOL)
        self.force_disconnection = 1

    def respond(self, *args, **kwargs):
        """
         Que pasa si el cliente se desconecta sin enviar quit? Entonces send
         devuelve una excepción.
        """
        if not args:  
            try:
                self.client_socket.send(self.current_state + " " \
                                        + error_messages[self.current_state] \
                                        + EOL)
                self.client_socket.send(self.response)
            except IOError:
                self.error_count+=1
                self.force_disconnection = 1
                self.client_is_here = False
        else:
            get_slice_response = args[0]

            try:
                self.client_socket.send(get_slice_response)

            except IOError:
                self.error_count+=1
                self.force_disconnection = 1
                self.client_is_here = False



    def get_file_listing(self):
        try:
            files = os.listdir(self.directory) 
            for file in files:
                self.response = self.response + EOL
        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count+=1
            self.force_disconnection = 1

    def react(self):
        if self.wish in execute:
            execute[self.wish]()
        else:
            self.current_state = INVALID_COMMAND
            self.error_count+=1

    def get_metadata(self):
        """
        El unico metadato actual es el tamaño.  Solo pueden obtenerse los 
        metadatos de los archivos que serían devueltos por get file listing
        """
        try:
            files = os.listdir(self.directory) 
            if self.data in files:
                try:
                    self.response = os.path.getsize(self.data) + EOL
                except OSError:
                    self.current_state = INTERNAL_ERROR
                    self.error_count+=1
                    self.force_disconnection = 1
            else:
                self.current_state = FILE_NOT_FOUND
                self.error_count+=1

        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count+=1
            self.force_disconnection = 1
        

    def get_slice(self):

        if len(self.data.split(BLANK)) < 3:
            current_state = BAD_REQUEST
            force_disconnection = 1
            error_count+=1
            return

        filename, offset, size = self.data.split(BLANK)

        files = os.listdir(self.directory) 
        if filename not in files:
            self.current_state = FILE_NOT_FOUND
            self.error_count+=1
            return

        if (not offset.isdigit()) or (not size.isdigit()):
            current_state = INVALID_ARGUMENTS
            error_count+=1
            return 

        offset = int(offset)
        size = int(size)

        size_of_file = os.path.getsize(filename)

        if (offset >= size_of_file) or ((offset + size) > size_of_file):
            current_state = BAD_OFFSET
            self.error_count+=1
            return

        try:
            file = open(filename, "r")
            file.seek(offset)
            slices_size = 0

            self.respond(self.current_state + " " \
                        + error_messages[self.current_state] + EOL)

            while (size > slices_size) and (not self.force_disconnection):
                if 4096 > size - slices_size:
                    file = file.read(size - slices_size)
                    slices_size+=4096
                else:
                    file = file.read(size - slices_size)
                    slices_size+=(size - slices_size)

                self.respond(slices_size + " " + file + EOL)
            if not force_disconnection:
                self.respond("0" + " " + EOL)
                file.close()
                self.force_send = True
            else:
                return
            """for i in slices:
                self.response = len(slices[i]) + BLANK + slices[i] + EOL"""
        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count+=1
            self.force_disconnection = 1
            return

    # Seteamos un switch para elegir el comando
    execute = {
    'quit': quit, \
    'get_file_listing': get_file_listing, \
    'get_metadata': get_metadata, \
    'get_slice': get_slice \
    }

