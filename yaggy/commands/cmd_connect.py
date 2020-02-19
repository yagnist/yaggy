# -*- coding: utf-8 -*-

import os
import shlex
import subprocess

from ..exceptions import YaggySyntaxError, YaggyConnectionError
from ..utils import pick


def validate_connect(**kwargs):
    args = kwargs['args']

    if args:
        raise YaggySyntaxError('CONNECT command does not expect any arguments')


def call_connect(ctx, **kwargs):

    ssh_cmd = pick(ctx, 'ssh.cmd_connect')
    ssh_run = pick(ctx, 'ssh.cmd_run')
    control_socket = pick(ctx, 'ssh.control_socket')
    ssh_timeout = pick(ctx, 'ssh.cmd_timeout')

    logger_local = pick(ctx, 'logger.local')
    logger_remote = pick(ctx, 'logger.remote')

    logger_local.debug(
        '# ssh control socket name: "%s"', os.path.basename(control_socket))

    ssh_proc = subprocess.Popen(shlex.split(ssh_cmd),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                encoding='utf-8')
    try:
        proc_stdout, proc_stderr = ssh_proc.communicate(timeout=ssh_timeout)
    except subprocess.TimeoutExpired:
        proc_stdout = proc_stderr = None

    if ssh_proc.poll() is not None:
        # NB. means no connection to server
        if proc_stdout:
            logger_remote.info(proc_stdout.strip())
        if proc_stderr:
            logger_remote.error(proc_stderr.strip())

        raise YaggyConnectionError('CONNECT failed')

    logger_local.debug('[CONNECT] state: connected')

    ctx['ssh']['proc'] = ssh_proc

    commands = ['uname -a', 'hostname -f', 'date', 'whoami']

    for cmd in commands:
        res = subprocess.run(shlex.split(ssh_run) + shlex.split(cmd),
                             capture_output=True,
                             encoding='utf-8',
                             timeout=ssh_timeout)
        if res.returncode == 0:
            logger_remote.info('---')
            logger_remote.info('$ %s', cmd)
            logger_remote.info('%s', res.stdout.strip())
        else:
            logger_remote.error('---')
            logger_remote.error('$ %s', cmd)
            logger_remote.error('%s', res.stderr.strip())
