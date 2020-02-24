# -*- coding: utf-8 -*-

from yaggy.utils import pick


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
