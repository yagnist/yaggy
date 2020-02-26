# -*- coding: utf-8 -*-

import os

from .commands import command_parts
from .exceptions import YaggySyntaxError


def load(filename):

    with open(filename, 'rt', encoding='utf-8') as f:
        buf = []

        for linenum, line in enumerate(f, start=1):
            line = line.rstrip()
            is_comment = line.startswith('#')
            if not line or is_comment:
                continue
            if line.endswith('\\'):
                buf.append(line)
                continue
            if buf:
                buf.append(line)
                cmd = (x.rstrip('\\').lstrip() for x in buf)
                cmd = ''.join(cmd)
                start = linenum - len(buf) + 1
                lines = f'{start}-{linenum}'
                buf = []
                yield lines, cmd
                continue

            yield linenum, line


def parse(filename, tags=None, refs=None, rootdir=None):

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    tags = tuple() if tags is None else tags
    assert isinstance(tags, tuple)

    refs = set() if refs is None else refs
    assert isinstance(refs, set)

    basedir = os.path.dirname(filename)
    if rootdir is None:
        rootdir = basedir
    relpath = os.path.relpath(filename, start=rootdir)

    for linenum, line in load(filename):

        to_include = None
        cmdname, cmd, ref, backref, args = command_parts(line)

        if cmd is None:
            msg = f'Unknown command in line "{line}"'
            raise YaggySyntaxError(relpath, linenum, msg)

        if ref is not None and ref == backref:
            msg = f'Backreference equals to reference "{ref}"'
            raise YaggySyntaxError(relpath, linenum, msg)

        if backref is not None and backref not in refs:
            msg = f'Unknown backreference "{backref}"'
            raise YaggySyntaxError(relpath, linenum, msg)

        if ref is not None and ref in refs:
            msg = f'Reference "{ref}" is already taken, please use another'
            raise YaggySyntaxError(relpath, linenum, msg)

        assert 'validators' in cmd
        assert isinstance(cmd['validators'], (list, tuple))

        parsed = {
            'cmdname': cmdname,
            'ref': ref,
            'backref': backref,
            'args': args,
            'tags': tuple(tags),
            'line': line,
            'basedir': basedir,
        }

        for validator in cmd['validators']:
            is_valid, res = validator(**parsed)
            if not is_valid:
                raise YaggySyntaxError(relpath, linenum, res)
            if res is not None and isinstance(res, dict):
                parsed.update(res)

        if cmdname == 'INCLUDE':
            to_include = parsed['to_include']
        elif cmdname in ('TAG', 'UNTAG'):
            tags = parsed['tags']

        if ref is not None:
            refs.add(ref)

        yield cmd, parsed

        if to_include is not None:
            yield from parse(to_include, tags=tags, refs=refs, rootdir=rootdir)
