# -*- coding: utf-8 -*-

import os
import shlex
import shutil

from yaggy.exceptions import YaggySyntaxError


def no_ref(**kwargs):
    ref = kwargs['ref']

    if ref is not None:
        cmdname = kwargs['cmdname']
        msg = f'{cmdname} command does not expect {ref} in arguments'
        raise YaggySyntaxError(msg)


def no_backref(**kwargs):
    backref = kwargs['backref']

    if backref is not None:
        cmdname = kwargs['cmdname']
        msg = f'{cmdname} command does not expect {backref} in arguments'
        raise YaggySyntaxError(msg)


def no_args(**kwargs):
    args = kwargs['args']

    if args:
        cmdname = kwargs['cmdname']
        raise YaggySyntaxError(
            f'{cmdname} command does not expect any arguments')


def has_args(**kwargs):
    args = kwargs['args']

    if not args:
        cmdname = kwargs['cmdname']
        raise YaggySyntaxError(f'{cmdname} command expects some arguments')


def validate_vars(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args)

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    return {'to_load': filename}


def validate_secrets(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    parts = shlex.split(args)

    executable = shutil.which(parts[0])

    if executable is None and len(parts) == 1:
        executable = shutil.which(os.path.join(basedir, parts[0]))

    if executable is None:
        filename = os.path.join(basedir, shlex.quote(args))

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)

        return {'to_load': filename}

    return {'to_exec': [executable] + parts[1:]}


def validate_include(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args)

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    return {'to_include': filename}


def validate_tag(**kwargs):
    tags = kwargs['tags']
    tag = kwargs['args']

    if tag in tags:
        msg = f'TAG "{tag}" is already in use, please use another'
        raise YaggySyntaxError(msg)

    return {'tags': tags + (tag, )}


def validate_untag(**kwargs):
    tags = kwargs['tags']
    tag = kwargs['args']

    if not tags or tag not in tags:
        msg = f'TAG "{tag}" is unknown, unable to untag'
        raise YaggySyntaxError(msg)
    if tags[-1] != tag:
        msg = f'TAG/UNTAG pair "{tags[-1]}/{tag}" differs, unable to untag'
        raise YaggySyntaxError(msg)

    return {'tags': tags[:-1]}
