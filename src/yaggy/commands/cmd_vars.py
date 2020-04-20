# -*- coding: utf-8 -*-

import os
import shlex
import shutil
import subprocess
from functools import partial

import qtoml

from yaggy.exceptions import YaggySyntaxError
from yaggy.utils import mergedict, pick

from . import validators


def validate_vars(**parsed):
    basedir = parsed['basedir']
    args = parsed['args']

    is_valid, is_invalid = True, False

    parts = shlex.split(args)

    executable = shutil.which(parts[0])

    if executable is None and len(parts) == 1:
        executable = shutil.which(os.path.join(basedir, parts[0]))

    if executable is None:
        filename = os.path.join(basedir, shlex.quote(args))

        if not os.path.isfile(filename):
            cmdname = parsed['cmdname']
            msg = f'{cmdname} "{filename}" file not found'
            return is_invalid, msg

        return is_valid, {'to_load': filename}

    return is_valid, {'to_exec': [executable] + parts[1:]}


def load_toml(name, ctx, **parsed):

    logger = pick(ctx, 'logger.local')

    is_valid, res = validate_vars(**parsed)
    if not is_valid:
        relpath = parsed.get('relpath', 'unknown')
        linenum = parsed.get('linenum', -1)
        raise YaggySyntaxError(relpath, linenum, res)

    if 'to_load' in res:
        filename = res['to_load']

        with open(filename, 'rt', encoding='utf-8') as f:
            data = f.read()

        msg = f'# [{name.upper()}] "%(args)s" file loaded'
    else:
        cmd = res['to_exec']

        result = subprocess.run(cmd, capture_output=True, encoding='utf-8')
        data = result.stdout

        msg = f'# [{name.upper()}] "%(args)s" command executed and loaded'

    data = qtoml.loads(data)

    current = pick(ctx, name)
    ctx[name] = mergedict(current, data)

    logger.info(msg, parsed)


call_vars = partial(load_toml, 'vars')
call_secrets = partial(load_toml, 'secrets')


CMD_VARS = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_vars,
}
CMD_SECRETS = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_secrets,
}
