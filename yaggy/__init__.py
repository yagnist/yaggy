# -*- coding: utf-8 -*-

from importlib.metadata import version, PackageNotFoundError


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
   __version__ = '0.0.0'
