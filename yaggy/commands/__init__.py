# -*- coding: utf-8 -*-

import re

from .cmd_connect import CMD_CONNECT, CMD_DISCONNECT, CMD_RECONNECT
from .cmd_local import (CMD_LRUN, CMD_LRUN_EXCLAMATION,
                        CMD_LFAILED, CMD_LSUCCEED, CMD_FETCH)
from .cmd_misc import CMD_INCLUDE, CMD_TAG, CMD_UNTAG, CMD_ECHO
from .cmd_remote import (CMD_RUN, CMD_RUN_EXCLAMATION,
                         CMD_FAILED, CMD_SUCCEED, CMD_SYNC, CMD_CHANGED)
from .cmd_vars import CMD_VARS, CMD_SECRETS


COMMANDS = {
    'VARS': CMD_VARS,
    'SECRETS': CMD_SECRETS,
    'CONNECT': CMD_CONNECT,
    'RECONNECT': CMD_RECONNECT,
    'DISCONNECT': CMD_DISCONNECT,
    'INCLUDE': CMD_INCLUDE,
    'TAG': CMD_TAG,
    'UNTAG': CMD_UNTAG,
    'ECHO': CMD_ECHO,
    'RUN': CMD_RUN,
    'RUN!': CMD_RUN_EXCLAMATION,
    'FAILED?': CMD_FAILED,
    'SUCCEED?': CMD_SUCCEED,
    'LRUN': CMD_LRUN,
    'LRUN!': CMD_LRUN_EXCLAMATION,
    'LFAILED?': CMD_LFAILED,
    'LSUCCEED?': CMD_LSUCCEED,
    'SYNC': CMD_SYNC,
    'CHANGED?': CMD_CHANGED,
    'FETCH': CMD_FETCH,
}


# NB. RUN! must be specified before RUN in regexp, LRUN! before LRUN
allowed_commands = sorted(COMMANDS.keys(), reverse=True)

COMMAND_RE = re.compile(
    r'((?P<ref>@[a-zA-Z0-9_-]+)\s+)?'
    r'(?P<command>' + r'|'.join(re.escape(x) for x in allowed_commands) + r')'
    r'((\s+(?P<backref>@[a-zA-Z0-9._-]+))?(\s*(?P<args>.*)))$',
    re.UNICODE
)


def command_parts(line):
    parts = COMMAND_RE.match(line)

    if not parts:
        return None, None, None, None, None

    ref = parts.group('ref')
    cmdname = parts.group('command')
    backref = parts.group('backref')
    args = parts.group('args')
    if args:
        args = args.strip()

    cmd = COMMANDS[cmdname]

    return cmdname, cmd, ref, backref, args
