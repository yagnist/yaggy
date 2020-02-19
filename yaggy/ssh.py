# -*- coding: utf-8 -*-

import os
import uuid


def init(runtimedir, **kwargs):

    logger = kwargs['logger']

    hostname = kwargs['hostname']
    username = kwargs.get('username')
    port = kwargs.get('port')

    cpname = f'{uuid.uuid4()}.cp'
    cp = os.path.join(runtimedir, cpname)

    timeout = 3.5
    conn_timeout = int(timeout)

    opts_connect = (f'-N '
                    f'-o ControlMaster=yes '
                    f'-o ControlPath="{cp}" '
                    f'-o ConnectTimeout={conn_timeout} '
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
        'cmd_timeout': timeout,
    }
