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
    '''
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    '''

    def __init__(self, socket, directory):
        # Inicializamos atributos de conexión
        self.client_socket = socket
        self.directory = directory
        self.socket_buffer = ''
        # Diccionario de métodos
        self.dic = {
            'get_slice': (self.get_slice, 3),
            'get_metadata': (self.get_metadata, 1),
            'get_file_listing': (self.get_file_listing, 0),
            'quit': (self.quit, 0),
        }

    def handle(self):
        '''
        Atiende eventos de la conexión hasta que termina.
        '''
        self.client_online = True

        # Mientras la conexión este activa
        while self.client_online:
            # Lleno el buffer con datos del socket
            try:
                partial_request = self.client_socket.recv(4096)
            except:
                self.client_socket.close()
            self.socket_buffer += partial_request

            if len(partial_request) == 0:
                self.client_online = False
                continue
            # Si hay End of line
            if EOL in self.socket_buffer:
                # Creamos el request dividiendo por EOL o \r\n
                request_command, self.socket_buffer = self.socket_buffer.split(EOL, 1)
                request_size = len(request_command)

                # Si el tamaño del request es mayor a 0
                if request_size > 0 and not (('\n' in request_command) or ('\r\n' in request_command)):
                    # Separamos el request por espacios
                    s = request_command.split(' ')
                    command, arguments = s[0], s[1:]
                    # Vemos si el comando existe
                    if command not in self.dic:
                        self.client_socket.send(
                            '200 - ' + error_messages[INVALID_COMMAND] + EOL)
                    else:
                        # Vemos si los argumentos son válidos
                        if len(arguments) == self.dic[command][1]:
                            # Si lo son se procede a procesar los comandos
                            if not self.dic[command][1]:
                                self.dic[command][0]()
                            else:
                                self.dic[command][0](arguments)
                        else:
                            self.client_socket.send(
                                '201 - ' + error_messages[INVALID_ARGUMENTS] + EOL)
                else:
                    self.client_socket.send(
                        '100 - ' + error_messages[BAD_REQUEST] + EOL)
                    self.client_online = False
        self.client_socket.close()

    def get_file_listing(self):
        # Lista los archivos de directorio
        res = '0 OK\r\n' + '\r\n'.join(os.listdir(self.directory)) + '\r\n \r\n'
        self.client_socket.send(res)

    def get_metadata(self, arguments):
        path = self.directory
        filename = arguments[0]

        if os.path.isdir(path + '/' + filename) or ('/' in filename):
            res = '201 - ' + error_messages[INVALID_ARGUMENTS] + EOL
            self.client_socket.send(res)
        else:
            # Buscamos el archivo en el directorio y devolvemos su tamaño
            if filename in os.listdir(path):
                res = '0 OK \r\n' + \
                    str(os.path.getsize(path + '/' + filename)) + EOL
            else:
                # Si el nombre del archivo no es válido
                for character in filename:
                    if character not in VALID_CHARS and character != ' ':
                        res = '201 - ' + error_messages[INVALID_ARGUMENTS] + EOL
                        break
                    else:
                        res = '202 - ' + error_messages[FILE_NOT_FOUND] + EOL

            self.client_socket.send(res)

    def get_slice(self, arguments):
        # Nos fijamos si el archivo existe y si los argumentos son válidos
        try:
            filename, offset, size = arguments[0], int(
                arguments[1]), int(arguments[2])
            path = self.directory
            # Si se le pasa un directorio en vez de un archivo tirar error 201
            if os.path.isdir(path + '/' + filename) or ('/' in filename):
                res = '201 - ' + error_messages[INVALID_ARGUMENTS] + EOL
                self.client_socket.send(res)
            else:
                if offset < 0 or size < 0:
                    res = '201 - ' + error_messages[INVALID_ARGUMENTS] + EOL
                elif filename in os.listdir(path):
                    filesize = os.path.getsize(path + '/' + filename)
                    # Vemos si el offset + size es válido
                    if size + offset > filesize:
                        res = '203 - ' + error_messages[BAD_OFFSET] + EOL
                    else:
                        file = open(path + '/' + filename)
                        file.seek(offset)
                        res = '0 OK\r\n' + file.read(size) + EOL
                        self.client_socket.send(res)
                else:
                    res = '202 - ' + error_messages[FILE_NOT_FOUND] + EOL
                    self.client_socket.send(res)
        except ValueError:
            self.client_socket.send('201 - ' + error_messages[INVALID_ARGUMENTS] + EOL)

    def quit(self):
        # Cerramos la conexión
        res = '0 OK \r\n'
        self.client_online = False
        self.client_socket.send(res)
        self.client_socket.close()
