# -*- coding: utf-8 -*-

from yaggy.utils import pick

from . import validators


def call_include(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.info('# [INCLUDE] "%(args)s" file included', kwargs)


def call_tag(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.info('# [TAG] "%(args)s" tag added', kwargs)


def call_untag(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.info('# [UNTAG] "%(args)s" tag removed', kwargs)


def call_echo(ctx, **kwargs):

    logger = pick(ctx, 'logger.local')

    logger.info('***** %(args)s *****', kwargs)


CMD_INCLUDE = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_include,
    ],
    'call': call_include,
    'is_internal': True,
}
CMD_TAG = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_tag,
    ],
    'call': call_tag,
    'is_internal': True,
}
CMD_UNTAG = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_untag,
    ],
    'call': call_untag,
    'is_internal': True,
}
CMD_ECHO = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
    ],
    'call': call_echo,
    'is_internal': True,
}
