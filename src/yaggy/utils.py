# -*- coding: utf-8 -*-

import re

from .exceptions import YaggyCommandError


def mergedict(a, b, path=None):
    path = '' if path is None else path

    if not isinstance(a, dict):
        raise TypeError(f'Unable to merge dicts on path "{path}"')
    if not isinstance(b, dict):
        raise TypeError(f'Unable to merge dicts on path "{path}"')

    if not a:
        return b

    res = a.copy()
    for k, v in b.items():
        if k not in res:
            res[k] = v
        else:
            sep = '.' if path else ''
            path = f'{path}{sep}{k}'
            res[k] = mergedict(res[k], v, path=path)

    return res


def pick(ctx, path):

    parts = path.split('.')
    for key in parts[:-1]:
        if key in ctx:
            ctx = ctx[key]
        else:
            return
    name = parts[-1]
    if hasattr(ctx, name):
        return getattr(ctx, name)
    return ctx.get(name)


def mutate(ctx, path, value):

    parts = path.split('.')
    for key in parts[:-1]:
        if key not in ctx:
            ctx[key] = {}
        ctx = ctx[key]
    ctx[parts[-1]] = value
