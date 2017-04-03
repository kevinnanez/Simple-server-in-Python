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
        # Buffering de los request

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
                    
                    self.respond()


    def respond(self):
        """
        A esta función solo llegan los pedidos separados por opción y 
        argumentos para esa opción
        - Se utiliza un equivalente a switch (de C) para elegir una funcion a 
        ejecutar
        """
        if self.wish in execute:
            execute[self.wish]()      


    def quit(self):
        print ("0 {0}", % error_messages[CODE_OK])
        return

    def give_file_listing(self):
        files_listed = os.listdir(self.directory)
        for file in files_listed :
            print ("{0} {1}", % (file, EOL))





