# -*- coding: utf-8 -*-


class YaggyError(Exception):
    pass


class YaggySyntaxError(YaggyError):
    pass


class YaggyCommandError(YaggyError):
    pass


class YaggyConnectionError(YaggyError):
    pass
