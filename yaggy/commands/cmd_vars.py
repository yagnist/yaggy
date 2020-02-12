# -*- coding: utf-8 -*-

import os
import shlex

import qtoml

from ..utils import mergedict, pick


def validate_vars(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args.strip())

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)


def run_vars(ctx, **kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    logger = pick(ctx, 'logger.local')

    filename = os.path.join(basedir, args.strip())

    with open(filename, 'rt', encoding='utf-8') as f:
        data = qtoml.load(f)

    current = pick(ctx, 'vars')
    ctx['vars'] = mergedict(current, data)

    logger.info('VARS file "%s" loaded', args)


def validate_secrets(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    parts = shlex.split(args)

    if len(parts) == 1:
        # assume this is simple file to execute or include
        # NB. this makes it impossible to execute a command without arguments
        filename = os.path.join(basedir, args)

        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
