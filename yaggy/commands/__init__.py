# -*- coding: utf-8 -*-

import re

from .common import no_ref_backref, no_backref, has_args
from .cmd_connect import (validate_connect, call_connect,
                          validate_disconnect, call_disconnect)
from .cmd_local import (call_lrun, call_lrun_exclamation,
                        call_lfailed, call_lsucceed)
from .cmd_misc import (validate_include, call_include,
                       call_tag, call_untag, call_echo)
from .cmd_remote import (call_run, call_run_exclamation,
                         call_failed, call_succeed)
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
    'RUN': {
        'validate': has_args,
        'validate_ref_backref': no_backref,
        'call': call_run,
    },
    'RUN!': {
        'validate': has_args,
        'validate_ref_backref': no_backref,
        'call': call_run_exclamation,
    },
    'FAILED?': {
        'validate': has_args,
        'call': call_failed,
    },
    'SUCCEED?': {
        'validate': has_args,
        'call': call_succeed,
    },
    'CHANGED?': {},
    'COPY': {},
    'FETCH': {},
    'TEMPLATE': {},
    'LRUN': {
        'validate': has_args,
        'validate_ref_backref': no_backref,
        'call': call_lrun,
    },
    'LRUN!': {
        'validate': has_args,
        'validate_ref_backref': no_backref,
        'call': call_run_exclamation,
    },
    'LFAILED?': {
        'validate': has_args,
        'call': call_lfailed,
    },
    'LSUCCEED?': {
        'validate': has_args,
        'call': call_lsucceed,
    },
    'LTEMPLATE': {},
    'LCHANGED?': {},
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

    cmd = COMMANDS[cmdname]

    return cmdname, cmd, ref, backref, args
