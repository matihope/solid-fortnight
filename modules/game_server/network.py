from modules.game_server.connection_helper import process_msg
import socket
import json
import threading
import time
import pygame
import enum

with open('server_settings.json') as f:
    GLB = json.load(f)


class NetworkEvents(enum.IntEnum):
    EVENT_HANGUP = pygame.USEREVENT + 1
    EVENT_MESSAGE = pygame.USEREVENT + 2
    EVENT_ACTION = pygame.USEREVENT + 3


class SocketConnection(threading.Thread):
    def __init__(self, server_address, server_port):
        super().__init__()
        self.server_address = server_address
        self.server_port = server_port
        self.server_socket = None
        self.data_buffer = ''
        self.deamon = True  # exit with parent
        self.done = False
        self.connected = False

    def send_message(self, message):
        if self.connected:
            self.server_socket.send(message.encode(GLB['FORMAT']))

    def stop(self):
        self.connected = False
        self.done = True

    def __bool__(self):
        return self.connected and not self.done

    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = self.server_address, self.server_port
        for i in range(3):
            try:
                self.server_socket.connect(address)
                self.server_socket.setblocking(False)
                print(f'[CONNECTION ESTABILISHED] Connected to: {address}')
                self.connected = True
                return
            except Exception as e:
                print(f'[CONNECTION FAILED] Failed to connect to: {address}')
                if i < 2:
                    print('[CONNECTION RETRY] Retrying...')
                    time.sleep(5)
        print('[CONNECTION RETRY] Quting...')
        self.done = True

    def run(self):
        """ Connects to Server, then Loops until the server hangs-up """
        self.connect()

        # Now we're connected, start reading commands
        data = ''
        while not self.done:
            try:
                new_data = self.server_socket.recv(1024).decode(GLB['FORMAT']).rstrip()

            except BlockingIOError:
                pass
            except ConnectionResetError:
                # Socket has closed
                new_event = pygame.event.Event(NetworkEvents.EVENT_HANGUP,
                                               {"address": self.server_address})
                pygame.event.post(new_event)
                self.server_socket.close()
                self.done = True
            else:
                if GLB['MESSAGE_END'] in new_data:
                    # divide new message by message separator
                    divided_data = new_data.split(GLB['MESSAGE_END'])

                    # finish the first message
                    queried_commands = [data + divided_data.pop(0).rstrip()]

                    # process the rest of new_data
                    while True:
                        d = divided_data.pop(0).rstrip()
                        if len(divided_data):
                            queried_commands.append(d)
                        else:
                            # clear the data buffer and
                            # set data to last piece of new_data
                            data = d
                            break

                    for finished_command in queried_commands:

                        cmd, args = process_msg(finished_command, as_client=True)
                        if cmd == 'DISCONNECT':
                            pygame.event.post(
                                pygame.event.Event(NetworkEvents.EVENT_HANGUP,
                                                   {"address": self.server_address})
                            )
                            self.server_socket.close()
                            self.done = True
                        else:
                            # post event to pygame main loop
                            pygame.event.post(
                                pygame.event.Event(NetworkEvents.EVENT_ACTION,
                                                   {"action": cmd, "args": args})
                            )
