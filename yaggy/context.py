# -*- coding: utf-8 -*-

import os
import sys
import datetime
import pwd

from . import ssh, __version__ as version

from .logging import setup_logging, get_logger
from .templates import setup_env
from .utils import pick


def get_local_username():
    return pwd.getpwuid(os.getuid()).pw_name


def mkdir(mode, *args):
    path = os.path.join(*args)
    if not os.path.isdir(path):
        os.mkdir(path)
        os.chmod(path, mode)
    return path


def setup_context(filename, **cli_kwargs):

    dt = datetime.datetime.now()

    host = cli_kwargs['host']
    dry_run = cli_kwargs['dry_run']

    basedir = os.path.dirname(filename)
    basename = os.path.basename(filename)
    prefix = os.path.splitext(basename)[0]

    filesdir = os.path.join(basedir, 'files')
    templatesdir = os.path.join(basedir, 'templates')

    # logging
    logdir = cli_kwargs['logdir'] = mkdir(0o700, basedir, cli_kwargs['logdir'])
    logfilename = '{}.{}.{}.log'.format(
        prefix, host, dt.strftime('%Y%m%d%H%M%S'))
    logfile = os.path.join(logdir, logfilename)

    setup_logging(filename=logfile)

    localname = 'localhost'
    w = max((len(host), len(localname)))

    logger_local = get_logger('yaggy.local', localname.rjust(w))
    logger_remote = get_logger('yaggy.remote', host.rjust(w))

    # ssh
    cli_kwargs['runtimedir'] = mkdir(0o700, basedir, cli_kwargs['runtimedir'])

    ssh_config = ssh.setup_ssh(logger=logger_local, **cli_kwargs)

    logger_local.info('# Yaggy version:%s localtime:%s',
                      version,
                      dt.strftime('"%Y-%m-%d %H:%M:%S"'))
    logger_local.info('# logfile path:\n'
                      '# logs/%s', logfilename)
    logger_local.info('# command line arguments:\n'
                      '# %s', ' '.join(sys.argv))
    if dry_run:
        logger_local.warning(
            '# DRY RUN mode, will try to connect to server only')

    ctx = {
        'filename': filename,
        'cli': cli_kwargs,
        'ssh': ssh_config,
        'logger': {
            'local': logger_local,
            'remote': logger_remote,
        },
        'local': {
            'user': get_local_username(),
            'rootdir': basedir,
            'filesdir': filesdir,
            'templatesdir': templatesdir,
        },
        'started_at': dt,
        'vars': {},
        'secrets': {},
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
