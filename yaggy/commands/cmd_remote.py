# -*- coding: utf-8 -*-

from functools import partial

from .common import execute_cmd, failed, succeed

from . import validators, vstate


call_run = partial(execute_cmd, remote=True)
call_run_exclamation = partial(execute_cmd, remote=True, raise_on_error=False)

call_failed = partial(execute_cmd, remote=True, predicate=failed)
call_succeed = partial(execute_cmd, remote=True, predicate=succeed)


CMD_RUN = {
    'validators': [
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_run,
    'vstate': vstate.vstate_run,
    'is_internal': False,
}
CMD_RUN_EXCLAMATION = {
    'validators': [
        validators.no_backref,
        validators.has_args,
    ],
    'call': call_run_exclamation,
    'vstate': vstate.vstate_run,
    'is_internal': False,
}
CMD_FAILED = {
    'validators': [
        validators.no_ref,
        validators.has_args,
    ],
    'call': call_failed,
    'vstate': vstate.vstate_conditional_run,
    'is_internal': False,
}
CMD_SUCCEED = {
    'validators': [
        validators.no_ref,
        validators.has_args,
    ],
    'call': call_succeed,
    'vstate': vstate.vstate_conditional_run,
    'is_internal': False,
}
CMD_SYNC = {
    'validators': [
        validators.no_backref,
        validators.has_args,
    ],
    'is_internal': False,
}
CMD_CHANGED = {
    'validators': [
        validators.no_ref,
        validators.has_args,
    ],
    'is_internal': False,
}
