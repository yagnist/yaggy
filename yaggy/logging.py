# -*- coding: utf-8 -*-

import os
import logging
import logging.config

import click


class IndentedFormatter(logging.Formatter):

    def formatMessage(self, record):
        s = self._style.format(record)
        sep = ' | '
        parts = s.split(sep, 2)
        indent = sum(len(x) for x in parts[:-1])
        if len(parts) > 2:
            indent += len(sep)
        indent = self.indent = ' ' * indent + sep

        return s.replace('\n', '\n' + indent)

    def formatException(self, ei):
        s = super().formatException(ei)
        s = self.indent + s.replace('\n', '\n' + self.indent)
        return s


class ColoredStreamHandler(logging.StreamHandler):

    COLORS = {
        logging.INFO: 'bright_cyan',
        logging.WARNING: 'bright_yellow',
        logging.ERROR: 'bright_red',
        logging.CRITICAL: 'bright_magenta',
    }
    COLOR_LOCAL = 'bright_green'
    COLOR_REMOTE = 'bright_blue'

    def emit(self, record):

        fg = self.COLORS.get(record.levelno)
        is_local = record.name.endswith('local')
        is_remote = record.name.endswith('remote')

        try:
            msg = self.format(record)
            err = record.levelno in (logging.ERROR, logging.CRITICAL)
            if hasattr(self.formatter, 'indent'):
                width = len(self.formatter.indent)
                lines = msg.splitlines(keepends=True)
                head = lines[0]
                tail = lines[1:]

                if is_local or is_remote:
                    clr = self.COLOR_LOCAL if is_local else self.COLOR_REMOTE
                    left, leftsep, middle = head.partition('|')
                    middle, rightsep, right = middle.partition('|')

                    head = (
                        click.style(left + leftsep, fg=fg) +
                        click.style(middle, fg=clr) +
                        click.style(rightsep, fg=fg) +
                        right)

                tail = ''.join(
                    click.style(x[:width], fg=fg) + x[width:]
                    for x in tail
                )
                msg = head + tail
            click.echo(msg, err=err)
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


class YaggyLoggerAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        prefix = self.extra.get('prefix')
        msg = '| %s | %s' % (prefix, msg)
        return msg, kwargs


def logging_config(filename, verbose):
    level = 'DEBUG' if verbose else 'INFO'
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'indented': {
                'format': '%(levelname).1s %(asctime)s %(message)s',
                'datefmt': '%H:%M:%S',
                'class': 'yaggy.logging.IndentedFormatter',
            },
        },
        'handlers': {
            'console': {
                'level': level,
                'class': 'yaggy.logging.ColoredStreamHandler',
                'formatter': 'indented',
            },
            'file': {
                'level': level,
                'class': 'logging.FileHandler',
                'formatter': 'indented',
                'encoding': 'utf-8',
                'filename': filename,
            },
        },
        'loggers': {
            'yaggy': {
                'level': level,
                'handlers': ['console', 'file'],
                'propagate': False,
            },
        },
    }


def setup_logging(logdir, logfile, verbose):

    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    logfile = os.path.join(logdir, logfile)
    logconf = logging_config(logfile, verbose)

    logging.config.dictConfig(logconf)


def get_logger(name, prefix):
    logger = logging.getLogger(name)
    extra = {'prefix': prefix}
    adapter = YaggyLoggerAdapter(logger, extra=extra)
    return adapter
