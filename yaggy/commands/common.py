# -*- coding: utf-8 -*-

import shlex
import subprocess

from yaggy.exceptions import YaggySyntaxError, YaggyCommandError


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
