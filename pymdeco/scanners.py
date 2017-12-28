# -*- coding: utf-8 -*-
#
# Author: Todor Bukov
# License: LGPL version 3.0 - see LICENSE.txt for details
#
"""

:mod:`scanners` - Stateful classes for scanning and extracting metadata
=======================================================================

.. module:: pymdeco.scanners
   :platform: Unix, Windows
   :synopsis: Provides statefull classes for extracting file metadata.
.. moduleauthor:: Todor Bukov

Scanner are classes that call libraries or execute external utilities to
collect file metadata and convert it to a regular Python dictionary.

The :class:`Scanner` class and it descendants has method :meth:`pre_checks`
which should be executed prior using the scanner. This method should perform
the initialization of the external libraries, search for the location of the
executable files and everything else required to prepare for the metadata
extraction.

Example usage (the output has been truncated for brievety)::

    >>> from pymdeco import scanners
    >>> vis = scanners.VideoInfoScanner()
    >>> meta = vis.scan('/tests/big_buck_bunny_720p_surround.avi')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pymdeco/scanners.py", line 183, in scan
        raise GeneralException(err)
    pymdeco.exceptions.GeneralException: Pre checks have not passed. Run pre_checks() method first.
    >>> vis.pre_checks()
    >>> meta = vis.scan('/tests/big_buck_bunny_720p_surround.avi')
    >>> print(meta.to_json(indent=2))
    {
      "file_name": "big_buck_bunny_720p_surround.avi", 
      "file_type": "video", 
      "file_size": 332243668, 
      "mime_type": "video/x-msvideo", 
      "file_hash": {
        "value": "b957d6e6212638441b52d3b620af157cc8d40c2a0342669294854a06edcd528c", 
        "algorithm": "sha256"
      }, 
      "file_timestamps": {
        "modified": "2008-06-11 13:29:26", 
        "created": "2008-06-11 13:29:26"
      }, 
      "video_metadata": {
        "streams": [
          {
            "sample_aspect_ratio": "1:1", 
            "codec_type": "video", 
            "codec_name": "mpeg4", 
            "duration": "596.457", 
            "nb_frames": "14315", 
    # ... output truncated
    

.. note::

   :class:`Scanner` and its subclasses have :attr:`Scanner.mime_types`
   class attribute which shows the type of files the scanner recognizes and
   which the :meth:`Scanner.scan` should be invoked for.
   Although the scanner can be invoked for other type of files, the output
   result is not guaranteed to be completed or make sense at all. In this case
   the output depends on the external library or utility used which may or may
   not produce sensible results.

   Refer to :mod:`pymdeco.services` for classes which offer additional
   logic and allow extracting metadata from arbitrary type of files.

.. seealso:: Module :mod:`pymdeco.services`

       Documentation of the :mod:`pymdeco.services` services module.

"""
from __future__ import print_function
import os
import mimetypes
#
from pymdeco.utils import checksum_file, get_file_timestamp, find_executable
from pymdeco.utils import TreeDict
from pymdeco.extractors import get_image_metadata, guess_file_mime
from pymdeco.extractors import get_multimedia_metadata
from pymdeco.exceptions import GeneralException, MissingDependencyException


DEFAULT_MIME_TYPE = 'application/octet-stream'


# ---
class Scanner(object):
    """
    TODO:
    """
    mime_types = ['unknown']

    def __init__(self):
        self._methods = list()
        self._pre_checks_passed = False
