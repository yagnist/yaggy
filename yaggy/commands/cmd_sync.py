# -*- coding: utf-8 -*-

import os
import shlex
import subprocess

from yaggy.utils import pick

from .common import log_result
from . import validators, vstate


def call_sync(ctx, **parsed):

    logger_remote = pick(ctx, 'logger.remote')
    logger_local = pick(ctx, 'logger.local')

    cmd_run = pick(ctx, 'ssh.cmd_run')
    cmd_scp = pick(ctx, 'ssh.cmd_scp')
    syncroot = pick(ctx, 'ssh.syncroot')

    host = pick(ctx, 'cli.host')
    user = pick(ctx, 'cli.user')
    cli_tags = pick(ctx, 'cli.tags_set')

    filesdir = pick(ctx, 'local.filesdir')
    rootdir = pick(ctx, 'local.rootdir')
    reldir = os.path.relpath(filesdir, start=rootdir)

    if not os.path.isdir(filesdir):
        return

    to_copy = os.listdir(filesdir)
    if cli_tags:
        to_copy = [x for x in to_copy if x in cli_tags]

    if not to_copy:
        return

    # make sure sync root exists
    cmd_mksyncroot = f'mkdir -p {syncroot}'
    mksyncroot = shlex.split(f'{cmd_run} {cmd_mksyncroot}')
    res = subprocess.run(mksyncroot,
                         capture_output=True,
                         encoding='utf-8')
    log_result(cmd_mksyncroot, res, logger_remote)

    # prepare command to run
    src = ' '.join(os.path.join(filesdir, x) for x in to_copy)
    target = f'{user}@{host}:{syncroot}' if user else f'{host}:{syncroot}'
    cmd = shlex.split(f'{cmd_scp} {src} {target}')

    # prepare command repr for logging
    prefix = ' ' * 6
    relsrc = f' \\\n{prefix}'.join(os.path.join(reldir, x) for x in to_copy)
    cmd_repr = f'scp {relsrc} \\\n{prefix}{target}'

    res = subprocess.run(cmd,
                         capture_output=True,
                         encoding='utf-8')
    log_result(cmd_repr, res, logger_local)


CMD_SYNC = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.no_args,
    ],
    'call': call_sync,
    'vstate': vstate.vstate_sync,
    'is_internal': False,
}
