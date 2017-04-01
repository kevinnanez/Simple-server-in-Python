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
        self.bufferin = ""
        self.bufferout = ""
        self.connected = True
        pass

    def send(self):
        #Envía lo que queda en buffer al cliente
        while self.bufferout:
            sent = self.client_socket.send(self.bufferout)
            self.bufferout = self.bufferout[sent:]

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # FALTA: Manejar recepciones y envíos hasta desconexión
        while self.connected:
            partial_request = self.client_socket.recv(BUFFSIZE)
            self.bufferin += partial_request
                if len(partial_request) == 0:
                    self.connected = False
                    continue
            if EOL in self.bufferin
                request, self.bufferin = self.bufferin.split("\r\n",1)
                program = self.valid_request(request)
                if program == CODE_OK
                    arg = request.split(' ')
                    command = arg[0]
                    result = ''
                    if command == "get_file_listing":
                        program, result = self.get_file_listing()
                    elif command == "get_metadata"
                        program, result = self.get_metadata(arg[1])
                    elif command == "get_slice"
                        program, result = self.get_slice(arg[1], arg[2], arg[3])
                    else:
                        self.connected = False

                    self.bufferout += result
                else: error
            self.send()
        # Buffering de los request
        self.buffer = ""
        self.partial_request = self.client_socket.recv()

        while self.partial_request not "":
            self.buffer = self.buffer + self.partial_request
            self.commands = self.request.split("\r\n")
                if self.commands is ""  # nada en buffer
                    continue
                else if len(self.commands) is 1  # pedido incompleto
                    continue
                else if len(self.commands) is not 1  # pedido completo
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

        def request_valid(self, request):
            req = request.split(' ')
            comm = req[0]
            if '\n' in request:
                return BAD_EOL
            for char in list(request):
                if char not in VALID_CHARS and char != ' ':
                    return INVALID_ARGUMENTS
            return CODE_OK

        def get_file_listing(self):
            result = ''
            try
                files_listed = os.listdir(self.directory)
            except OSError:
                return INTERNAL_ERROR, result
            for file in files_listed
                result += file + EOL
            result += EOL
            return CODE_OK, result
