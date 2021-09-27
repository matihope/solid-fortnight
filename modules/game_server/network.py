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

    def stop(self):
        self.done = True

    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = self.server_address, self.server_port
        for i in range(3):
            try:
                self.server_socket.connect(address)
                print(f'[CONNECTION ESTABILISHED] Connected to: {address}')
                return True
            except Exception as e:
                print(f'[CONNECTION FAILED] Failed to connect to: {address}')
                if i < 2:
                    print('[CONNECTION RETRY] Retrying...')
                    time.sleep(5)
        print('[CONNECTION RETRY] Quting...')
        return False

    def run(self):
        """ Connects to Server, then Loops until the server hangs-up """
        if not self.connect():
            return

        # Now we're connected, start reading commands
        while not self.done:
            incoming = self.server_socket.recv(GLB["MESSAGE_HEADER_LENGTH"])

            if len(incoming) == 0:
                # Socket has closed
                new_event = pygame.event.Event(NetworkEvents.EVENT_HANGUP,
                                               {"address": self.server_address})
                pygame.event.post(new_event)
                self.server_socket.close()
                self.done = True

            else:
                # Data has arrived
                try:
                    msg_len = int(incoming.decode(GLB['FORMAT']))
                    msg = self.server_socket.recv(msg_len).decode(GLB['FORMAT'])

                    cmd, args = process_msg(msg)
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

                except Exception as e:
                    print(e)


def send_message(connection: SocketConnection, msg):
    try:
        msg_len = len(msg)
        send_length = str(msg_len).encode(GLB['FORMAT'])
        send_length += b' ' * (GLB['MESSAGE_HEADER_LENGTH'] - len(send_length))

        connection.server_socket.send(send_length)
        connection.server_socket.send(msg.encode(GLB['FORMAT']))
        return True

    except Exception as e:
        return False
