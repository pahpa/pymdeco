# -*- coding: utf-8 -*-
#
# Author: Todor Bukov
# License: LGPL version 3.0 - see LICENSE.txt for details
#
"""
:mod:`utils` - Various utility functions and classes
=====================================================

.. module:: pymdeco.utils
   :platform: Unix, Windows
   :synopsis: Provides commonly used utility functions
.. moduleauthor:: Todor Bukov

Contains various utility functions used by the rest of the package.
"""
from __future__ import print_function
# internal Python modules
import hashlib
import os, stat
import sys
import time, datetime
from collections import OrderedDict
import numbers
import types
import json
from pymdeco.exceptions import GeneralException


def check_dependencies():
    """
    Checks if the required dependenices for the package are present (with
    the default settings for the package).
    Returns a dictionary with keys - library or tool names and values -
    None (if these libraries or tools are not found) or other non-None value
    if they are present.
    """
    result = {  'pyexiv2': None,
                'ffprobe': None
             }
    try:
        import pyexiv2
        pyexiv2_ver = 'pyexiv2: ' + str(pyexiv2.__version__)
        result['pyexiv2'] = pyexiv2_ver
    except ImportError:
        pass

    result['ffprobe'] = find_executable('ffprobe')

    return result


# -----------------------------------------------
# Calculating file's checksum
def checksum_data(data, algorithm='sha256'):
    """
    Calculates checksum of the block of data using the various algorithms
    provided by the Python's standard :mod:`hashlib` module.
    *algorithm* should be one of the available in :attr:`hashlib.algorithms`
    or :exc:`GeneralException` will be raised.

.. seealso:: Module :mod:`hashlib`

       Documentation of the :mod:`hashlib` module in Python's standard library.

    """
    if not algorithm in hashlib.algorithms:
        errmsg = "Unknown algorithm requested '" +algorithm + "'." + \
                 "Valid algorithms are : " + str(hashlib.algorithms)
        raise GeneralException(errmsg)
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


# -----------------------------------------------
def checksum_file(fpath,
                  algorithm='sha256',  # check hashlib.algorithms for more
                  block_size=4194304): # 4 * 1024 * 1024 = 4MB
    """
    Calculates checksum of the file using the various algorithms provided
    by the Python's standard :mod:`hashlib` module.

    *fpath* is the absolute path to the file.
    *algorithm* should be one of the available in :attr:`hashlib.algorithms`
    or :exc:`GeneralException` will be raised.
    *block_size* is the amount of data read from the file at once.

.. seealso:: Module :mod:`hashlib`

       Documentation of the :mod:`hashlib` module in Python's standard library.

    """
    if not algorithm in hashlib.algorithms:
        errmsg = "Unknown algorithm requested '" +algorithm + "'." + \
                 "Valid algorithms are : " + str(hashlib.algorithms)
        raise GeneralException(errmsg)

    hasher = hashlib.new(algorithm)
    with open(fpath,'rb') as afile:
        buf = afile.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(block_size)
    return hasher.hexdigest()


# -----------------------------------------------
def get_file_timestamp(filepath, mode="modified", localtime=True):
    """
    Returns the timestamp of a file as provided by the operating system.

    *filepath* is the full path to the file. *mode* should be *modified* or
    *created*.
    If *localtime* is *False* the the time stamp will be in in GMT,
    otherwise it will be converted to the local system's time.

    The function returns a string with date and time in the format
    "yyyy:mm:dd hh:mm:ss". It raises :exc:`GeneralException` if any error
    occurs.
    """
    # -- alternative implementation
    # see http://stackoverflow.com/questions/237079/
    #import os
    #import datetime
    #def modification_date(filename):
    #    t = os.path.getmtime(filename) # modification time
    #    t = os.path.getctime(filename) # creation time
    #    return datetime.datetime.fromtimestamp(t)

    if mode == "modified":
        ftimestamp = os.stat(filepath)[stat.ST_MTIME]
    elif mode == "created":
        ftimestamp = os.stat(filepath)[stat.ST_CTIME]
    else:
        raise GeneralException("Unknown 'mode' provided: '" + str(mode) + \
                        ". Valid values are 'created' and 'modified'.")

    if localtime:
        ts = time.localtime(ftimestamp)
    else:
        ts = time.gmtime(ftimestamp)

    result = datetime.datetime(ts.tm_year, ts.tm_mon, ts.tm_mday,
                               ts.tm_hour, ts.tm_min, ts.tm_sec)

    return result


