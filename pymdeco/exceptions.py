# -*- coding: utf-8 -*-
#
# Author: Todor Bukov
# License: LGPL version 3.0 - see LICENSE.txt for details
#
"""
:mod:`exceptions` - Exception classes used within the library
=============================================================

.. module:: pymdeco.exceptions
   :platform: Unix, Windows
   :synopsis: Contains the exception classes used in the library
.. moduleauthor:: Todor Bukov

Contains the hierarchy of exceptions used within the library.
"""

class PymdecoException(Exception):
    """
    The base class for all exception used in the library. It is not meant to
    be raised by any functions/method directly, but can be used by the
    applications as "catch all" exception.
    """
    pass


class GeneralException(PymdecoException):
    """
    Raised by the various functions and object methods in the library.
    """
    pass


class MissingDependencyException(GeneralException):
    """
    Indicates that a third-party library that has not been installed or
    external command-line tool has not been found, but is required by the
    function or class to operates.
    """
    pass


class ServiceException(GeneralException):
    """
    Raised by high-level :mod:`pymdeco.services` classes.
    """
    pass

