# -*- coding: utf-8 -*-

import os
import sys
import datetime

import click

from .context import setup_context
from .ssh import disconnect
from .utils import pick


@click.command(help='Run yaggy scenario from specified file.')
@click.argument('filename', type=click.Path(exists=True, resolve_path=True))
@click.option(
    '-u', '--username', envvar='YAGGY_USERNAME',
    help='Username to connect to the server.')
@click.option(
    '-h', '--hostname', envvar='YAGGY_HOSTNAME', required=True,
    help='Server hostname to connect to.')
@click.option(
    '-p', '--port', envvar='YAGGY_PORT',
    type=int, help='Server port to connect to.')
@click.option(
    '-t', '--tag', multiple=True,
    help='Run actions for specified tag (can be specified multiple times).')
@click.option(
    '-v', '--verbose', is_flag=True, help='Be verbose.')
@click.option(
    '--run', is_flag=True,
    help='Must be set to actually run the scenario.')
def runner(filename, **kwargs):

    dry_run = not kwargs['run']

    ctx, scenario = setup_context(filename, **kwargs)

    logger = pick(ctx, 'logger.local')

    try:

        safe_commands = ('ECHO', 'CONNECT', 'DISCONNECT', 'INCLUDE', 'VARS',
                         'SECRETS', 'TAG', 'UNTAG')

        for cmd, parsed in scenario:
            logger.debug('')
            if not pick(cmd, 'is_internal'):
                logger.debug('# %(line)s', parsed)

            cmdname = pick(parsed, 'cmdname')
            caller = pick(cmd, 'call')

            if callable(caller):
                if dry_run and cmdname not in safe_commands:
                    continue
                try:
                    caller(ctx, **parsed)
                except Exception as e:
                    logger.error('"%(cmdname)s" command failed', parsed)

                    logger.exception(e)
                    sys.exit(1)

    finally:
        disconnect(ctx)
