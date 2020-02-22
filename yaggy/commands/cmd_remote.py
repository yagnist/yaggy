# -*- coding: utf-8 -*-

from functools import partial

from .common import execute_cmd, failed, succeed


call_run = partial(execute_cmd, remote=True)
call_run_exclamation = partial(execute_cmd, remote=True, raise_on_error=False)

call_failed = partial(execute_cmd, remote=True, predicate=failed)
call_succeed = partial(execute_cmd, remote=True, predicate=succeed)