# -----------------------------------------------
def get_file_size(fpath):
    """
    Returns the file size (in bytes).
    """
    return os.path.getsize(fpath)


# -----------------------------------------------
def escape_file_name(fname):
    """
    Helper function to safely convert the file name (a.k.a. escaping) with
    spaces which can cause issues when passing over to the command line.
    """
    result = fname.replace('\"', '\\"') # escapes double quotes first
    result = ['"',result,'"']
    return "".join(result)


# -----------------------------------------------
def is_executable(fname_abs):
    """
    Checks if the given file name is a regular file and if it is an
    executable by the current user.
    """
    result = False
    if os.path.isfile(fname_abs) and os.access(fname_abs, os.X_OK):
        result = True
    return result


# -----------------------------------------------
def find_executable(executable, path=None):
    # cross-platofrm way to find executable
    # inspired by http://snippets.dzone.com/posts/show/6313
    # and
    # http://stackoverflow.com/questions/377017/
    """
    Attempts to find executable file in the directories listed in 'path' (a
    string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH']).
    Returns the complete filename or None if no such file is found.
    """

    if path is None:
        path = os.environ['PATH']

    paths = path.split(os.pathsep)
    extlist = ['']
    if sys.platform == 'win32':
        # checks if the provided executable file name has an extension
        # and if not - then search for all possible extensions
        # in order as defined by the 'PATHEXT' environmental variable
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext

    result = None
    for ext in extlist:
        execname = executable + ext
        abs_execname = os.path.abspath(execname)
        # checks if the file exists, is a normal file and can be executed
        if is_executable(abs_execname):
            result = abs_execname
            break
        else:
            for p in paths:
                f = os.path.join(p, execname)
                abs_f = os.path.abspath(f)
                if is_executable(abs_f):
                    result = abs_f
                    break

    return result


# -----------------------------------------------
def get_as_number_if_possible(arg):
    """
    Tries to identify if the argument is a number (Rational, Number, Fraction
    or integer/float in a string) and then return it either as integer or
    float. If the conversion is not successful, then it returns the argument
    as it is.
    """
    result = arg
    if isinstance(arg, numbers.Number):
        # 'arg' is already a number - return it as it is
        # TODO: check if it is a numbers.Fraction and if the denominator == 1
        # then return the numerator part only
        pass # result = arg
    else:
        sarg = str(arg).lower()
        if sarg.count('.') == 1 or sarg.count('e') == 1:
            # looks like a float, let's try to convert it to float then
            try:
                result = float(arg)
            except ValueError:
                # apparently it is not a float - return it as it is
                result = arg
        elif sarg.isdigit():
            # try to convert it to an integer (using 10 as base)
            try:
                result = int(arg)
            except ValueError:
                # apparently it is not an int (or may be not in base 10) so
                # just return the original argument as it is
                result = arg
        else:
            # then it must be something else - return the original value
            result = arg

    return result


# -----------------------------------------------
class EnhancedDict(OrderedDict):
    """
    This class adds some handy and often used methods to the standard
    OrderedDict() class.
    """
    
    def to_json(self, *args, **kwargs):
        """
        Converts the dictionary into JSON format. Any arguments provided are
        passed to :func:`json.dumps`.
        """
        result = json.dumps(self, *args, **kwargs)
        return result


