# -*- coding: utf-8 -*-

import os
import shlex
import subprocess

from yaggy.exceptions import YaggySyntaxError, YaggyCommandError
from yaggy.utils import pick, mutate


def no_ref_backref(**kwargs):
    ref = kwargs['ref']
    backref = kwargs['backref']

    if ref is not None or backref is not None:
        cmdname = kwargs['cmdname']
        msg = (f'{cmdname} command does not expect '
               f'@ref or @backref in arguments')
        raise YaggySyntaxError(msg)


def no_backref(**kwargs):
    backref = kwargs['backref']

    if backref is not None:
        cmdname = kwargs['cmdname']
        msg = (f'{cmdname} command does not expect '
               f'@backref in arguments')
        raise YaggySyntaxError(msg)


def has_args(**kwargs):
    args = kwargs['args']

    if not args.strip():
        cmdname = kwargs['cmdname']
        raise YaggySyntaxError(f'{cmdname} command expects some command '
                               f'to execute')


def failed(ctx, backref):
    path = '__lastres' if backref is None else f'results.{backref}'
    res = pick(ctx, path)
    return res.returncode != 0


def succeed(ctx, backref):
    path = '__lastres' if backref is None else f'results.{backref}'
    res = pick(ctx, path)
    return res.returncode == 0


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
        if res.returncode == 0:
            logger.info('-' * 70)
            # logger.info('$ %s\n%s', cmd, res.stdout.strip())
            logger.info('$ %s', cmd)
            logger.info('%s', res.stdout.strip())
        else:
            logger.error('-' * 70)
            # logger.error('$ %s\n%s', cmd, res.stderr.strip())
            logger.error('$ %s', cmd)
            logger.error('%s', res.stderr.strip())
            logger.error('# return code: %s', res.returncode)

            if raise_on_error:
                msg = f'command {cmd} failed'
                raise YaggyCommandError(msg)

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
            logger.debug('# run condition is false, skipping "%s"', cmd)
            return
        else:
            logger.debug('# run condition is true, going to run "%s"', cmd)

    if not remote:
        cmd = os.path.expandvars(os.path.expanduser(cmd))

    res = run(execute=execute,
              cmd=cmd,
              logger=logger,
              raise_on_error=raise_on_error,
              capture_output=True,
              encoding='utf-8')

    mutate(ctx, '__lastres', res)
    if ref:
        mutate(ctx, f'results.{ref}', res)
