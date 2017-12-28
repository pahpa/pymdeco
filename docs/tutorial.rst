
Tutorial
========

Assuming that all external dependencies have been satisfied (see Installation
section for details) the easiest way to use the library is to instantiate 
a service from :mod:`pymdeco.services` module:

Example::

    >>> import os
    >>> from pymdeco.services import FileMetadataService
    >>> srv = FileMetadataService()
    >>> for root, dirs, files in os.walk(r'/tests/'):
    ...    for afile in files:
    ...        meta = srv.get_metadata(os.path.join(root,afile))
    ...        print(meta.to_json(indent=2))
    ... 
    # long prinout of metadata in nested dictionaries
        

In PyMDECO, there is a separation between the various components for
extracting metadata:

* *Extractors* - The low-level functions which call the third-party libraries
  or invoke the external executable programs and parse their output. These
  functions expect the third-party libraries and tool to be present on the
  system, otherwise they won't work.

* *Scanners* - Mid-level classes which can perform additional checks during
  the initializations and identify, load and check for the external
  dependencies and/or provide alternatives if they are not present.
  Scanners usually specialize in the extraction of only certain type of
  files i.e. only in audio or only in image metadata extraction.

* *Services* - High-level classes which can combine multiple scanners to allow
  scanning of different types files. They also provide fall-back method if
  some of the scanners can not work due to missing dependencies.

Each of these class of components sit in their own module. There is a clear
separation of the of their duties and the components from a module only know
and use the classes from the lower layers i.e.:
*Services only use Scanners. Scanners only use Extractors.*

Each Service and Scanner use the file's MIME
(`Multipurpose Internet Mail Extensions <http://en.wikipedia.org/wiki/MIME>`_)
to identify what kind of data it is likely to contain and then runs the
appropriate function to get the metadata.

The Services are the most convenient way to extract data as they know which
Scanner to use for particular file type. However, sometimes the library user
may wish to exert more control over which Scanner class is used, so it is
possible to construct the service manually:

Example::

    >>> from pymdeco import scanners, services
    >>> ais = scanners.AudioInfoScanner() # using the default MIME 'audio/*'
    >>> ais.pre_checks() # see API documentation for details
    >>> srv = services.FileMetadataService(scanners_list=[ais]) # using the default scanner for */*
    >>> srv.available_scanners()
    {'*/*': <pymdeco.scanners.FileInfoScanner object at 0x02A76A30>, \
    'audio/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>}
    >>> vis = scanners.VideoInfoScanner()
    >>> vis.pre_checks()
    >>> srv.register_scanner("video/mpeg", vis) # registering with specific MIME
    >>> srv.available_scanners()
    {'video/mpeg': <pymdeco.scanners.VideoInfoScanner object at 0x02A76A90>, \
    '*/*': <pymdeco.scanners.FileInfoScanner object at 0x02A76A30>, \
    'audio/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>}
    >>> srv.set_default_scanner(ais)
    >>> srv.available_scanners()
    {'video/mpeg': <pymdeco.scanners.VideoInfoScanner object at 0x02A76A90>, \
    '*/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>, \
    'audio/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>}
    >>> meta = srv.get_metadata('/some/video/file.mpeg')
    >>> # do something with the metadata

Regardless of which method has been used to obtain the metadata, the
result is always a (nested) Python dictionary with keys - undescore separated
meaningfull descriptions of the metadata tag and values - either strings or
numbers.
The result can then easily be converted to JSON for transmission via HTTP or
stored to document-oriented database (like
`MongoDB <http://www.mongodb.org/>`_).

