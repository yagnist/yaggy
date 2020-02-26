# -*- coding: utf-8 -*-

import os

from .commands import command_parts
from .exceptions import YaggySyntaxError


def load(filename):

    with open(filename, 'rt', encoding='utf-8') as f:
        buf = []

        for line in f:
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
                buf = []
                yield cmd
                continue

            yield line


def parse(filename, tags=None, refs=None):

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    tags = tuple() if tags is None else tags
    assert isinstance(tags, tuple)

    refs = set() if refs is None else refs
    assert isinstance(refs, set)

    basedir = os.path.dirname(filename)

    for line in load(filename):

        to_include = validate_res = None
        cmdname, cmd, ref, backref, args = command_parts(line)

        if cmd is None:
            # TODO better message including filename and line number
            msg = f'Unknown command in line "{line}"'
            raise YaggySyntaxError(msg)

        if ref is not None and ref == backref:
            # TODO better message including filename and line number
            msg = f'Backreference equals to reference "{ref}"'
            raise YaggySyntaxError(msg)

        if backref is not None and backref not in refs:
            # TODO better message including filename and line number
            msg = f'Unknown backreference "{backref}"'
            raise YaggySyntaxError(msg)

        if ref is not None and ref in refs:
            # TODO better message including filename and line number
            msg = f'Reference "{ref}" is already taken, please use another'
            raise YaggySyntaxError(msg)

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
            validate_res = validator(**parsed)
            if validate_res is not None and isinstance(validate_res, dict):
                parsed.update(validate_res)

        if cmdname == 'INCLUDE':
            to_include = parsed['to_include']
        elif cmdname in ('TAG', 'UNTAG'):
            tags = parsed['tags']

        if ref is not None:
            refs.add(ref)

        yield cmd, parsed

        if to_include is not None:
            yield from parse(to_include, tags=tags, refs=refs)
