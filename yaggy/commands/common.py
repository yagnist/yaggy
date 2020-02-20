# -*- coding: utf-8 -*-

import subprocess

from ..exceptions import YaggySyntaxError


def no_ref_backref(**kwargs):
    ref = kwargs['ref']
    backref = kwargs['backref']

    if ref is not None or backref is not None:
        cmdname = kwargs['cmdname']
        msg = (f'{cmdname} command should not include '
               f'@ref or @backref in arguments')
        raise YaggySyntaxError(msg)


def run(*args, **kwargs):
    logger = kwargs.pop('logger')
    cmd = kwargs.pop('cmd')

    res = subprocess.run(*args, **kwargs)

    if res.returncode == 0:
        logger.info('---')
        logger.info('$ %s', cmd)
        logger.info('%s', res.stdout.strip())
    else:
        logger.error('---')
        logger.error('$ %s', cmd)
        logger.error('%s', res.stderr.strip())

    return res
