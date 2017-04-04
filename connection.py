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

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # FALTA: Manejar recepciones y envíos hasta desconexión
        socket_buffer = ""

        while True:
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
                    self.arguments = self.request.command.split(BLANK) 
                    """ 
                    Si habia multiples argumentos, self.arguments los guarda en 
                    un arreglo, si habia uno, devuelve un arreglo con ese unico
                    argumento
                    """ 
                    self.wish = self.arguments[:1]
                    self.data = self.arguments[1:]
                    
                    if self.wish in execute:
                        execute[self.wish]()
                    else:
                        self.current_state = INVALID_ARGUMENTS
                        self.error_count++

            # Despues de todo, habla con el cliente
            if not error_count:            
                self.respond()
            else:
                self.error()




   
    def error(self):
        # A definir manejo de errores.


    def quit(self):
        self.response = ("{0} {1}", % CODE_OK, error_messages[CODE_OK])

    def respond():
        self.client_socket.send(self.response)

    def get_file_listing(self):

        files = os.listdir(self.directory)
        for file in files:
            response = response + EOL
        








