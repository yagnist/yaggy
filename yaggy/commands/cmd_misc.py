# -*- coding: utf-8 -*-

import os

from ..utils import pick


def validate_include(**kwargs):
    basedir = kwargs['basedir']
    args = kwargs['args']

    filename = os.path.join(basedir, args.strip())

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    return {'to_include': filename}


def call_include(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.debug('[INCLUDE] "%(args)s" file included', kwargs)


def call_tag(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.debug('[TAG] "%(args)s" tag added', kwargs)


def call_untag(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.debug('[UNTAG] "%(args)s" tag removed', kwargs)


def call_echo(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.info('***** %(args)s *****', kwargs)
