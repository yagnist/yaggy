# -*- coding: utf-8 -*-

import os
import sys
import datetime

import click

from .context import setup_context
from .exceptions import YaggyError
from .parser import parse
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

    ctx = setup_context(filename, **kwargs)

    logger = pick(ctx, 'logger.local')
    dt = pick(ctx, 'started_at')

    logger.info('***** Yaggy version:%s localtime:%s *****',
                version,
                dt.strftime('"%Y-%m-%d %H:%M:%S"'))

    try:
        scenario = list(parse(filename))
    except YaggyError as e:
        msg = str(e)
        logger.exception('Parsing error: "%s"', msg)
        sys.exit(1)
    except FileNotFoundError as e:
        msg = str(e)
        logger.exception('File not found: "%s"', msg)
        sys.exit(1)

    try:

        for cmd, kwargs in scenario:
            logger.info('')
            logger.debug('# %(line)s', kwargs)

            caller = cmd.get('call')
            if callable(caller):
                try:
                    caller(ctx, **kwargs)
                except Exception as e:
                    logger.error('"%(cmdname)s" command failed', kwargs)

                    msg = str(e)
                    logger.exception(e)
                    sys.exit(1)

    finally:
        ssh= pick(ctx, 'ssh')
        if 'proc' in ssh:
            ssh_proc = pick(ssh, 'proc')
            ssh_timeout = pick(ssh, 'cmd_timeout')

            res = ssh_proc.poll()
            if res is None:
                ssh_proc.terminate()
                ssh_proc.wait(timeout=ssh_timeout)
