import json


with open('server_settings.json') as f:
    GLB = json.load(f)


def process_msg(msg, as_client=False) -> tuple[str, list]:
    if msg.startswith(GLB['CMD_START']):
        # Message is a command

        command = msg.removeprefix(GLB['CMD_START'])
        args = command.split(GLB['ARG_SEPARATOR'])[1:]
        new_command = command.split(';')[0]
        # print(f'[COMMAND ACCEPTED] {new_command} {args}')

        for cmd in GLB['COMMANDS']:
            # in server settings, the ARGS count is viewed as recieving server
            # so when client RECIEVES, it has ARGS + 1 args
            if cmd['CMD'] == new_command:
                if new_command == 'TOCLIENT' or \
                   cmd['ARGS'] == len(args) or \
                   (cmd['ARGS'] + 1 == len(args) and as_client):

                    return new_command, args

    return '', []


class WrongCommandName(Exception):
    """Raised when the CMD_START or MESSAGE_END character is in the gen_cmd's cmd argument"""
    pass


class WrongArgument(Exception):
    """Raised when the CMD_START or MESSAGE_END character is in the gen_cmd's args argument"""
    pass


def gen_cmd(cmd, args):
    # CHECK COMMAND NAME
    if GLB["CMD_START"] in cmd or GLB["MESSAGE_END"] in cmd:
        raise WrongCommandName

    msg = f'{GLB["CMD_START"]}{cmd}'
    for arg in args:

        # CHECK ARGUMENT
        if type(arg) == str:
            if GLB["CMD_START"] in arg or GLB["MESSAGE_END"] in arg:
                raise WrongArgument

        msg += f'{GLB["ARG_SEPARATOR"]}{arg}'

    return msg + GLB["MESSAGE_END"]
