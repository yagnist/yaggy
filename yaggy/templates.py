# -*- coding: utf-8 -*-

import os
from functools import partial

import jinja2

from .utils import pick, mutate


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


def render(ctx, filename=None, string=None):

    env = pick(ctx, 'jinja.env')

    host = pick(ctx, 'cli.host')
    user = pick(ctx, 'cli.user')
    syncroot = pick(ctx, 'cli.syncroot')

    dt = pick(ctx, 'local.datetime')
    dt_str = dt.strftime('%Y%m%d%H%M%S')

    yaggy_managed = 'DO NOT EDIT! This file is managed by yaggy.'

    if not env:
        env = setup_env(ctx)
        mutate(ctx, 'jinja.env', env)

    content = ''

    if filename is not None:
        tmpl = env.get_template(filename)
        content = tmpl.render(filename=os.path.basename(filename),
                              yaggy_managed=yaggy_managed,
                              hostname=host,
                              username=user,
                              syncroot=syncroot,
                              now=dt,
                              now_str=dt_str)
    elif string is not None:
        tmpl = env.from_string(string)
        content = tmpl.render(hostname=host,
                              username=user,
                              syncroot=syncroot,
                              now=dt,
                              now_str=dt_str)

    return content
