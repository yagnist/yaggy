# -*- coding: utf-8 -*-

import shlex
import subprocess

from yaggy.utils import pick

from .common import log_result
from . import validators, vstate


def call_fetch(ctx, **parsed):

    logger_local = pick(ctx, 'logger.local')

    cmd_scp = pick(ctx, 'ssh.cmd_scp')
    host = pick(ctx, 'cli.host')
    user = pick(ctx, 'cli.user')

    args = parsed['args']
    args = f'{user}@{host}:{args}' if user else f'{host}:{args}'
    cmd = shlex.split(f'{cmd_scp} {args}')
    cmd_repr = f'scp {args}'

    res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
    log_result(cmd_repr, res, logger_local)


CMD_FETCH = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_fetch,
    'vstate': vstate.vstate_fetch,
}
