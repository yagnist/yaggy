# -*- coding: utf-8 -*-

from functools import partial

import jinja2

from .utils import pick


def get_var(ctx, prefix, name):
    return pick(ctx, f'{prefix}.{name}')


def setup_env(ctx):

    templatesdir = pick(ctx, 'local.templatesdir')

    loader = jinja2.FileSystemLoader(templatesdir)
    extensions = [
        'jinja2.ext.do',
        'jinja2.ext.loopcontrols',
        'jinja2.ext.with_',
        'jinja2.ext.autoescape',
    ]
    env = jinja2.Environment(loader=loader, extensions=extensions)

    env.globals['var'] = partial(get_var, ctx, 'vars')
    env.globals['secret'] = partial(get_var, ctx, 'secrets')
    env.globals['result'] = partial(get_var, ctx, 'results')

    return env