#        self.pre_checks()

    def pre_checks(self):
        """
        This method can include necessary pre-checks and initialization code
        that needs to be run after the initialization , but before the actual
        usage of the instance. The method can be called a number of times
        either by other methods in the subclasses or by pther classes or
        applications.

        If all checks are successfully, subclasses should call
        :meth:`_pre_checks_pass` otherwise they should raise
        :exc:`MissingDependencyException` (or call :meth:`_pre_checks_fail`
        method which will do it for them).
        """
        self._pre_checks_pass()


    def _pre_checks_pass(self):
        """
        Subclasses should call this method when all checks for external
        dependancies have passed successfully.
        """
        self._pre_checks_passed = True


    def _pre_checks_fail(self, error_message):
        """
        Subclasses should call this method when any of the checks for external
        dependancies have failed. Alternatively
        :exc:`MissingDependencyException` can be raised.
        """
        raise MissingDependencyException(error_message)


    def _register(self, meth, description = None):
        """
        Subclasses will use this method to register callback functions which
        will be called when :meth:`scan` method is invoked on a file.
        """
        desc = description
        if desc is None:
            desc = str(meth)

        if callable(meth) and hasattr(meth, 'im_class') and \
           isinstance(self, meth.im_class):
               self._methods.append((meth, desc))
        else:
            msg =   'Argument not callable, not method class or ' + \
                    'does not belong to an instance.'
            raise GeneralException(msg)

    # -- public methods and properties
    def scan(self, fpath):
        """
        Walks through the registered methods, runs them with a single argument
        and then assigns the result to a dictionary and returns it.
        Returns :exc:`GeneralException` if *fpath* is not a valid or if the
        :meth:`pre_checks` method has not been run before.
        """
        if not self._pre_checks_passed:
            err = "Pre checks have not passed. Run pre_checks() method first."
            raise GeneralException(err)

        if not os.path.isfile(fpath):
            errmsg = 'Path not found or is not a file: ' + fpath
            raise GeneralException(errmsg)

        results = TreeDict()

        for a_method, desc in self._methods:
            meth_result = a_method(fpath)
            results.update(meth_result)
        return results



# ----
class FileInfoScanner(Scanner):
    """
    This scanner collects metadata about the file from the operating system
    along with checksumming the content of the file.
    It can be safely used against any type of file and is always guaranteed to
    produce sensible results.
    """
    mime_types = ['*/*'] # this is "catch all" clause

    def __init__(self):
        super(FileInfoScanner, self).__init__()

        self._register(self._add_file_name)
        self._register(self._add_file_type)
        self._register(self._add_size)
        self._register(self._add_mime)
        self._register(self._add_hash)
        self._register(self._add_timestamps)


    def _add_file_name(self, fpath):
        fname = os.path.basename(fpath)

        result = dict(file_name = fname)
        return result


    def _add_hash(self, fpath,
                 algorithm='sha256',
                 block_size=4194304): # 4 * 1024 * 1024 = 4MB
        checksum = checksum_file(fpath,
                                 block_size=block_size,
                                 algorithm=algorithm)
        temp_dict = {}
        temp_dict['algorithm'] = algorithm
        temp_dict['value'] = checksum

        result = dict(file_hash = temp_dict)
        return result


    def _add_timestamps(self, fpath, localtime=True):
        modtime = get_file_timestamp(fpath,
                                     mode='modified',
                                     localtime=localtime)
        crtime = get_file_timestamp(fpath,
                                    mode='created',
                                    localtime=localtime)

        temp_dict = {}
        temp_dict['modified'] = '{:%Y-%m-%d %H:%M:%S}'.format(modtime)
        temp_dict['created'] = '{:%Y-%m-%d %H:%M:%S}'.format(crtime)

        result = dict(file_timestamps = temp_dict)
        return result


    def _add_size(self, fpath):
        fsize = os.path.getsize(fpath)

        result = dict(file_size = fsize)
        return result


    def _add_mime(self, fpath):
        mt = guess_file_mime(fpath)
        if mt is None:
            mt = DEFAULT_MIME_TYPE # unknown type

        result = dict(mime_type = mt)
        return result


    def _add_file_type(self, fpath):
        mime = mimetypes.guess_type(fpath)[0]
        tp = 'unknown'
        try:
            if not (mime is None):
                tp = mime.split('/')[0]
        except:
            pass

        result = dict(file_type = tp)
        return result


