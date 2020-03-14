# -*- coding: utf-8 -*-

import os
import glob
import shlex
import subprocess

from yaggy.templates import setup_env
from yaggy.utils import pick

from .common import log_result
from . import validators, vstate


def call_sync(ctx, **parsed):

    logger_remote = pick(ctx, 'logger.remote')
    logger_local = pick(ctx, 'logger.local')

    cmd_run = pick(ctx, 'ssh.cmd_run')
    cmd_scp = pick(ctx, 'ssh.cmd_scp')
    syncroot = pick(ctx, 'ssh.syncroot')

    host = pick(ctx, 'cli.host')
    user = pick(ctx, 'cli.user')
    cli_tags = pick(ctx, 'cli.tags_set')

    templatesdir = pick(ctx, 'local.templatesdir')
    filesdir = pick(ctx, 'local.filesdir')
    rootdir = pick(ctx, 'local.rootdir')
    reldir = os.path.relpath(filesdir, start=rootdir)

    has_files = os.path.isdir(filesdir)
    to_copy = os.listdir(filesdir) if has_files else []
    if has_files and cli_tags:
        to_copy = [x for x in to_copy if x in cli_tags]

    # make sure sync root exists
    cmd_mksyncroot = f'mkdir -p {syncroot}'
    mksyncroot = shlex.split(f'{cmd_run} {cmd_mksyncroot}')
    res = subprocess.run(mksyncroot, capture_output=True, encoding='utf-8')
    log_result(cmd_mksyncroot, res, logger_remote)

    # copy files if any
    if to_copy:
        # prepare command to run
        src = ' '.join(os.path.join(filesdir, x) for x in to_copy)
        target = f'{user}@{host}:{syncroot}' if user else f'{host}:{syncroot}'
        cmd = shlex.split(f'{cmd_scp} {src} {target}')

        # prepare command repr for logging
        prefix = ' ' * 6
        relsrc = f' \\\n{prefix}'.join(os.path.join(reldir, x)
                                       for x in to_copy)
        cmd_repr = f'scp {relsrc} \\\n{prefix}{target}'

        res = subprocess.run(cmd,
                             capture_output=True,
                             encoding='utf-8')
        log_result(cmd_repr, res, logger_local)

    has_templates = os.path.isdir(templatesdir)

    # render templates if any
    if has_templates:
        if cli_tags:
            templates = [y
                         for x in cli_tags
                         for y in glob.glob(
                             os.path.join(templatesdir, x, '**', '*.j2'),
                             recursive=True)
                         ]
        else:
            templates = glob.glob(os.path.join(templatesdir, '**', '*.j2'),
                                  recursive=True)

        jinja_env = setup_env(ctx)
        # TODO
        context = {
            'yaggy_managed': 'DO NOT EDIT! This file is managed by yaggy.',
        }

        dirnames = set()
        for template in templates:
            filename = os.path.relpath(template, start=templatesdir)
            dst = os.path.splitext(filename)[0]
            dirname = os.path.join(syncroot, os.path.dirname(filename))

            if dirname not in dirnames:
                cmd_mkdir = f'mkdir -p {dirname}'
                mkdir = shlex.split(f'{cmd_run} {cmd_mkdir}')
                res = subprocess.run(mkdir,
                                     capture_output=True,
                                     encoding='utf-8')
                log_result(cmd_mkdir, res, logger_remote)

                dirnames.add(dirname)

            tmpl = jinja_env.get_template(filename)
            content = tmpl.render(filename=os.path.basename(filename),
                                  **context)

            target = os.path.join(syncroot, dst)
            cmd = f'cat >{target}'
            cmd = shlex.split(f'{cmd_run} {cmd}')
            res = subprocess.run(cmd,
                                 input=content,
                                 capture_output=True,
                                 encoding='utf-8')
            log_result(f'RENDER {filename} {target}', res, logger_remote)


CMD_SYNC = {
    'validators': [
        validators.no_ref,
        validators.no_backref,
        validators.no_args,
    ],
    'call': call_sync,
    'vstate': vstate.vstate_sync,
    'is_internal': False,
}
