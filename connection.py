# encoding: utf-8
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from os import listdir
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
            self.commands = self.buffer.split("\r\n")
            if self.commands is "": # nada en buffer
                continue 
            else if len(self.commands) is 1: # pedido incompleto
                continue
            else if len(self.commands) is not 1: # pedido completo
                if self.commands[-1] is not "":
                    self.commands[:1]
                for req in self.commands: # estos pedidos si estan estan completos (\r\n),
                                         # de lo contrario estan malformados. (solo pedidos
                                         # completos)
                    if req is "":
                        continue
                    else if req is "quit":
                        return
                    else if req is "get_file_listing":
                        # reply with file listing
                    else :
                        arguments = req.split(" ")
                        if len(arguments) is 2 :
                            if arguments[0] is "get_metadata":
                                # try to get metadata of arguments[1]
                            else :
                                # error bad request

                        else if len(arguments) is 3:
                            if arguments[0] is "get_slice":
                                #try to get slice of arguments[1] from arguments[2] to arguments[3]
                            else:
                                # error bad request

                    else:
                        # error bad request



            self.partial_request = self.client_socket.recv()
                
    def quit(self):
        print ("0 {0}", % error_messages[CODE_OK])
        return

    def give_file_listing(self):
        files_listed = os.listdir(self.directory)
        for file in files_listed :
            print ("{0} {1}", % (file, EOL))





