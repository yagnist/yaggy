# -*- coding: utf-8 -*-

from functools import partial

from .common import execute_cmd, failed, succeed

from . import validators, vstate


call_lrun = partial(execute_cmd, remote=False)
call_lrun_exclamation = partial(
    execute_cmd, remote=False, raise_on_error=False)

call_lfailed = partial(execute_cmd, remote=False, predicate=failed)
call_lsucceed = partial(execute_cmd, remote=False, predicate=succeed)


CMD_LRUN = {
    'validators': [
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_lrun,
    'vstate': vstate.vstate_lrun,
    'is_internal': False,
}
CMD_LRUN_EXCLAMATION = {
    'validators': [
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_lrun_exclamation,
    'vstate': vstate.vstate_lrun,
    'is_internal': False,
}
CMD_LFAILED = {
    'validators': [
        validators.no_ref,
        validators.has_args,
    ],
    'call': call_lfailed,
    'vstate': vstate.vstate_conditional_lrun,
    'is_internal': False,
}
CMD_LSUCCEED = {
    'validators': [
        validators.no_ref,
        validators.has_args,
    ],
    'call': call_lsucceed,
    'vstate': vstate.vstate_conditional_lrun,
    'is_internal': False,
}
CMD_FETCH = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.has_args,
    ],
    'is_internal': False,
}
