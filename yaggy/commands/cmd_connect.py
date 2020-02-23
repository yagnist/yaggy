# -*- coding: utf-8 -*-

from yaggy.ssh import connect, disconnect
from yaggy.utils import pick

from .common import run


def call_connect(ctx, **kwargs):

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


def call_disconnect(ctx, **kwargs):

    disconnect(ctx)
