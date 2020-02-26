# -*- coding: utf-8 -*-

import re

from .cmd_connect import call_connect, call_disconnect
from .cmd_local import (call_lrun, call_lrun_exclamation,
                        call_lfailed, call_lsucceed)
from .cmd_misc import call_include, call_tag, call_untag, call_echo
from .cmd_remote import (call_run, call_run_exclamation,
                         call_failed, call_succeed)
from .cmd_vars import call_vars, call_secrets

from .validators import (no_ref, no_backref, no_args, has_args,
                         validate_vars, validate_secrets,
                         validate_include, validate_tag, validate_untag)


COMMANDS = {
    'VARS': {
        'validators': [
            no_ref,
            no_backref,
            has_args,
            validate_vars,
        ],
        'call': call_vars,
    },
    'SECRETS': {
        'validators': [
            no_ref,
            no_backref,
            has_args,
            validate_secrets,
        ],
        'call': call_secrets,
    },
    'CONNECT': {
        'validators': [
            no_ref,
            no_backref,
            no_args,
        ],
        'call': call_connect,
    },
    'RECONNECT': {
        'validators': [
        ],
    },
    'DISCONNECT': {
        'validators': [
            no_ref,
            no_backref,
            no_args,
        ],
        'call': call_disconnect,
    },
    'INCLUDE': {
        'validators': [
            no_ref,
            no_backref,
            validate_include,
        ],
        'call': call_include,
    },
    'TAG': {
        'validators': [
            no_ref,
            no_backref,
            validate_tag,
        ],
        'call': call_tag,
    },
    'UNTAG': {
        'validators': [
            no_ref,
            no_backref,
            validate_untag,
        ],
        'call': call_untag,
    },
    'ECHO': {
        'validators': [
            no_ref,
            no_backref,
        ],
        'call': call_echo,
    },
    'RUN': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_run,
    },
    'RUN!': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_run_exclamation,
    },
    'FAILED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_failed,
    },
    'SUCCEED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_succeed,
    },
    'CHANGED?': {
        'validators': [
            no_ref,
            has_args,
        ],
    },
    'COPY': {
        'validators': [
            no_backref,
            has_args,
        ],
    },
    'FETCH': {
        'validators': [
            no_ref,
            no_backref,
            has_args,
        ],
    },
    'TEMPLATE': {
        'validators': [
            no_backref,
            has_args,
        ],
    },
    'LRUN': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_lrun,
    },
    'LRUN!': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_lrun_exclamation,
    },
    'LFAILED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_lfailed,
    },
    'LSUCCEED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_lsucceed,
    },
    'LTEMPLATE': {
        'validators': [
            no_backref,
            has_args,
        ],
    },
    'LCHANGED?': {
        'validators': [
            no_backref,
            has_args,
        ],
    },
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
