# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
import time
import uuid

from .exceptions import YaggyConnectionError
from .utils import mutate, pick


def setup_ssh(**cli_kwargs):

    logger = cli_kwargs['logger']

    runtimedir = cli_kwargs['runtimedir']

    host = cli_kwargs['host']
    user = cli_kwargs.get('user')
    port = cli_kwargs.get('port')

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
    opts_user = f'-l {user}' if user else ''

    # NB. command with ControlMaster=yes
    cmd_connect = f'ssh {opts_port} {opts_user} {opts_connect} {host}'
    # NB. command with ControlMaster=no
    cmd_run = f'ssh {opts_port} {opts_user} {opts_run} {host}'

    opts_scp = (f'-p '
                f'-r '
                f'-o ControlMaster=no '
                f'-o ControlPath="{cp}" '
                f'-o PreferredAuthentications=publickey')
    opts_scp_port = f'-P {port}' if port else ''
    cmd_scp = f'scp {opts_scp_port} {opts_scp}'

    return {
        'cmd_connect': cmd_connect,
        'cmd_run': cmd_run,
        'cmd_scp': cmd_scp,
        'control_socket': cp,
        'conn_timeout': conn_timeout,
        'tunnel': None,
        'is_connected': False,
    }


def connect(ctx, suppress_logs=False):
    ssh_cmd = pick(ctx, 'ssh.cmd_connect')
    control_socket = pick(ctx, 'ssh.control_socket')
    conn_timeout = pick(ctx, 'ssh.conn_timeout')

    logger_local = pick(ctx, 'logger.local')
    logger_remote = pick(ctx, 'logger.remote')

    if not suppress_logs:
        logger_local.info(
            '# ssh control socket name: "%s"',
            os.path.basename(control_socket))
        logger_local.info(
            '# attempting to connect with connect timeout %s ...',
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
        if not suppress_logs:
            if proc_stdout:
                logger_remote.info(proc_stdout.strip())
            if proc_stderr:
                logger_remote.error(proc_stderr.strip())

        raise YaggyConnectionError('[TUNNEL] connection failed')

    if not suppress_logs:
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


def reconnect(ctx, **parsed):

    cli_kwargs = pick(ctx, 'cli')
    logger_local = pick(ctx, 'logger.local')

    timeout = int(parsed['args'])

    disconnect(ctx)

    ssh_config = setup_ssh(logger=logger_local, **cli_kwargs)
    mutate(ctx, 'ssh', ssh_config)

    control_socket = pick(ctx, 'ssh.control_socket')
    conn_timeout = pick(ctx, 'ssh.conn_timeout')
    start = time.time()

    logger_local.info(
        '# [TUNNEL] attempting to reconnect with timeout %s ...', timeout)

    # NB. intentional delay before starting new connection
    time.sleep(conn_timeout * 2)

    while True:
        try:
            connect(ctx, suppress_logs=True)
        except YaggyConnectionError:
            pass

        is_connected = pick(ctx, 'ssh.is_connected')
        if is_connected:
            logger_local.info(
                '# ssh control socket name: "%s"',
                os.path.basename(control_socket))
            logger_local.info('# [TUNNEL] state: reconnected')
            break

        if (start + timeout) < time.time():
            raise YaggyConnectionError('[TUNNEL] reconnect failed')
