# -*- coding: utf-8 -*-


is_valid = True
is_invalid = False


def vstate_connect(vstate, **parsed):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_invalid, 'CONNECT command duplicate'

    return is_valid, {'is_connected': True}


def vstate_disconnect(vstate, **parsed):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'is_connected': False}

    return is_invalid, 'DISCONNECT unable to disconnect, not connected'


def vstate_reconnect(vstate, **parsed):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'reconnect_called': True}

    return is_invalid, 'RECONNECT not connected, unable to reconnect'


def vstate_run(vstate, **parsed):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'run_called': True}

    return is_invalid, 'RUN not connected, unable to run command'


def vstate_conditional_run(vstate, **parsed):
    cmdname = parsed['cmdname']

    is_connected = vstate.get('is_connected', False)
    run_called = vstate.get('run_called', False)
    lrun_called = vstate.get('lrun_called', False)

    if not is_connected:
        return is_invalid, f'{cmdname} not connected, unable to run command'

    if not run_called and not lrun_called:
        return is_invalid, (f'{cmdname} no RUN/RUN! or LRUN/LRUN! command '
                            f'appeared before, unable to run command')

    return is_valid, None


def vstate_lrun(vstate, **parsed):
    return is_valid, {'lrun_called': True}


def vstate_conditional_lrun(vstate, **parsed):
    cmdname = parsed['cmdname']

    run_called = vstate.get('run_called', False)
    lrun_called = vstate.get('lrun_called', False)

    if not run_called and not lrun_called:
        return is_invalid, (f'{cmdname} no RUN/RUN! or LRUN/LRUN! command '
                            f'appeared before, unable to run command')

    return is_valid, None


def vstate_sync(vstate, **parsed):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'sync_called': True}

    return is_invalid, 'SYNC not connected, unable to sync'


def vstate_fetch(vstate, **parsed):
    is_connected = vstate.get('is_connected', False)
    if is_connected:
        return is_valid, {'fetch_called': True}

    return is_invalid, 'FETCH not connected, unable to fetch'
