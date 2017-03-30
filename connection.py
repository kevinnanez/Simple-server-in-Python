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
        self.request = ""
        self.partial_request = self.client_socket.recv()    

        while self.partial_request not "":
            self.request = self.request + self.partial_request
            self.partial_request = self.client_socket.recv()


            
        

        
        pass
