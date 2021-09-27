from connection_helper import gen_cmd, process_msg
import threading
import socket
import json

with open('server_settings.json') as f:
    GLB = json.load(f)

id = 0
connections = {}


def init_connection(conn, addr):
    global id
    id += 1
    connections[id] = (conn, addr)
    print(f'[NEW CONNECTION] {addr} connected, with id {id}.')

    msg = gen_cmd('INIT', [id])
    msg_len = len(msg)
    send_length = str(msg_len).encode(GLB['FORMAT'])
    send_length += b' ' * (GLB['MESSAGE_HEADER_LENGTH'] - len(send_length))

    conn.send(send_length)
    conn.send(msg.encode(GLB['FORMAT']))


def handle_client(conn, addr):
    init_connection(conn, addr)

    connected = True
    while connected:
        msg_len = conn.recv(HEADER).decode(FORMAT)
        # TODO: Setup timeout
        if msg_len:
            msg_len = int(msg_len)
            msg: str = conn.recv(msg_len).decode(FORMAT)
            # print(f'[{addr}] {msg}')

            cmd, args = process_msg(msg)
            if cmd == 'DISCONNECT':
                connected = False
                break
            elif cmd == 'SAY':
                print(f'{addr}: {args[0]}')

    conn.close()
    print(f'[CONNECTION CLOSED] Client {addr} with id {id} disconnected.')


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print(f"[STARTING] Server is listening at {ADDR}.")
    server.listen()
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()
        print(f'[ACTIVE CONNECTIONS]: {threading.active_count() - 1}')


if __name__ == "__main__":
    HEADER = GLB['MESSAGE_HEADER_LENGTH']
    PORT = GLB['SERVER_PORT']
    IP = GLB["SERVER_IP"]
    ADDR = (IP, PORT)
    FORMAT = GLB['FORMAT']

    main()
