# -*- coding: utf-8 -*-
#
# Author: Todor Bukov
# License: LGPL version 3.0 - see LICENSE.txt for details
#
"""
:mod:`services` - High-level metadata collectors
========================================================

.. module:: pymdeco.services
   :platform: Unix, Windows
   :synopsis: Provides high-level classes for extracting file metadata.
.. moduleauthor:: Todor Bukov

Services act like "registry" and are high-level constructs that use "scanners"
(i.e. instances of :class:`pymdeco.scanners.Scanner` or its sublasses) to
interrogates files and extract the metadata. Unlike scanners, which are
designed to inspect only a specific type of files like "images" or "videos",
a service can implement logic to determine what the type of file is and then
use the appropriate scanner to extract the metadata.

Services use the MIME
(`Multipurpose Internet Mail Extensions <http://en.wikipedia.org/wiki/MIME>`_)
of the file to determine their type - audio, video, image, text or binary.
Currently the MIME type is determined by the file extension, but future
versions may include more sophisticated methods like
`file signatures <http://en.wikipedia.org/wiki/List_of_file_signatures>`_.

Example usage:

    >>> import os
    >>> from pymdeco.services import FileMetadataService
    >>> srv = FileMetadataService()
    >>> for root, dirs, files in os.walk(r'/tests/'):
    ...    for afile in files:
    ...        meta = srv.get_metadata(os.path.join(root,afile))
    ...        print(meta.to_json(indent=2))
    ... 
    # long prinout of metadata in nested dictionaries

"""
from pymdeco.extractors import guess_file_mime
from pymdeco.scanners import FileInfoScanner, ImageInfoScanner
from pymdeco.scanners import AudioInfoScanner, VideoInfoScanner
from pymdeco.exceptions import GeneralException, ServiceException


# ----
class BaseScanService(object):
    """
    Base class for all services using scanners.
    """
    def __init__(self, default_scanner=None):
        self._scanners_registry = {}
        self._default_scanner = default_scanner


    def register_scanner(self, mime, scanner, overwrite=False):
        """
        Adds instance of :class:`pymdeco.scanners.Scanner` and associate it
        with given MIME type. Rises :exc:`GeneralException`
        or :exc:`MissingDependencyException` when the
        :meth:`pymdeco.scanners.Scanner.pre_checks` method fails.
        """
        if (not overwrite) and (mime in self._scanners_registry):
            errmsg = "MIME type '" + mime + "' already registered."
            raise ServiceException(errmsg)
        else:
            self._scanners_registry[mime] = scanner

        try:
            scanner.pre_checks()
        except GeneralException:
            # TODO: do something here
            raise


    def set_default_scanner(self, scanner):
        """
        Sets default instance of :class:`pymdeco.scanners.Scanner` in the scan
        service registry.
        """

        self.register_scanner('*/*', scanner, overwrite=True)
        self._default_scanner = scanner



    def guess_file_mime(self, fpath):
        """
        Convenience function, alias for
        :func:`pymdeco.extractors.guess_file_mime`
        """
        return guess_file_mime(fpath)


    def get_scanner_by_mime(self, mime):
        """
        Returns the appropirate scanner registered for the given MIME type. If
        the MIME type has not been registered before, the default scanner is
        returned (which may be None).
        """
        lookup_mime = mime

        # the default to handle the default case when all other checks fail
        result = self._default_scanner

        # handles None value
        if lookup_mime is None:
            result = self._default_scanner

        # handles 'mimetype/subtype' already in the registry
        elif lookup_mime in self._scanners_registry:
            result = self._scanners_registry[lookup_mime]

        # handles the case when 'mimetype/subtype' not in registry
        # but 'mimetype/*' is
        elif lookup_mime.find('/') > 0:
            # transform 'mimetype/subtype' to 'mimetype/*'
            # and try again
            lookup_mime = lookup_mime.split('/')[0] + '/*'

            if lookup_mime in self._scanners_registry:
                result = self._scanners_registry[lookup_mime]
            else:
                # handles the case whan there is Scanner class that registerd
                # '*/*' mime type in the registry
                lookup_mime = '*/*'
                if lookup_mime in self._scanners_registry:
                    result = self._scanners_registry[lookup_mime]
        return result


    def get_metadata(self, fpath):
        """
        Identifies the MIME type of the file path, then finds the
        appropriate scanner in the registry and use it to obtain the metadata
        from the file.

        This method may raise :exc:`ServiceException` if no appropriate MIME
        scanner has been found in the registry (and when no default scanner
        is registered either).
        It can also re-raises :exc:`GeneralException` from the scanner itself.
        """

#        if not os.path.isfile(fpath):
#            errmsg = 'Path not found or is not a file.'
#            raise ServiceException(errmsg)

        result = {}

        mime = self.guess_file_mime(fpath)
        scanner = self.get_scanner_by_mime(mime)

        if scanner is None:
            errmsg = "No scanner available for this file/MIME type."
            raise ServiceException(errmsg)
        try:
            result = scanner.scan(fpath)
        except GeneralException:
            # TODO: do something sane here
            raise

        return result


    def available_scanners(self):
        """
        Returns a dictionary with keys - MIME types and values - instances of
        the registered scanners.
        """
        return self._scanners_registry


# ----
class FileMetadataService(BaseScanService):
    """
    Accepts optional list with scanners objects and a default scanner
    and register them all with their preferred MIME types (as defined in
    :attr:`Scanner.mime_types` attribute.) If no *default_scanner* is
    provided, then :class:`FileInfoScanner` is used. If *scanners_list* is
    None or empty list, then the default set of scanners is used as listed in
    :attr:`default_scanners_list`.

    Raises :exc:`ServiceException` if there is a problem with registering
    the scanners or :exc:`GeneralException` if one is raised by the
    scanners themselves.
    """

    _default_scanners_list = [FileInfoScanner, ImageInfoScanner,
                              AudioInfoScanner, VideoInfoScanner
                             ]

    def __init__(self,
                 scanners_list = None,
                 default_scanner = None):
        super(FileMetadataService, self).__init__()


        if default_scanner is None:
            default_scanner = FileInfoScanner()
        default_scanner.pre_checks()
        self.set_default_scanner(default_scanner)

        if (scanners_list is None) or len(scanners_list) == 0:
            scanners_objects = []
            for scanner_class in self._default_scanners_list:
                scanner_instance = scanner_class()
                scanners_objects.append(scanner_instance)
        else:
            scanners_objects = scanners_list

        for scanner in scanners_objects:
            try:
                scanner.pre_checks()
                for mime in scanner.mime_types:
                    self.register_scanner(mime, scanner, overwrite=True)
            except GeneralException:
                # TODO: do something sane here
                raise

            except ServiceException:
                # TODO: do something sane here
                raise

