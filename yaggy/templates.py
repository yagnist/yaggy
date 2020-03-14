# -*- coding: utf-8 -*-

import jinja2

from .utils import pick


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

    def yaggy_var(name):
        return pick(ctx, f'vars.{name}')

    def yaggy_secret(name):
        return pick(ctx, f'secrets.{name}')

    env.globals['var'] = yaggy_var
    env.globals['secret'] = yaggy_secret

    return env
