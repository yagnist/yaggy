# -*- coding: utf-8 -*-

import os
import sys
import datetime
import pwd

from . import ssh, __version__ as version

from .logging import setup_logging, get_logger
from .utils import pick


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
    host = kwargs['host']
    dry_run = kwargs['dry_run']

    basedir = os.path.dirname(filename)
    basename = os.path.basename(filename)
    prefix = os.path.splitext(basename)[0]

    # logging
    logdir = mkdir(0o700, basedir, 'logs')
    logfilename = '{}.{}.{}.log'.format(
        prefix, host, dt.strftime('%Y%m%d%H%M%S'))
    logfile = os.path.join(logdir, logfilename)

    setup_logging(logfile, verbose)

    localname = 'localhost'
    w = max((len(host), len(localname)))

    logger_local = get_logger('yaggy.local', localname.rjust(w))
    logger_remote = get_logger('yaggy.remote', host.rjust(w))

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
            'user': get_local_username(),
        },
        'started_at': dt,
        'vars': {},
        'secrets': {},
        # 'env': setup_templates(),
        'results': {},
    }

    return ctx


def gather_tags(scenario):
    tree = {}
    pseudotree = {}
    current = []

    lines = (x for _, x in scenario if pick(x, 'cmdname') in ('TAG', 'UNTAG'))

    for parsed in lines:
        cmdname = pick(parsed, 'cmdname')
        args = pick(parsed, 'args')

        if cmdname == 'TAG':
            node = tree
            for tag in current:
                if tag not in node:
                    node[tag] = {}
                if tag not in pseudotree:
                    pseudotree[tag] = []
                node = node[tag]
                pseudotree[tag].append(args)
            node[args] = {}
            current.append(args)
        elif cmdname == 'UNTAG':
            assert current[-1] == args
            current = current[:-1]

    return {'tree': tree, 'pseudotree': pseudotree}
