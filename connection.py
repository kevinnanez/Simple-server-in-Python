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
            self.current_state = CODE_OK
        else:
            return

    def respond(self, *args, **kwargs):
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
        self.force_disconnection = 1

    def get_file_listing(self):
        try:
            files = os.listdir(self.directory) 
            for file in files:
                self.response = file + EOL
        except OSError:
            self.current_state = INTERNAL_ERROR
            self.error_count+=1
            self.force_disconnection = 1

    def react(self):
    
        if self.wish == "get_file_listing":
            if (len(self.data) > 0):
                self.current_state = BAD_REQUEST
                self.error_count+=1
                self.force_disconnection = 1
            else:   
                self.get_file_listing()
        elif self.wish == "get_metadata":
            if (len(self.data) < 1):
                self.current_state = BAD_REQUEST
                self.error_count+=1
                self.force_disconnection = 1
            elif (type(self.data[0]) == int):
                self.current_state = INVALID_ARGUMENTS
                self.error_count+=1
            else:
                self.get_metadata()
        elif self.wish == "get_slice":
            if (len(self.data) < 3):
                self.current_state = BAD_REQUEST
                self.error_count+=1
                self.force_disconnection = 1
            elif (type(self.data[0]) == int):
                self.current_state = INVALID_ARGUMENTS
                self.error_count+=1
            else:
                self.get_slice()
        elif self.wish == "quit":
            if (len(self.data) > 0):
                self.current_state = BAD_REQUEST
                self.error_count+=1
                self.force_disconnection = 1
            else:   
                self.quit()
        else:   
            self.current_state = INVALID_COMMAND
            self.error_count+=1
            

    def get_metadata(self):
        """
        El unico metadato actual es el tamaño.  Solo pueden obtenerse los 
        metadatos de los archivos que serían devueltos por get file listing
        """
        file = self.data[0]
        try:
            files = os.listdir(self.directory) 
            if file in files:
                try:
                    self.response = str(os.path.getsize(\
                                    os.path.join(self.directory, file))) + EOL
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

        if len(self.data) < 3:
            self.current_state = BAD_REQUEST
            self.error_count+=1
            force_disconnection = 1
        else:
            filename, offset, size = self.data

            files = os.listdir(self.directory) 
            if filename not in files:
                self.current_state = FILE_NOT_FOUND
                self.error_count+=1
            else:
                if (not offset.isdigit()) or (not size.isdigit()):
                    self.current_state = INVALID_ARGUMENTS
                    self.error_count+=1
                else:
                    offset = int(offset)
                    size = int(size)

                    size_of_file = os.path.getsize(\
                        os.path.join(self.directory, filename))

                    if (offset >= size_of_file) or \
                        ((offset + size) > size_of_file) or not size_of_file:
                        self.current_state = BAD_OFFSET
                        self.error_count+=1
                    else:
                        try:
                            file = open(os.path.join(self.directory, filename), \
                                                     "r")
                            file.seek(offset)
                            slices_size = 0

                            self.respond(str(self.current_state) + " " \
                                        + error_messages[self.current_state] \
                                         + EOL)

                            while (size > slices_size) and \
                                (not self.force_disconnection):
                                file_slice = file.read(size - slices_size)
                                
                                if 4096 > size_of_file - slices_size:
                                    slices_size+=(size - slices_size)
                                else:
                                    slices_size+=4096

                                size+=file_slice.count("\n")

                                file_slice_helper = file_slice.split("\n")
                                if len(file_slice_helper) > 1:
                                    file_slice_first = file_slice_helper[0]
                                    file_slice_helper = file_slice_helper[1:]
                                    file_slice = ""
                                    for sli in file_slice_helper:
                                        if len(sli) != 0:
                                            file_slice+=(EOL + str(len(sli)) + \
                                                        " " + sli)
                                    file_slice = str(len(file_slice_first)) \
                                                + " " + file_slice_first +  \
                                                file_slice
                                else:
                                    file_slice = str(slices_size) + " " + \
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
                self.quit()       # se ha ido
                
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

   

    

