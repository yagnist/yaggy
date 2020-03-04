# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.config


# NB. see https://en.wikipedia.org/wiki/ANSI_escape_code
# styles bold:1 dim:2 italic:3 underline:4 inverse:7 hidden:8 strikethrough:9
FG = {
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'bright_black': 90,
    'bright_red': 91,
    'bright_green': 92,
    'bright_yellow': 93,
    'bright_blue': 94,
    'bright_magenta': 95,
    'bright_cyan': 96,
    'bright_white': 97,
}
BG = {
    'black': 40,
    'red': 41,
    'green': 42,
    'yellow': 43,
    'blue': 44,
    'magenta': 45,
    'cyan': 46,
    'white': 47,
    'bright_black': 100,
    'bright_red': 101,
    'bright_green': 102,
    'bright_yellow': 103,
    'bright_blue': 104,
    'bright_magenta': 105,
    'bright_cyan': 106,
    'bright_white': 107,
}


def colorize(text, fg=None, bg=None):
    clr = '\x1b['
    reset = '\x1b[0m'
    spec = []

    if bg in BG:
        spec.append(f'{BG[bg]}')
    if fg in FG:
        spec.append(f'{FG[fg]}')

    if spec:
        spec = ';'.join(spec)
        text = f'{clr}{spec}m{text}{reset}'

    return text


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

    COLOR_COMMENT = 'bright_black'

    def emit(self, record):

        fg = self.COLORS.get(record.levelno)
        body_color = None
        is_local = record.name.endswith('local')
        is_remote = record.name.endswith('remote')

        try:
            msg = self.format(record)
            err = record.levelno in (logging.ERROR, logging.CRITICAL)
            stream = sys.stderr if err else sys.stdout
            self.setStream(stream)

            # NB. just empty line in log
            if not getattr(record, 'message'):
                stream.write(self.terminator)
                self.flush()
                return
            if hasattr(self.formatter, 'indent'):
                width = len(self.formatter.indent)
                lines = msg.splitlines(keepends=True)
                head = lines[0]
                tail = lines[1:]

                if is_local or is_remote:
                    clr = self.COLOR_LOCAL if is_local else self.COLOR_REMOTE
                    left, leftsep, middle = head.partition('|')
                    middle, rightsep, right = middle.partition('|')

                    is_comment = right.startswith(' #')
                    body_color = self.COLOR_COMMENT if is_comment else None

                    head = (
                        colorize(left + leftsep, fg=fg) +
                        colorize(middle, fg=clr) +
                        colorize(rightsep, fg=fg) +
                        colorize(right, fg=body_color))

                tail = ''.join(
                    colorize(x[:width], fg=fg) +
                    colorize(x[width:], fg=body_color)
                    for x in tail
                )
                msg = head + tail
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


class YaggyLoggerAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        if not msg:
            return msg, kwargs
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


def setup_logging(logfile, verbose):
    logconf = logging_config(logfile, verbose)
    logging.config.dictConfig(logconf)


def get_logger(name, prefix):
    logger = logging.getLogger(name)
    extra = {'prefix': prefix}
    adapter = YaggyLoggerAdapter(logger, extra=extra)
    return adapter
