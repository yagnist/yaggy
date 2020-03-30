# -*- coding: utf-8 -*-

import subprocess

import qtoml

from yaggy.utils import mergedict, pick

from . import validators


def call_vars(ctx, **kwargs):
    filename = kwargs['to_load']

    logger = pick(ctx, 'logger.local')

    with open(filename, 'rt', encoding='utf-8') as f:
        data = qtoml.load(f)

    current = pick(ctx, 'vars')
    ctx['vars'] = mergedict(current, data)

    logger.info('# [VARS] "%(args)s" file loaded', kwargs)


def call_secrets(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    if 'to_load' in kwargs:
        filename = kwargs['to_load']

        with open(filename, 'rt', encoding='utf-8') as f:
            data = f.read()

        msg = '# [SECRETS] "%(args)s" file loaded'
    else:
        cmd = kwargs['to_exec']

        res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
        data = res.stdout

        msg = '# [SECRETS] "%(args)s" command executed and loaded'

    data = qtoml.loads(data)

    current = pick(ctx, 'secrets')
    ctx['secrets'] = mergedict(current, data)

    logger.info(msg, kwargs)


CMD_VARS = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.has_args,
        validators.validate_vars,
    ],
    'call': call_vars,
}
CMD_SECRETS = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.has_args,
        validators.validate_secrets,
    ],
    'call': call_secrets,
}
