# -*- coding: utf-8 -*-

from ..exceptions import YaggySyntaxError


def no_ref_backref(**kwargs):
    ref = kwargs['ref']
    backref = kwargs['backref']

    if ref is not None or backref is not None:
        cmdname = kwargs['cmdname']
        msg = (f'{cmdname} command should not include '
               f'@ref or @backref in arguments')
        raise YaggySyntaxError(msg)
