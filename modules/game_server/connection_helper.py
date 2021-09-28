import json


with open('server_settings.json') as f:
    GLB = json.load(f)


def process_msg(msg) -> tuple[str, list]:
    if msg.startswith(GLB['CMD_START']):
        # Message is a command

        command = msg.removeprefix(GLB['CMD_START'])
        args = command.split(GLB['ARG_SEPARATOR'])[1:]
        new_command = command.split(';')[0]
        # print(f'[COMMAND ACCEPTED] {new_command} {args}')

        for cmd in GLB['COMMANDS']:
            if cmd['CMD'] == new_command and cmd['ARGS'] == len(args):
                return new_command, args
                # if command == 'DISCONNECT':
                #     connected = False
                # break
    return '', []


def gen_cmd(cmd, args):
    msg = f'{GLB["CMD_START"]}{cmd}'
    for arg in args:
        msg += f'{GLB["ARG_SEPARATOR"]}{arg}'

    return msg + GLB["MESSAGE_END"]
