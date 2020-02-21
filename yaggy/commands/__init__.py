# -*- coding: utf-8 -*-

import re

from .common import no_ref_backref
from .cmd_connect import (validate_connect, call_connect,
                          validate_disconnect, call_disconnect)
from .cmd_misc import (validate_include, call_include,
                       call_tag, call_untag, call_echo)
from .cmd_vars import validate_vars, call_vars, validate_secrets, call_secrets


COMMANDS = {
    'VARS': {
        'validate': validate_vars,
        'validate_ref_backref': no_ref_backref,
        'call': call_vars,
    },
    'SECRETS': {
        'validate': validate_secrets,
        'validate_ref_backref': no_ref_backref,
        'call': call_secrets,
    },
    'CONNECT': {
        'validate': validate_connect,
        'validate_ref_backref': no_ref_backref,
        'call': call_connect,
    },
    'RECONNECT': {},
    'DISCONNECT': {
        'validate': validate_disconnect,
        'validate_ref_backref': no_ref_backref,
        'call': call_disconnect,
    },
    'INCLUDE': {
        'validate': validate_include,
        'validate_ref_backref': no_ref_backref,
        'call': call_include,
    },
    'TAG': {
        'validate_ref_backref': no_ref_backref,
        'call': call_tag,
    },
    'UNTAG': {
        'validate_ref_backref': no_ref_backref,
        'call': call_untag,
    },
    'ECHO': {
        'validate_ref_backref': no_ref_backref,
        'call': call_echo,
    },
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
