# -*- coding: utf-8 -*-

from yaggy.ssh import connect, disconnect, reconnect
from yaggy.utils import pick

from .common import run

from . import validators, vstate


def call_connect(ctx, **parsed):

    connect(ctx)

    ssh_run = pick(ctx, 'ssh.cmd_run')
    conn_timeout = pick(ctx, 'ssh.conn_timeout')

    logger_remote = pick(ctx, 'logger.remote')

    commands = ['uname -a', 'hostname -f', 'date', 'whoami']

    for cmd in commands:
        run(execute=ssh_run,
            cmd=cmd,
            logger=logger_remote,
            raise_on_error=False,
            capture_output=True,
            encoding='utf-8',
            timeout=conn_timeout)


def call_disconnect(ctx, **parsed):

    disconnect(ctx)


def call_reconnect(ctx, **parsed):

    reconnect(ctx, **parsed)


CMD_CONNECT = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.no_args,
    ],
    'call': call_connect,
    'vstate': vstate.vstate_connect,
    'is_internal': False,
}
CMD_DISCONNECT = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.no_args,
    ],
    'call': call_disconnect,
    'vstate': vstate.vstate_disconnect,
    'is_internal': False,
}
CMD_RECONNECT = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_reconnect,
    ],
    'call': call_reconnect,
    'vstate': vstate.vstate_reconnect,
    'is_internal': False,
}
