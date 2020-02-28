# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
import uuid

from .exceptions import YaggyConnectionError
from .utils import mutate, pick


def setup_ssh(runtimedir, **kwargs):

    logger = kwargs['logger']

    hostname = kwargs['hostname']
    username = kwargs.get('username')
    port = kwargs.get('port')

    cpname = f'{uuid.uuid4()}.cp'
    cp = os.path.join(runtimedir, cpname)

    conn_timeout = 3.5
    timeout = int(conn_timeout)

    opts_connect = (f'-N '
                    f'-o ControlMaster=yes '
                    f'-o ControlPath="{cp}" '
                    f'-o ConnectTimeout={timeout} '
                    f'-o PreferredAuthentications=publickey')
    opts_run = (f'-o ControlMaster=no '
                f'-o ControlPath="{cp}" '
                f'-o PreferredAuthentications=publickey')
    opts_port = f'-p {port}' if port else ''
    opts_username = f'-l {username}' if username else ''

    # NB. command with ControlMaster=yes
    cmd_connect = f'ssh {opts_port} {opts_username} {opts_connect} {hostname}'
    # NB. command with ControlMaster=no
    cmd_run = f'ssh {opts_port} {opts_username} {opts_run} {hostname}'

    return {
        'cmd_connect': cmd_connect,
        'cmd_run': cmd_run,
        'control_socket': cp,
        'conn_timeout': conn_timeout,
        'tunnel': None,
        'is_connected': False,
    }


def connect(ctx):
    ssh_cmd = pick(ctx, 'ssh.cmd_connect')
    control_socket = pick(ctx, 'ssh.control_socket')
    conn_timeout = pick(ctx, 'ssh.conn_timeout')

    logger_local = pick(ctx, 'logger.local')
    logger_remote = pick(ctx, 'logger.remote')

    logger_local.debug(
        '# ssh control socket name: "%s"', os.path.basename(control_socket))
    logger_local.debug('# attempting to connect with connect timeout %s ...',
                       conn_timeout)

    tunnel = subprocess.Popen(shlex.split(ssh_cmd),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               encoding='utf-8')
    try:
        proc_stdout, proc_stderr = tunnel.communicate(timeout=conn_timeout)
    except subprocess.TimeoutExpired:
        proc_stdout = proc_stderr = None

    if tunnel.poll() is not None:
        # NB. means no connection to server
        if proc_stdout:
            logger_remote.info(proc_stdout.strip())
        if proc_stderr:
            logger_remote.error(proc_stderr.strip())

        raise YaggyConnectionError('[TUNNEL] connection failed')

    logger_local.info('# [TUNNEL] state: connected')

    mutate(ctx, 'ssh.tunnel', tunnel)
    mutate(ctx, 'ssh.is_connected', True)


def disconnect(ctx):
    tunnel = pick(ctx, 'ssh.tunnel')
    is_connected = pick(ctx, 'ssh.is_connected')
    conn_timeout = pick(ctx, 'ssh.conn_timeout')

    logger_local = pick(ctx, 'logger.local')

    if not is_connected or not tunnel:
        return

    if tunnel:
        res = tunnel.poll()
        if res is None:
            tunnel.terminate()
            tunnel.wait(timeout=conn_timeout)

        logger_local.info('# [TUNNEL] state: disconnected')

        mutate(ctx, 'ssh.tunnel', None)
        mutate(ctx, 'ssh.is_connected', False)