# ----
class ImageInfoScanner(FileInfoScanner):
    """
    Scanner for extracting
    `EXIF <http://en.wikipedia.org/wiki/Exchangeable_image_file_format>`_,
    `XMP <http://en.wikipedia.org/wiki/Extensible_Metadata_Platform>`_ and
    `IPTC <http://en.wikipedia.org/wiki/Extensible_Metadata_Platform>`_
    metadata from image formats (JPEG, PNG, GIF, etc).

    This class currently uses `exiv2 <http://exiv2.org/>`_  and its Python
    bindings `pyxeiv2 <http://tilloy.net/dev/pyexiv2/>`_.
    """

    mime_types = ['image/*']

    def __init__(self, fractions_as_float=False):
        self._pyexiv2_version = None
        self._fractions_as_float = fractions_as_float
        super(ImageInfoScanner, self).__init__()
        self._register(self._add_image_metadata)


    def pre_checks(self):
        """
        see :meth:`Scanner.pre_checks`
        """
        try:
            import pyexiv2
            self._pyexiv2_version = pyexiv2.__version__
            self._pre_checks_pass()
        except ImportError:
            msg = "pyexiv2 library not installed! " + \
            "Image metadata extracting is not possible."
            raise MissingDependencyException(msg)


    def _add_image_metadata(self, fpath):
        temp_dict = get_image_metadata(
                        fpath,
                        fractions_as_float=self._fractions_as_float
                    )

        # Use :class:`TreeDict` to return tree-like dictionary instead of
        # dot-separated attributes i.e.
        # {"Exif" : {"Image": "Make": {"SomeMaker"}}}
        # instead of
        # "Exif.Image.Make" : "SomeMaker"
        # The benefit is that MongoDB makes better use of tree-like/nested
        # dictionaries

        # pyexiv2 returns the keys in dotted format i.e. "Exif.key.subkey"
        # Use TreeDict to convert them to tree-like/nested dictionaries
        tree = TreeDict()
        for key in temp_dict:
            # TODO: make sure the key and values are string or can be converted
            # *safely* to a string values
            tree.add_node(key, temp_dict[key])

        result = dict(image_metadata = tree)
        return result


# ---
class VideoInfoScanner(FileInfoScanner):
    """
    Scanner for extracting metadata from video files.
    Currently depends on having the :program:`ffprobe` binary (from
    `ffmpeg suite <http://ffmpeg.org/>`_) located in the system's PATH
    environment variable.
    """
    mime_types = ['video/*']

    def __init__(self):
        self._ffprobe_path = None
        super(VideoInfoScanner, self).__init__()
        self._register(self._add_video_metadata)


    def pre_checks(self):
        """
        see :meth:`Scanner.pre_checks`
        """
        ffprobe_path = find_executable('ffprobe')
        if ffprobe_path is None:
            msg = "Cannot find 'ffprobe' executable (in PATH)."
            raise MissingDependencyException(msg)
        self._ffprobe_path = ffprobe_path
        self._pre_checks_pass()


    def _add_video_metadata(self, fpath):
        temp_dict = get_multimedia_metadata(fpath, self._ffprobe_path)

        result = dict(video_metadata = temp_dict)
        return result

# ----
class AudioInfoScanner(FileInfoScanner):
    """
    Scanner for extracting metadata from audio files.
    Currently depends on having the :program:`ffprobe` binary (from
    `ffmpeg suite <http://ffmpeg.org/>`_) located in the system's PATH
    environment variable.
    """
    mime_types = ['audio/*']

    def __init__(self):
        self._ffprobe_path = None
        super(AudioInfoScanner, self).__init__()
        self._register(self._add_audio_metadata)

    def pre_checks(self):
        """
        see :meth:`Scanner.pre_checks`
        """
        ffprobe_path = find_executable('ffprobe')
        if ffprobe_path is None:
            msg = "Cannot find 'ffprobe' executable (in PATH)."
            raise MissingDependencyException(msg)
        self._ffprobe_path = ffprobe_path
        self._pre_checks_pass()


    def _add_audio_metadata(self, fpath):
        temp_dict = get_multimedia_metadata(fpath, self._ffprobe_path)

        result = dict(audio_metadata = temp_dict)
        return result


# ----
# STILL EXPERIMENTAL
class FFprobeScanner(FileInfoScanner):
    """
    TODO: Still experimental!
    """
    mime_types = ['video/*',
                  'audio/*'
                 ]

    def __init__(self):
        self._ffprobe_path = None
        super(FFprobeScanner, self).__init__()
        self._register(self._add_multimedia_metadata)


    def pre_checks(self):
        ffprobe_path = find_executable('ffprobe')
        if ffprobe_path is None:
            msg = "Cannot find 'ffprobe' executable (in PATH)."
            raise MissingDependencyException(msg)
        self._ffprobe_path = ffprobe_path
        self._pre_checks_pass()


    def _add_multimedia_metadata(self, fpath):
        temp_dict = get_multimedia_metadata(fpath, self._ffprobe_path)

        content_mime = guess_file_mime(fpath).split('/')[0]
        if content_mime.startswith('video'):
            result = dict(video_metadata = temp_dict)
        elif content_mime.startswith('audio'):
            result = dict(audio_metadata = temp_dict)
        return result


# ----
class TextInfoScanner(FileInfoScanner):
    """
    TODO:
    """
    mime_types = ['text/*']

# ----

