# -*- coding: utf-8 -*-

import shlex

from ..exceptions import YaggySyntaxError
from ..ssh import connect, disconnect
from ..utils import pick

from .common import run


def validate_connect(**kwargs):
    args = kwargs['args']

    if args:
        raise YaggySyntaxError('CONNECT command does not expect any arguments')


def call_connect(ctx, **kwargs):

    connect(ctx)

    ssh_run = pick(ctx, 'ssh.cmd_run')
    conn_timeout = pick(ctx, 'ssh.conn_timeout')

    logger_remote = pick(ctx, 'logger.remote')

    commands = ['uname -a', 'hostname -f', 'date', 'whoami']

    for cmd in commands:
        run(shlex.split(ssh_run) + shlex.split(cmd),
            capture_output=True,
            encoding='utf-8',
            timeout=conn_timeout,
            logger=logger_remote,
            cmd=cmd)


def validate_disconnect(**kwargs):
    args = kwargs['args']

    if args:
        raise YaggySyntaxError(
            'DISCONNECT command does not expect any arguments')


def call_disconnect(ctx, **kwargs):

    disconnect(ctx)
