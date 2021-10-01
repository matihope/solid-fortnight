from connection_helper import gen_cmd, process_msg
import threading
import socket
import json

with open('server_settings.json') as f:
    GLB = json.load(f)

global_id = 0
connections: dict = {}


def init_connection(conn, addr):
    global global_id
    global_id += 1
    connections[global_id] = (conn, addr)
    print(f'[NEW CONNECTION] {addr} connected, with id {global_id}.')

    msg = gen_cmd('INIT', [global_id])
    conn.send(msg.encode(GLB['FORMAT']))

    return global_id


def handle_client(conn, addr):
    client_id = init_connection(conn, addr)

    connected = True
    data = ''
    while connected:
        try:
            new_data: str = conn.recv(1024).decode(FORMAT).rstrip()
        except BlockingIOError:
            pass
        except ConnectionResetError:
            connected = False
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

                # execute the commands
                for finished_command in queried_commands:
                    cmd, args = process_msg(finished_command)

                    # direct command to other player
                    if cmd == 'TOCLIENT':
                        target_id = int(args.pop(0))
                        target_command = args.pop(0)
                        target_conn, _ = connections[target_id]
                        target_conn.send(gen_cmd(target_command,
                                                 [client_id] + args).encode(GLB['FORMAT']))

                    else:
                        # GLOBAL COMMANDS
                        # propagate the command to other clients
                        for other_conn, _ in connections.values():
                            if other_conn == conn:
                                continue
                            other_conn.send(gen_cmd(cmd, [client_id] + args).encode(GLB['FORMAT']))

                        if cmd == 'DISCONNECT':
                            connected = False
                            break

                        elif cmd == 'SAY':
                            print(f'{addr}: {args[0]}')

    connections.pop(client_id)
    conn.close()
    print(f'[CONNECTION CLOSED] Client {addr} with id {client_id} disconnected.')


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print(f"[STARTING] Server is listening at {ADDR}.")
    server.listen()
    while True:
        conn, addr = server.accept()
        conn.setblocking(False)
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()
        print(f'[ACTIVE CONNECTIONS]: {threading.active_count() - 1}')


if __name__ == "__main__":
    PORT = GLB['SERVER_PORT']
    IP = GLB["SERVER_IP"]
    ADDR = (IP, PORT)
    FORMAT = GLB['FORMAT']

    main()
