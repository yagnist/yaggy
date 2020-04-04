# -*- coding: utf-8 -*-

import re

from .exceptions import YaggyCommandError


_delim = '$'
_idpattern = r'(?a:[_a-z][_a-z0-9\.]*)'
_var_re = r"""
%(delim)s{(?:
    (?P<type>var|secret):(?P<name>%(idpattern)s) |
    (?P<special>%(idpattern)s)
)}
"""
VAR_RE = re.compile(
    _var_re % {'delim': re.escape(_delim), 'idpattern': _idpattern},
    re.IGNORECASE | re.VERBOSE
)


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


def render_vars(ctx, cmd_args):

    def replacer(match):
        res = None
        var_type = match.group('type')
        var_name = match.group('name')
        special = match.group('special')
        if var_type is not None and var_name is not None:
            res = pick(ctx, f'{var_type}s.{var_name}')
        elif special == 'syncroot':
            res = pick(ctx, 'cli.syncroot')
        if res is None:
            ref = match.group(0)
            raise YaggyCommandError(
                f'Unknown variable reference "{ref}" in command args')
        return res

    return VAR_RE.sub(replacer, cmd_args)
