# -*- coding: utf-8 -*-

from yaggy.utils import pick

from . import validators


CMD_INCLUDE = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_include,
    ],
}
CMD_TAG = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_tag,
    ],
}
CMD_UNTAG = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.validate_untag,
    ],
}
CMD_ECHO = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
    ],
}
