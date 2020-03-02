# -*- coding: utf-8 -*-

import os
import sys
import datetime
import pwd

from . import ssh, __version__ as version

from .exceptions import YaggyError
from .logging import setup_logging, get_logger
from .parser import parse


def get_local_username():
    return pwd.getpwuid(os.getuid()).pw_name


def mkdir(mode, *args):
    path = os.path.join(*args)
    if not os.path.isdir(path):
        os.mkdir(path)
        os.chmod(path, mode)
    return path


def setup_context(filename, **kwargs):

    dt = datetime.datetime.now()

    verbose = kwargs['verbose']
    hostname = kwargs['hostname']
    dry_run = not kwargs['run']

    basedir = os.path.dirname(filename)
    basename = os.path.basename(filename)
    prefix = os.path.splitext(basename)[0]

    # logging
    logdir = mkdir(0o700, basedir, 'logs')
    logfilename = '{}.{}.{}.log'.format(
        prefix, hostname, dt.strftime('%Y%m%d%H%M%S'))
    logfile = os.path.join(logdir, logfilename)

    setup_logging(logfile, verbose)

    localname = 'localhost'
    w = max((len(hostname), len(localname)))

    logger_local = get_logger('yaggy.local', localname.rjust(w))
    logger_remote = get_logger('yaggy.remote', hostname.rjust(w))

    try:
        scenario = list(parse(filename))
    except YaggyError as e:
        logger_local.error('%s', str(e))
        sys.exit(1)
    except FileNotFoundError as e:
        logger_local.error('File not found: "%s"', str(e))
        sys.exit(1)

    # ssh
    runtimedir = mkdir(0o700, basedir, '.yaggy')

    ssh_config = ssh.setup_ssh(runtimedir, logger=logger_local, **kwargs)

    logger_local.info('# Yaggy version:%s localtime:%s',
                      version,
                      dt.strftime('"%Y-%m-%d %H:%M:%S"'))
    logger_local.info('# logfile path: "logs/%s"', logfilename)
    if dry_run:
        logger_local.warning(
            '# DRY RUN mode, will try to connect to server only')

    ctx = {
        'filename': filename,
        'basedir': basedir,
        'cli': kwargs,
        'ssh': ssh_config,
        'logger': {
            'local': logger_local,
            'remote': logger_remote,
        },
        'local': {
            'username': get_local_username(),
        },
        'started_at': dt,
        'vars': {},
        'secrets': {},
        # 'env': setup_templates(),
        'results': {},
    }

    return ctx, scenario
