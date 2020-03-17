# -*- coding: utf-8 -*-


is_valid = True
is_invalid = False


def vstate_connect(vstate, **kwargs):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_invalid, 'CONNECT command duplicate'

    return is_valid, {'is_connected': True}


def vstate_disconnect(vstate, **kwargs):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'is_connected': False}

    return is_invalid, 'DISCONNECT unable to disconnect, not connected'


def vstate_run(vstate, **kwargs):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'run_called': True}

    return is_invalid, 'RUN not connected, unable to run command'


def vstate_conditional_run(vstate, **kwargs):
    cmdname = kwargs['cmdname']

    is_connected = vstate.get('is_connected', False)
    run_called = vstate.get('run_called', False)
    lrun_called = vstate.get('lrun_called', False)

    if not is_connected:
        return is_invalid, f'{cmdname} not connected, unable to run command'

    if not run_called and not lrun_called:
        return is_invalid, (f'{cmdname} no RUN/RUN! or LRUN/LRUN! command '
                            f'appeared before, unable to run command')

    return is_valid, None


def vstate_lrun(vstate, **kwargs):
    return is_valid, {'lrun_called': True}


def vstate_conditional_lrun(vstate, **kwargs):
    cmdname = kwargs['cmdname']

    run_called = vstate.get('run_called', False)
    lrun_called = vstate.get('lrun_called', False)

    if not run_called and not lrun_called:
        return is_invalid, (f'{cmdname} no RUN/RUN! or LRUN/LRUN! command '
                            f'appeared before, unable to run command')

    return is_valid, None


def vstate_sync(vstate, **kwargs):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'sync_called': True}

    return is_invalid, 'SYNC not connected, unable to sync'


def vstate_fetch(vstate, **kwargs):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'fetch_called': True}

    return is_invalid, 'FETCH not connected, unable to fetch'
