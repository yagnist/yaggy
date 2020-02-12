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

    tags = set() if tags is None else tags
    assert isinstance(tags, set)

    refs = set() if refs is None else refs
    assert isinstance(refs, set)

    basedir = os.path.dirname(filename)

    for line in load(filename):

        to_include = None
        cmdname, cmd, ref, backref, args = command_parts(line)

        if cmd is None:
            # TODO better message including filename and line number
            msg = 'Unknown command in line "%s"' % line
            raise YaggySyntaxError(msg)

        if ref is not None and ref == backref:
            # TODO better message including filename and line number
            msg = 'Backreference equals to reference "%s"' % ref
            raise YaggySyntaxError(msg)

        if backref is not None and backref not in refs:
            # TODO better message including filename and line number
            msg = 'Unknown backreference "%s"' % backref
            raise YaggySyntaxError(msg)

        if ref is not None and ref in refs:
            # TODO better message including filename and line number
            msg = 'Reference "%s" is already taken, please use another' % ref
            raise YaggySyntaxError(msg)

        # print('ref:{} cmd:{} backref:{} args:{}'.format(
        #     ref or '', cmd, backref or '', args or ''))

        if cmdname == 'INCLUDE':
            to_include = os.path.join(basedir, args)
        elif cmdname == 'TAG':
            tags.add(args)
        elif cmdname == 'UNTAG':
            tags.remove(args)

        refs.add(ref)

        parsed = {
            'cmdname': cmdname,
            'ref': ref,
            'backref': backref,
            'args': args,
            'tags': tuple(tags),
            'line': line,
            'basedir': basedir,
        }

        if 'validate' in cmd:
            cmd['validate'](**parsed)
        if 'validate_ref_backref' in cmd:
            cmd['validate_ref_backref'](**parsed)

        yield cmd, parsed

        if to_include is not None:
            yield from parse(to_include, tags=tags, refs=refs)
