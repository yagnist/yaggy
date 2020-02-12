# -*- coding: utf-8 -*-

import re

from .cmd_common import no_ref_backref
from .cmd_vars import validate_vars, run_vars, validate_secrets


COMMANDS = {
    'VARS': {
        'validate': validate_vars,
        'validate_ref_backref': no_ref_backref,
        'run': run_vars,
    },
    'SECRETS': {
        'validate': validate_secrets,
        'validate_ref_backref': no_ref_backref,
    },
    'CONNECT': {},
    'RECONNECT': {},
    'DISCONNECT': {},
    'INCLUDE': {},
    'TAG': {},
    'UNTAG': {},
    'ECHO': {},
    'RUN!': {},
    'RUN': {},
    'SU': {},
    'LOGOUT': {},
    'FAILED?': {},
    'SUCCEED?': {},
    'CHANGED?': {},
    'COPY': {},
    'FETCH': {},
    'TEMPLATE': {},
    'LRUN!': {},
    'LRUN': {},
    'LFAILED?': {},
    'LSUCCEED?': {},
    'LTEMPLATE': {},
    'LCHANGED?': {},
}


COMMAND_RE = re.compile(
    r'((?P<ref>@[a-zA-Z0-9_-]+)\s+)?'
    r'(?P<command>' + r'|'.join(re.escape(x) for x in COMMANDS.keys()) + r')'
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

    cmd = COMMANDS[cmdname]

    return cmdname, cmd, ref, backref, args
