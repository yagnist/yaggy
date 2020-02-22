# -*- coding: utf-8 -*-

from functools import partial

from .common import execute_cmd, failed, succeed


call_lrun = partial(execute_cmd, remote=False)
call_lrun_exclamation = partial(
    execute_cmd, remote=False, raise_on_error=False)

call_lfailed = partial(execute_cmd, remote=False, predicate=failed)
call_lsucceed = partial(execute_cmd, remote=False, predicate=succeed)
