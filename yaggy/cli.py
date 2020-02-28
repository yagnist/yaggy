# -*- coding: utf-8 -*-

import os
import sys
import datetime

import click

from .context import setup_context
from .exceptions import YaggyError
from .parser import parse
from .ssh import disconnect
from .utils import pick
from . import __version__ as version


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

    dry_run = kwargs.get('run', False) is False

    ctx = setup_context(filename, **kwargs)

    logger = pick(ctx, 'logger.local')
    dt = pick(ctx, 'started_at')

    logger.info('***** Yaggy version:%s localtime:%s *****',
                version,
                dt.strftime('"%Y-%m-%d %H:%M:%S"'))
    if dry_run:
        logger.info('')
        logger.info(
            '!!!!! dry run mode, will try to connect to server only !!!!!')

    try:
        scenario = list(parse(filename))
    except YaggyError as e:
        logger.error('%s', str(e))
        sys.exit(1)
    except FileNotFoundError as e:
        msg = str(e)
        logger.error('File not found: "%s"', msg)
        sys.exit(1)

    try:

        safe_commands = ('ECHO', 'CONNECT', 'DISCONNECT', 'INCLUDE', 'VARS',
                         'SECRETS', 'TAG', 'UNTAG')
        def is_internal(command):
            category = pick(command, 'category')
            return category == 'internal'

        for cmd, kw in scenario:
            logger.debug('')
            if not is_internal(cmd):
                logger.debug('# %(line)s', kw)

            cmdname = pick(kw, 'cmdname')
            caller = pick(cmd, 'call')

            if callable(caller):
                if dry_run and cmdname not in safe_commands:
                    continue
                try:
                    caller(ctx, **kw)
                except Exception as e:
                    logger.error('"%(cmdname)s" command failed', kw)

                    logger.exception(e)
                    sys.exit(1)

    finally:
        disconnect(ctx)
