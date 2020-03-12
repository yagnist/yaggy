# -*- coding: utf-8 -*-

import os
import shlex
import shutil


is_valid = True
is_invalid = False


def no_ref(**kwargs):
    ref = kwargs['ref']

    if ref is not None:
        cmdname = kwargs['cmdname']
        msg = f'{cmdname} command does not expect {ref} in arguments'
        return is_valid, msg

    return is_valid, None


def no_backref(**kwargs):
    backref = kwargs['backref']

    if backref is not None:
        cmdname = kwargs['cmdname']
        msg = f'{cmdname} command does not expect {backref} in arguments'
        return is_invalid, msg

    return is_valid, None


def no_args(**kwargs):
    args = kwargs['args']

    if args:
        cmdname = kwargs['cmdname']
        msg = f'{cmdname} command does not expect any arguments'
        return is_invalid, msg

    return is_valid, None


def has_args(**kwargs):
    args = kwargs['args']

    if not args:
        cmdname = kwargs['cmdname']
        msg = f'{cmdname} command expects some arguments'
        return is_invalid, msg

    return is_valid, None


def validate_vars(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args)

    if not os.path.isfile(filename):
        msg = f'VARS "{filename}" file not found'
        return is_invalid, msg

    return is_valid, {'to_load': filename}


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
            msg = f'SECRETS "{filename}" file not found'
            return is_invalid, msg

        return is_valid, {'to_load': filename}

    return is_valid, {'to_exec': [executable] + parts[1:]}


def validate_include(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args)

    if not os.path.isfile(filename):
        msg = f'INCLUDE "{filename}" file not found'
        return is_invalid, msg

    return is_valid, {'to_include': filename}


def validate_tag(**kwargs):
    tags = kwargs['tags']
    tag = kwargs['args']

    if tag in tags:
        msg = f'TAG "{tag}" is already in use, please use another'
        return is_invalid, msg

    return is_valid, {'tags': tags + (tag, )}


def validate_untag(**kwargs):
    tags = kwargs['tags']
    tag = kwargs['args']

    if not tags or tag not in tags:
        msg = f'TAG "{tag}" is unknown, unable to untag'
        return is_invalid, msg
    if tags[-1] != tag:
        msg = f'TAG/UNTAG pair "{tags[-1]}/{tag}" differs, unable to untag'
        return is_invalid, msg

    return is_valid, {'tags_delayed': tags[:-1]}
