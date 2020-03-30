# -*- coding: utf-8 -*-

import os
import sys
import argparse

from .context import setup_context, gather_tags
from .exceptions import YaggyError
from .logging import setup_logging, get_logger
from .parser import run_parser
from .ssh import disconnect
from .utils import pick, mutate, render_vars


def tags_type(value):
    return [x.strip() for x in value.split(',') if x.strip()]


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
        type=tags_type,
        action='extend',
        help='comma-separated list of tags to run actions for')
    run_cmd.add_argument(
        '--syncroot', default='~/.yaggy',
        help=('remote server directory to copy files and render templates to '
              '(defaults to "~/.yaggy")')
    )
    run_cmd.add_argument(
        '--runtimedir', default='.rt',
        help='local runtime directory to store ssh control path socket file')
    run_cmd.add_argument(
        '--logdir', default='logs',
        help='local logs directory to store yaggy logs')
    run_cmd.add_argument(
        '--dry-run', action='store_true', help='dry-run mode')
    run_cmd.add_argument(
        '--help', action='help', default=argparse.SUPPRESS,
        help='show this help message and exit')

    return parser.parse_args(args)


def cli():
    args = parse_args(sys.argv[1:])
    kwargs = dict(vars(args))

    command = kwargs.pop('command')
    filename = kwargs.pop('filename')
    filename = os.path.abspath(os.path.expanduser(filename))

    if command == 'run':
        tags = kwargs['tags']
        tags = set() if tags is None else set(tags)
        kwargs['tags_set'] = tags
        run(filename, **kwargs)
    elif command == 'tags':
        list_tags(filename, **kwargs)


def list_tags(filename, **cli_kwargs):

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


def run(filename, **cli_kwargs):

    dry_run = cli_kwargs.get('dry_run')
    cli_tags = cli_kwargs.get('tags_set')

    ctx = setup_context(filename, **cli_kwargs)

    logger = pick(ctx, 'logger.local')

    scenario = run_parser(filename, logger)

    tags = gather_tags(scenario)
    mutate(ctx, 'tags', tags)

    if cli_tags:
        cli_tags_repr = ','.join(cli_kwargs.get('tags'))
        logger.info('# selected tags to run commands for: "%s"', cli_tags_repr)

    try:

        safe_commands = ('CONNECT', 'DISCONNECT', 'INCLUDE', 'VARS',
                         'SECRETS', 'TAG', 'UNTAG')

        for cmd, parsed in scenario:

            caller = pick(cmd, 'call')
            cmdname = pick(parsed, 'cmdname')
            cmd_tags = set(pick(parsed, 'tags'))

            if cli_tags and cmd_tags and cli_tags.isdisjoint(cmd_tags):
                continue

            if cmdname == 'ECHO' and not dry_run:
                logger.info('')
                logger.info('***** %(args)s *****', parsed)
            else:
                logger.info('# %(line)s', parsed)

            if dry_run and cmdname not in safe_commands:
                continue

            if callable(caller):
                try:
                    cmd_args = parsed['args']
                    if cmd_args:
                        parsed['args'] = render_vars(ctx, cmd_args)

                    caller(ctx, **parsed)
                except YaggyError as e:
                    logger.error('%s', str(e))
                    sys.exit(1)
                except Exception as e:
                    logger.error('"%(cmdname)s" command failed', parsed)

                    logger.exception(e)
                    sys.exit(1)

    finally:
        disconnect(ctx)
