# -*- coding: utf-8 -*-

import os
import shlex
import shutil
import subprocess

import qtoml

from ..exceptions import YaggySyntaxError
from ..utils import mergedict, pick


def validate_vars(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args.strip())

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    return {'to_load': filename}


def call_vars(ctx, **kwargs):
    filename = kwargs['to_load']

    logger = pick(ctx, 'logger.local')

    with open(filename, 'rt', encoding='utf-8') as f:
        data = qtoml.load(f)

    current = pick(ctx, 'vars')
    ctx['vars'] = mergedict(current, data)

    logger.debug('[VARS] "%(args)s" file loaded', kwargs)


def validate_secrets(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    parts = shlex.split(args)

    if not parts:
        raise YaggySyntaxError(
            'SECRETS command requires an argument to be specified '
            '(executable to call returning toml file '
            'or a path to toml file to load)')

    executable = shutil.which(parts[0])

    if executable is None and len(parts) == 1:
        executable = shutil.which(os.path.join(basedir, parts[0]))

    if executable is None:
        filename = os.path.join(basedir, shlex.quote(args.strip()))

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)

        return {'to_load': filename}

    return {'to_exec': [executable] + parts[1:]}


def call_secrets(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    if 'to_load' in kwargs:
        filename = kwargs['to_load']

        with open(filename, 'rt', encoding='utf-8') as f:
            data = f.read()

        msg = '[SECRETS] "%(args)s" file loaded'
    else:
        cmd = kwargs['to_exec']

        res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
        data = res.stdout

        msg = '[SECRETS] "%(args)s" command executed and loaded'

    data = qtoml.loads(data)

    current = pick(ctx, 'secrets')
    ctx['secrets'] = mergedict(current, data)

    logger.debug(msg, kwargs)
