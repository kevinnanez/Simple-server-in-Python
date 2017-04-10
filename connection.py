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
        # FALTA: Inicializar atributos de Connection
        self.client_socket = socket
        self.directory = directory
        self.current_state = CODE_OK # Es necesario tener una constancia
        self.response = ""              # del estado (funcional o erroneo)
        self.error_count = 0
        self.force_disconnection = 0
        self.force_send = False
        self.client_is_here = True
        self.wish = ""
        self.arguments = ""
        self.data = ""


    def error_notify(self):
        if self.client_is_here:
            self.error_count = 0
            self.response = ""
            self.respond()
        else:
            return

    def respond(self, *args, **kwargs):
        print ("respond!")
        """
         Que pasa si el cliente se desconecta sin enviar quit? Entonces send
         devuelve una excepción.
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
                self.error_count+=1
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
                self.error_count+=1
                self.force_disconnection = 1
                self.client_is_here = False


    def quit(self):
        print ("quit!")
        self.force_disconnection = 1

    def get_file_listing(self):
        print ("get_file_listing!")
        try:
            files = os.listdir(self.directory) 
            for file in files:
                self.response = file + EOL
        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count+=1
            self.force_disconnection = 1

    def react(self):
        print ("react!")
    
        if self.wish == "get_file_listing":
            self.get_file_listing()
        elif self.wish == "get_metadata":
            self.get_metadata()
        elif self.wish == "get_slice":
            self.get_slice()
        elif self.wish == "quit":
            self.quit()
        else:   
            self.current_state = INVALID_COMMAND
            self.error_count+=1
            

    def get_metadata(self):
        print ("get_metadata!")
        """
        El unico metadato actual es el tamaño.  Solo pueden obtenerse los 
        metadatos de los archivos que serían devueltos por get file listing
        """
        file = self.data[0]
        try:
            files = os.listdir(self.directory) 
            if file in files:
                try:
                    self.response = str(os.path.getsize(os.path.join(self.directory, file))) + EOL
                except OSError:
                    self.current_state = INTERNAL_ERROR
                    self.error_count+=1
                    self.force_disconnection = 1
                    print (self.current_state)
            else:
                self.current_state = FILE_NOT_FOUND
                self.error_count+=1
                print (self.current_state)  

        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count+=1
            self.force_disconnection = 1
            print (self.current_state)
        

    def get_slice(self):
        print ("get_slice!")

        if len(self.data) < 3:
            current_state = BAD_REQUEST
            force_disconnection = 1
            self.error_count+=1
            return

        filename, offset, size = self.data

        files = os.listdir(self.directory) 
        if filename not in files:
            self.current_state = FILE_NOT_FOUND
            self.error_count+=1
            return

        if (not offset.isdigit()) or (not size.isdigit()):
            current_state = INVALID_ARGUMENTS
            self.error_count+=1
            return 

        offset = int(offset)
        size = int(size)

        size_of_file = os.path.getsize(os.path.join(self.directory, filename))

        if (offset >= size_of_file) or ((offset + size) > size_of_file):
            current_state = BAD_OFFSET
            self.error_count+=1
            return

        try:
            file = open(os.path.join(self.directory, filename), "r")
            file.seek(offset)
            slices_size = 0

            self.respond(str(self.current_state) + " " \
                        + error_messages[self.current_state] + EOL)

            while (size > slices_size) and (not self.force_disconnection):
                if 4096 > size_of_file - slices_size:
                    file_slice = file.read(size - slices_size)
                    slices_size+=(size - slices_size)
                else:
                    file_slice = file.read(size - slices_size)
                    slices_size+=4096

                self.respond(str(slices_size) + " " + file_slice + EOL)
            if not self.force_disconnection:
                self.respond("0" + " " + EOL)
                
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
                if request_size > 0: # check request no esta vacio 
                                          # (caso split(EOL)."\r\n" -> ["",""] )
                    if ('\n' in request_command) or \
                        ('\r' in request_command):
                        self.current_state = BAD_EOL
                        self.error_count+=1
                        self.force_disconnection = 1

                    arguments = request_command.split(BLANK)

                    if len(arguments) > 1:
                        self.wish = arguments[0]
                        self.data = arguments[1:]
                    else:
                        self.wish = arguments[0]
                    
                    self.react()

                    # Despues de todo, habla con el cliente
                    if not self.error_count:
                        if not self.force_send:            
                            self.respond()
                            if self.error_count: 
                                self.error_notify()

                    else:
                        self.error_notify()

                    self.force_send = False

        self.client_socket.close()  

   

    

