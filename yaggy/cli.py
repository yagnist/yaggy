# -*- coding: utf-8 -*-

import os
import sys
import argparse

from .context import setup_context, gather_tags
from .logging import setup_logging, get_logger
from .parser import run_parser
from .ssh import disconnect
from .utils import pick, mutate


def parse_args(args):
    parser = argparse.ArgumentParser(
        description=('yg (aka yaggy) - simple tool to administer '
                     'remote servers using ssh'),
        add_help=False)
    parser.add_argument(
        '--help', action='help', default=argparse.SUPPRESS,
        help='show this help message and exit')
    commands = parser.add_subparsers(
        title='commands', dest='command', required=True)

    # tags command
    tags_cmd = commands.add_parser(
        'tags',
        help='show tags tree built from yaggy scenario',
        description='Show tags tree built from yaggy scenario.',
        add_help=False)

    tags_cmd.add_argument(dest='filename',
                          help='yaggy scenario')

    tags_cmd.add_argument(
        '--help', action='help', default=argparse.SUPPRESS,
        help='show this help message and exit')

    # run command
    run_cmd = commands.add_parser(
        'run', help='run yaggy scenario', add_help=False)

    run_cmd.add_argument(dest='filename',
                         help='yaggy scenario')

    run_cmd.add_argument(
        '-h',
        '--host',
        required=True,
        help='remote host to connect to (required)')
    run_cmd.add_argument(
        '-p', '--port', type=int, help='remote port to connect to')
    run_cmd.add_argument(
        '-u', '--user', help='remote user to connect as')
    run_cmd.add_argument(
        '-t',
        '--tags',
        help='comma-separated list of tags to run actions for')
    run_cmd.add_argument(
        '--dry-run', action='store_true', help='dry-run mode')
    run_cmd.add_argument(
        '-v', '--verbose', action='store_true', help='be verbose')
    run_cmd.add_argument(
        '--help', action='help', default=argparse.SUPPRESS,
        help='show this help message and exit')

    return parser.parse_args(args)


def cli():
    args = parse_args(sys.argv[1:])
    args = dict(vars(args))

    command = args.pop('command')
    filename = args.pop('filename')
    filename = os.path.abspath(os.path.expanduser(filename))

    if command == 'run':
        run(filename, **args)
    elif command == 'tags':
        list_tags(filename, **args)


def list_tags(filename, **kwargs):

    setup_logging()
    logger = get_logger('yaggy.local', 'localhost')

    scenario = run_parser(filename, logger)
    tags = gather_tags(scenario)

    def format_node(node, level=0):
        assert isinstance(node, dict)
        prefix = '' if level == 0 else '    ' * level
        nl = '' if level == 0 else '\n'
        res = ''
        keys = sorted(node.keys())
        for k in keys:
            nested = format_node(node[k], level=level + 1)
            res = f'{res}{nl}{prefix}{k}{nested}'
        return res

    tree = format_node(tags['tree'])
    logger.info('# tags tree')
    logger.info(tree)


def run(filename, **kwargs):

    dry_run = kwargs.get('dry_run')

    ctx = setup_context(filename, **kwargs)

    logger = pick(ctx, 'logger.local')

    scenario = run_parser(filename, logger)

    tags = gather_tags(scenario)
    mutate(ctx, 'tags', tags)

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
