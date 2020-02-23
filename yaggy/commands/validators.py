# -*- coding: utf-8 -*-

from yaggy.exceptions import YaggySyntaxError


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


def no_args(**kwargs):
    args = kwargs['args']

    if args:
        cmdname = kwargs['cmdname']
        raise YaggySyntaxError(
            f'{cmdname} command does not expect any arguments')


def has_args(**kwargs):
    args = kwargs['args']

    if not args.strip():
        cmdname = kwargs['cmdname']
        raise YaggySyntaxError(f'{cmdname} command expects some arguments')
