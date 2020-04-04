# -*- coding: utf-8 -*-

import subprocess
from functools import partial

import qtoml

from yaggy.utils import mergedict, pick

from . import validators


def load_toml(name, ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    if 'to_load' in kwargs:
        filename = kwargs['to_load']

        with open(filename, 'rt', encoding='utf-8') as f:
            data = f.read()

        msg = f'# [{name.upper()}] "%(args)s" file loaded'
    else:
        cmd = kwargs['to_exec']

        res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
        data = res.stdout

        msg = f'# [{name.upper()}] "%(args)s" command executed and loaded'

    data = qtoml.loads(data)

    current = pick(ctx, name)
    ctx[name] = mergedict(current, data)

    logger.info(msg, kwargs)


call_vars = partial(load_toml, 'vars')
call_secrets = partial(load_toml, 'secrets')


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
        validators.validate_vars,
    ],
    'call': call_secrets,
}
