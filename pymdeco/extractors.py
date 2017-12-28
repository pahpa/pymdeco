# -*- coding: utf-8 -*-
#
# Author: Todor Bukov
# License: LGPL version 3.0 - see LICENSE.txt for details
#
"""
:mod:`extractors` - Low-level functions for extracting metadata from files
==========================================================================

.. module:: pymdeco.extractors
   :platform: Unix, Windows
   :synopsis: Provides low-level functions for extracting file metadata.
.. moduleauthor:: Todor Bukov


Extractors are various helper *functions* which refer to libraries or call 
external programs to extract files' metadata.

Unlike :mod:`pymdeco.scanners` or :mod:`pymdeco.services` the extractors are
not guaranteed to have stable API as they may depend on particular library
version, external tool or even the type or version of the operating systems 
(OS) itself.  
For these reasons it is recommended to use higher-level classes included in
:mod:`pymdeco.scanners` or :mod:`pymdeco.services`.

.. warning::
   
   The extractors' functions are not guaranteed to have a stable API and their
   use by applications is not recomended. Consider using 
   :mod:`pymdeco.scanners` or :mod:`pymdeco.services` modules instead.

.. seealso:: Module :mod:`pymdeco.scanners`

       Documentation of the :mod:`pymdeco.scanners` module.
   

.. seealso:: Module :mod:`pymdeco.services`

       Documentation of the :mod:`pymdeco.services` module.

"""
from __future__ import print_function
# internal Python modules
import os
import sys
import json
import subprocess
import numbers
import mimetypes

# package imports
from pymdeco.utils import EnhancedDict, escape_file_name
from pymdeco.exceptions import GeneralException

# external modules - must be installed separately
import pyexiv2


def get_image_metadata(fpath, fractions_as_float=False):
    """
    Uses `exiv2 <http://exiv2.org/>`_  and its Python
    bindings `pyxeiv2 <http://tilloy.net/dev/pyexiv2/>`_ library to extract
    the metadata from an image and return it as a dictionary.
    """
    metadata = pyexiv2.ImageMetadata(fpath)
    metadata.read()
    result = EnhancedDict()
    meta_keys = metadata.exif_keys + metadata.xmp_keys + metadata.iptc_keys
    # convert all keys to strings (some of them are plain python objects)
    for key in meta_keys:
        value = ''
        try:
            meta_val = metadata[key].value
            
            # TODO: handle the cases when the value is list of Fraction numbers
            # like the set of GPS coordinates

            if isinstance(meta_val, numbers.Rational):
                # if the denumerator is 1, then it is integer number
                if meta_val.denominator == 1:
                    value = meta_val.numerator
                elif fractions_as_float:
                    # calculate the result as a float value
                    value = meta_val.numerator / float(meta_val.denominator)
                else:
                # present the Rational and Fractions type as a string in
                # the form "x/y" 
                    value = str(meta_val.numerator) + "/" + \
                            str(meta_val.denominator)
            elif isinstance(meta_val, numbers.Number):
                # For any other type of numbers - just return the value
                value = meta_val
            else:
                # For other types (including binary), return utf-8 encoded 
                # string with escaped invalid/binary values
                try:
                    value = str(meta_val).encode("utf-8",
                                                  errors='backslashreplace')
                except ValueError:
                    # ok, must be a binary data, so just dump it as a hex
                    # string
                    value = '0x' + str(meta_val).encode('hex')
                    
        except pyexiv2.ExifValueError:
            # may happen if the format of the raw value is invalid according
            # to the EXIF specification 
            pass
        except NotImplementedError:
            # some keys cannot be currently converted by pyexiv2
            # so just ignore them
            pass
        except ValueError:
            # there may be some incorrect values in the EXIF/XMP, etc metadata.
            # Just ignore this error for now.
            pass
        except Exception:
            # TODO: to log this exception
            # DEBUG: print the error
#            print('No idea what went wrong, please report this error', ex)
            pass
        else:
            # if no exception has occured, then use the value
            result[key] = value
    # remove reference to ensure the original file won't be modified in any way
    del metadata
    return result


# -----------------------------------------------------------------------------
## Get video info by using ffprobe from ffpmeg package
## inspired by pipeffmpeg: https://github.com/kanryu/pipeffmpeg
## 
def get_multimedia_metadata(file_path, ffprobe_path):
    """
    Get the infomation about multimedia (audio, video or even some
    image formats) from :program:`ffprobe` command (part of 
    `ffmpeg <http://ffmpeg.org/>`_).
    
    Requires providing the path to the *ffprobe* external binary with
    permissions to execute it. It then parses the output and converts it to
    Python dictionary. Raises :exc:`ExtractorException` if it cannot find
    the :program:`ffprobe` binary or the output is not as expected.
    """
    
    if not os.path.isfile(ffprobe_path):
        errmsg = "Cannot find 'ffprobe' at: " + str(ffprobe_path)
        raise GeneralException(errmsg)

    # work around the issue with invoking the executable under Windows/Linux
    # Linux - shell must be True otherwise Popen can't find the file
    # Windows - shell must be False to avoid unnecessary invoking the command
    # shell
    use_shell = True
    if sys.platform.startswith('win'):
        use_shell = False

    escaped_fpath = escape_file_name(file_path)
    ffprobe_pipe = subprocess.Popen(
        " ".join([ffprobe_path,
                  '-print_format json',
                  '-show_format',
                  '-show_streams',
                  escaped_fpath]),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=use_shell
    )
    
    ffprobe_output = ffprobe_pipe.stdout.readlines()
    ffprobe_err = ffprobe_pipe.stderr.readlines()
    
    if ffprobe_output == []:
        err_msg = "".join(ffprobe_err)
        raise GeneralException("Error while invoking ffprobe:\n" + err_msg)
        
    ffprobe_json = []
    skip_line = True
    # cleanse any additional information that is not valid JSON
    for line in ffprobe_output:
        if line.strip() == '{':
            skip_line = False
        if not skip_line:
            ffprobe_json.append(line)
            
    result = json.loads("".join(ffprobe_json))
    return result


def guess_file_mime(fpath):
    """
    Tries to guess the MIME type of the file. Currently uses the file extension
    to identify the correct MIME.

.. todo::

   TODO: may enhance it in the future to use "magic numbers" or
   file content inspection to determine the correct MIME type.
    """
    mime_type = mimetypes.guess_type(fpath)[0]
    return mime_type
