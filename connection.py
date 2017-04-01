# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *


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
        pass

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # FALTA: Manejar recepciones y envíos hasta desconexión

        # Buffering de los request
        self.buffer = ""
        self.partial_request = self.client_socket.recv()    

        while self.partial_request not "":
            self.buffer = self.buffer + self.partial_request
            self.commands = self.request.split("\r\n")
            if self.commands is "" # nada en buffer
                continue 
            else if len(self.commands) is 1 # pedido incompleto
                continue
            else if len(self.commands) is not 1 # pedido completo
                # Fatales
                for req in self.commands
                    if req is ""
                        continue
                    else if req is "quit"
                        # quit
                    else if req is "get_file_listing"
                        # reply with file listing
                    else 
                        arguments = req.split(" ")
                        if len(arguments) is 2 
                            if (arguments[0] is "get_metadata")
                                # try to get metadata of arguments[1]
                            else 
                                # error bar request
                            

                            
                        else if len(arguments)  

# get_slice\r\n -> ["get_slice", ""] 
            self.partial_request = self.client_socket.recv()
                
            


            
        

        
        pass
