# -*- coding: utf-8 -*-

from functools import partial

from yaggy.exceptions import YaggySyntaxError
from yaggy.utils import pick, mutate

from .common import run


def validate_run(**kwargs):
    args = kwargs['args']

    if not args.strip():
        cmdname = kwargs['cmdname']
        raise YaggySyntaxError(f'{cmdname} command expects some command '
                               f'to run on the remote server')


def call_run(ctx, raise_on_error=True, **kwargs):

    cmd = kwargs['args']
    ref = kwargs.get('ref')

    ssh_run = pick(ctx, 'ssh.cmd_run')

    logger = pick(ctx, 'logger.remote')

    res = run(execute=ssh_run,
              cmd=cmd,
              logger=logger,
              raise_on_error=raise_on_error,
              capture_output=True,
              encoding='utf-8')

    if ref:
        mutate(ctx, f'results.{ref}', res)


call_run_exclamation = partial(call_run, raise_on_error=False)
