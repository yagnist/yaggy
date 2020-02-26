# -*- coding: utf-8 -*-


class YaggyError(Exception):
    pass


class YaggySyntaxError(YaggyError):

    def __init__(self, filename, linenum, message):
        super().__init__()
        self.filename = filename
        self.linenum = linenum
        self.message = message

    def __str__(self):
        return (
            f'syntax error in "{self.filename}:{self.linenum}"\n'
            f'{self.message}'
        )


class YaggyCommandError(YaggyError):
    pass


class YaggyConnectionError(YaggyError):
    pass
