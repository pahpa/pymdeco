#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyMDECO - Python Meta Data Extractor and Collection Organizer
Extract file metadata from a directory with files
"""

from __future__ import print_function
# internal Python modules
import os
import sys
import json
import argparse
#
from pymdeco.services import FileMetadataService
from pymdeco.exceptions import GeneralException


def main(arg=None):

    parser = argparse.ArgumentParser(
        description =
        'Crawl through directory tree and collects file metadata',
        epilog='author: Todor Bukov, dev.todor@gmail.com, ver.: ' + \
                os.path.basename(sys.argv[0])
)
    parser.add_argument(
        '-v','--verbose',
        action='store_true',
        help='Print verbose information'
        )

    parser.add_argument(
        '-p','--path',
        action='store',
        required=True,
        help='Starting point (directory path)'
        )

    if arg is None:
        arguments = parser.parse_args()
    else:
        arguments = parser.parse_args(arg)

    root_path = arguments.path
    scan_service = FileMetadataService() # use the defaults

#    print("Services:", scan_service.available_scanners())
    for root, dirs, files in os.walk(root_path):
        for afile in files:
            fpath = os.path.join(root, afile)
            print ("processing file:", fpath)
            try:
                finfo = scan_service.get_metadata(fpath)
            except GeneralException as ex:
                print("ERROR: Exception occured:\n" + str(ex))
            meta_json = json.dumps(finfo, ensure_ascii=False, indent=2)
            print ("Meta data (JSON):\n", meta_json)

if __name__ == '__main__':
    main()
