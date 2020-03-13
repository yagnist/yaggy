# -*- coding: utf-8 -*-

import jinja2


def setup_env(templatesdir):

    loader = jinja2.FileSystemLoader(templatesdir)
    env = jinja2.Environment(loader=loader)
    env.add_extension('jinja2.ext.autoescape')

    return env
