# -*- coding: utf-8 -*-

import os
import datetime

import paramiko

from .logging import setup_logging, get_logger


def load_ssh_config(hostname):
    conffile = os.path.join(os.path.expanduser('~'), '.ssh', 'config')

    if os.path.isfile(conffile):
        config = paramiko.SSHConfig.from_path(conffile)
        return config.lookup(hostname)

    return paramiko.SSHConfigDict()


def make_ssh_client():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    return client


def setup_context(filename, **kwargs):

    dt = datetime.datetime.now()

    verbose = kwargs['verbose']
    hostname = kwargs['hostname']

    basedir = os.path.dirname(filename)
    basename = os.path.basename(filename)
    prefix = os.path.splitext(basename)[0]

    logdir = os.path.join(basedir, 'logs')
    logfile = '{}.{}.{}.log'.format(
        prefix, hostname, dt.strftime('%Y%m%d%H%M%S'))

    setup_logging(logdir, logfile, verbose)

    ssh_config = load_ssh_config(hostname)
    ssh_client = make_ssh_client()

    remotename = ssh_config['hostname']
    localname = 'localhost'
    w = max((len(remotename), len(localname)))

    logger_local = get_logger('yaggy.local', localname.rjust(w))
    logger_remote = get_logger('yaggy.remote', remotename.rjust(w))

    ctx = {
        'filename': filename,
        'basedir': basedir,
        'cli': kwargs,
        'ssh': {
            'config': ssh_config,
            'client': ssh_client,
        },
        'logger': {
            'local': logger_local,
            'remote': logger_remote,
        },
        'started_at': dt,
        'vars': {},
        'secrets': {},
        # 'env': setup_templates(),
        'results': {},
    }

    return ctx