# -----------------------------------------------
def flatten_tree_dict(tree_dict, sep=u'.'):
    """
    Converts tree/nested dictionary into one a flat one where the keys
    are represented in a file path-like structure. By default the
    separator is a dot, but can be changed by providing new one with the
    *sep* argument.
    
    :param tree_dict: a dictionary that will be converted
        
    :param sep: a string used to separate the nested keys (branches and
        leaves) of the dictionary.
    
    :returns: new dictionary (instance of :class:`EnhancedDict`) where the
        tree-like dictionary has been converted to flat one.
    
    .. note:: 
        
       The branches of the provided tree dictionary must be convertable to
       regular strings.

    Example::

        >>> d = EnhancedDict()
        >>> d['answer'] = 42
        >>> d['a'] = {'b':{'c':4.2}}
        >>> print(d.to_json(indent=2))
        {
          "answer": 42, 
          "a": {
            "b": {
              "c": 4.2
            }
          }
        }
        >>> print(flatten_tree_dict(d).to_json(indent=2))
        {
          "answer": 42, 
          "a.b.c": 4.2
        }

    """
    
    result = EnhancedDict()
    stack = list()

    root = (None, tree_dict) # create tuple (parentkey, dict)
    stack.append(root)

    while len(stack) > 0:
        parentkey, subdict = stack.pop()
        for key in subdict:
            element = subdict[key]
            strkey = unicode(key) # should be converted to str() for Python 3.x
            newkey = strkey if parentkey is None else \
                     u''.join([parentkey, sep, strkey])
            if not isinstance(element, types.DictionaryType):
                result[newkey] = element
            else:
                branch = (newkey, element) # create tuple (parentkey, dict)
                stack.append(branch)
    
    return result


# -----------------------------------------------
class TreeDict(EnhancedDict):
    """
    This class allows the ability to easily create tree-like (nested)
    dictionaries.
    """

    def add_node(self, sep_key, val, sep=u'.'):
        """
        Adds a "leaf" node to the dictionary tree where the key specifies
        where to put the node by using file path-like key.
        
        Example::

            >>> t = TreeDict()
            >>> t.add_node('a.b.c',3)
            >>> print(t.to_json(indent=2))
            {
              "a": {
                "b": {
                  "c": 3
                }
              }
            }
            >>> t.add_node('answer',42)
            >>> print(t.to_json(indent=2))
            {
              "a": {
                "b": {
                  "c": 3
                }
              }, 
              "answer": 42
            }
            >>> t.add_node('answer/to/everything',42, sep=u'/')
            >>> print(t.to_json(indent=2))
            {
              "a": {
                "b": {
                  "c": 3
                }
              }, 
              "answer": {
                "to": {
                  "everything": 42
                }, 
                "42": null # the previous value is now a key in dict with value=None 
              }
            }

        """

        split_keys = sep_key.split(sep)
        last_key = split_keys.pop() # extract the last element

        current_dict = self
        for key in split_keys:
            sub_element = current_dict.get(key,{})
            
            # check if the sub_element is a dictionary and ifit isn't then
            # convert it to one. This logic also prevents overwriting existing
            # leaves with sub-dictionary as the leaf is also converted to a
            # dictionary key with value set to None
            if not isinstance(sub_element, dict):
                sub_element = {sub_element : None}

            current_dict[key] = sub_element
            current_dict = sub_element
        current_dict[last_key] = val


    def to_flatten(self, sep='.'):
        """
        Convenience method for invoking :func:`flatten_tree_dict`.
        
        Example::

            >>> print(t.to_json(indent=2)) # assume the dictionary has already been populated
            {
              "a": {
                "b": {
                  "c": 3
                }
              }, 
              "answer": {
                "to": {
                  "everything": 42
                }, 
                "42": null
              }
            }
            >>> print(t.to_flatten().to_json(indent=2))
            {
              "answer.42": null, 
              "answer.to.everything": 42, 
              "a.b.c": 3
            }

        """
        result = flatten_tree_dict(self, sep=sep)
        return result
