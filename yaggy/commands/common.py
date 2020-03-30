# -*- coding: utf-8 -*-

import os
import shlex
import subprocess

from yaggy.exceptions import YaggyCommandError
from yaggy.utils import pick, mutate


def failed(ctx, backref):
    path = '__lastrun' if backref is None else f'results.{backref}'
    res = pick(ctx, path)
    return res.returncode != 0


def succeed(ctx, backref):
    path = '__lastrun' if backref is None else f'results.{backref}'
    res = pick(ctx, path)
    return res.returncode == 0


def log_result(cmd, res, logger, raise_on_error=True):
    if res.returncode == 0:
        logger.info('-' * 70)
        logger.info('$ %s', cmd)
        stdout = res.stdout.strip()
        if stdout:
            logger.info('%s', stdout)
    else:
        logger.error('-' * 70)
        logger.error('$ %s', cmd)
        stderr = res.stderr.strip()
        if stderr:
            logger.error('%s', stderr)
        logger.error('# return code: %s', res.returncode)

        if raise_on_error:
            msg = f'command {cmd} failed'
            raise YaggyCommandError(msg)


def run(**kwargs):
    cmd = kwargs.pop('cmd')
    execute = kwargs.pop('execute', None)

    logger = kwargs.pop('logger')
    raise_on_error = kwargs.pop('raise_on_error', True)
    noisy = kwargs.pop('noisy', True)

    args = shlex.split(cmd)
    if execute is not None:
        args = shlex.split(execute) + args

    res = subprocess.run(args, **kwargs)

    if noisy:
        log_result(cmd, res, logger, raise_on_error=raise_on_error)

    return res


def execute_cmd(ctx, raise_on_error=True, remote=False, predicate=None,
                **kwargs):

    cmd = kwargs['args']
    ref = kwargs.get('ref')

    execute = pick(ctx, 'ssh.cmd_run') if remote else None
    logger = pick(ctx, 'logger.remote' if remote else 'logger.local')

    if callable(predicate):
        backref = kwargs.get('backref')
        cond = predicate(ctx, backref)

        if not cond:
            return

    if not remote:
        cmd = os.path.expandvars(os.path.expanduser(cmd))

    res = run(execute=execute,
              cmd=cmd,
              logger=logger,
              raise_on_error=raise_on_error,
              capture_output=True,
              encoding='utf-8')

    mutate(ctx, '__lastrun', res)
    if ref:
        mutate(ctx, f'results.{ref}', res)
