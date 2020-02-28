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
from .vstate import (vstate_connect, vstate_disconnect,
                     vstate_run, vstate_conditional_run,
                     vstate_lrun, vstate_conditional_lrun)


COMMANDS = {
    'VARS': {
        'validators': [
            no_ref,
            no_backref,
            has_args,
            validate_vars,
        ],
        'call': call_vars,
        'category': 'internal',
    },
    'SECRETS': {
        'validators': [
            no_ref,
            no_backref,
            has_args,
            validate_secrets,
        ],
        'call': call_secrets,
        'category': 'internal',
    },
    'CONNECT': {
        'validators': [
            no_ref,
            no_backref,
            no_args,
        ],
        'call': call_connect,
        'vstate': vstate_connect,
        'category': 'conn',
    },
    'RECONNECT': {
        'validators': [
        ],
        'category': 'conn',
    },
    'DISCONNECT': {
        'validators': [
            no_ref,
            no_backref,
            no_args,
        ],
        'call': call_disconnect,
        'vstate': vstate_disconnect,
        'category': 'conn',
    },
    'INCLUDE': {
        'validators': [
            no_ref,
            no_backref,
            validate_include,
        ],
        'call': call_include,
        'category': 'internal',
    },
    'TAG': {
        'validators': [
            no_ref,
            no_backref,
            validate_tag,
        ],
        'call': call_tag,
        'category': 'internal',
    },
    'UNTAG': {
        'validators': [
            no_ref,
            no_backref,
            validate_untag,
        ],
        'call': call_untag,
        'category': 'internal',
    },
    'ECHO': {
        'validators': [
            no_ref,
            no_backref,
        ],
        'call': call_echo,
        'category': 'internal',
    },
    'RUN': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_run,
        'vstate': vstate_run,
        'category': 'remote',
    },
    'RUN!': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_run_exclamation,
        'vstate': vstate_run,
        'category': 'remote',
    },
    'FAILED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_failed,
        'vstate': vstate_conditional_run,
        'category': 'remote',
    },
    'SUCCEED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_succeed,
        'vstate': vstate_conditional_run,
        'category': 'remote',
    },
    'CHANGED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'category': 'remote',
    },
    'COPY': {
        'validators': [
            no_backref,
            has_args,
        ],
        'category': 'local',
    },
    'FETCH': {
        'validators': [
            no_ref,
            no_backref,
            has_args,
        ],
        'category': 'local',
    },
    'TEMPLATE': {
        'validators': [
            no_backref,
            has_args,
        ],
        'category': 'local',
    },
    'LRUN': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_lrun,
        'vstate': vstate_lrun,
        'category': 'local',
    },
    'LRUN!': {
        'validators': [
            no_backref,
            has_args,
        ],
        'call': call_lrun_exclamation,
        'vstate': vstate_lrun,
        'category': 'local',
    },
    'LFAILED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_lfailed,
        'vstate': vstate_conditional_lrun,
        'category': 'local',
    },
    'LSUCCEED?': {
        'validators': [
            no_ref,
            has_args,
        ],
        'call': call_lsucceed,
        'vstate': vstate_conditional_lrun,
        'category': 'local',
    },
    'LTEMPLATE': {
        'validators': [
            no_backref,
            has_args,
        ],
        'category': 'local',
    },
    'LCHANGED?': {
        'validators': [
            no_backref,
            has_args,
        ],
        'category': 'local',
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
