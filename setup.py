# -*- coding: utf-8 -*-
#
# Author: Todor Bukov
# License: LGPL version 3.0 - see LICENSE.txt for details
#
"""
Setup script for PyMDECO library.
"""

from __future__ import print_function
import os
import sys
import glob
import shutil
import runpy
from distutils.core import setup
from distutils.core import Command
from distutils.command.build import build
from sphinx import setup_command

if sys.platform.startswith('win'):
    try:
        import py2exe
    except ImportError:
        print('WARNING: No py2exe module installed!')

# ---
def remove_dir(dirname):
    removed = False
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
        removed = True
    return removed


# ---
def remove_file(afile):
    removed = False
    if os.path.exists(afile):
        os.remove(afile)
        removed = True
    return removed


# ---
def find_files(path, file_pattern):
    """
    Returns a list with file names under the provided *path* and its
    that sub directories if the file names match the provided *file_pattern*.
    """
    result = []
    for root, dirs, files in os.walk(path):
        pattern = os.path.join(root,file_pattern)
        filelist = glob.glob(pattern)
        for f in filelist:
            if (not f in result) and (os.path.isfile(f)):
                result.append(f)
    return result


# ---
def find_subdirs(path):
    """Returns a sorted list of subdirectories (childs before parents)."""
    result = set()
    for root, dirs, files in os.walk(path):
        abs_dirs = [os.path.join(root,adir) for adir in dirs]
        result = result.union(set(abs_dirs))
    result = list(result) # convert to list to allow sorting
    # now sort by the length of the dirs (longer paths first)
    # (parent dir's paths are shorter than children's ones)
    result.sort()
    result.reverse()
    return result


# ---
def get_subpackages(name):
    """Return subpackages of package *name*"""
    splist = []
    for dirpath, _dirnames, _filenames in os.walk(name):
        if os.path.isfile(os.path.join(dirpath, '__init__.py')):
            splist.append(".".join(dirpath.split(os.sep)))
    return splist


# ---
def read_txt_file(fname):
    """Read thw whole text file and returns it as a string"""
    result = ''
    with open(fname) as filevar:
        result = filevar.read()
    return result


# ---
class CleanCommand(Command):
    description = "cleans temporary files and build/dist directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' %self.cwd
        print("Script directory:", SETUP_DIR)

        print ("Removing ./build and ./dist directories")
        build_dir = os.path.join(os.getcwd(),'build')
        dist_dir = os.path.join(os.getcwd(),'dist')
        print ("  deleting ./buildir: ",build_dir)
        remove_dir(build_dir)
        print ("  deleting ./dist: ",dist_dir)
        remove_dir(dist_dir)

        print ("Removing .pyc and .pyo compiled files")
        pyc_files = find_files(SETUP_DIR,"*.pyc")
        pyo_files = find_files(SETUP_DIR,"*.pyo")
        filelist = pyc_files + pyo_files
        for f in filelist:
            print ('  deleting:',f)
            os.remove(f)

        docs_build_dir = os.path.join(os.getcwd(),'docs/build')
        if os.path.exists(docs_build_dir):
            print("Clearing docs/build directory")
            docs_build_dir = os.path.join(os.getcwd(),'docs/build')
            print ("  deleting docs/buildir: ",docs_build_dir)
            remove_dir(docs_build_dir)

#        print("Removing .exe files")
#        exe_files = find_files(SETUP_DIR,"*.exe")
#        for f in exe_files:
#            print ('  deleting:',f)
#            os.remove(f)

        print("Cleaning complete.")
        print("Done.")


# ---
# Sphinx build (documentation)
class MyBuild(build):
    def has_doc(self):
        return os.path.isdir(os.path.join(SETUP_DIR, 'docs'))
    sub_commands = build.sub_commands + [('build_doc', has_doc)]


class MyBuildDoc(setup_command.BuildDoc):
    def run(self):
        build = self.get_finalized_command('build')
        sys.path.insert(0, os.path.abspath(build.build_lib))
        dirname = self.distribution.get_command_obj('build').build_purelib
        self.builder_target_dir = os.path.join(dirname, LIB_NAME, 'docs')
        try:
            setup_command.BuildDoc.run(self)
        except UnicodeDecodeError:
            msg = "ERROR: unable to build documentation because Sphinx " + \
                  "do not handle source path with non-ASCII characters. " + \
                  "Please try to move the source package to another " + \
                  "location (path with *only* ASCII characters)."
            print(msg, file=sys.stdout)
        sys.path.pop(0)


# ---
SCRIPT_NAME = 'metadump'
LIB_NAME = 'pymdeco'

SETUP_PATH = os.path.realpath(__file__)
SETUP_DIR = os.path.dirname(SETUP_PATH)

lib_init_py = os.path.join(SETUP_DIR, LIB_NAME, "__init__.py")
LIB_INIT_VARS = runpy.run_path(lib_init_py)

LONG_DESCRIPTON = read_txt_file('README.txt')


setup(
    name= LIB_NAME,
    version = LIB_INIT_VARS['__version__'],
    author = 'Todor Bukov',
    author_email = 'dev.todor@gmail.com',
    url = 'https://bitbucket.org/todor/pymdeco/',
#    download_url = 'https://bitbucket.org/todor/pymdeco/',
    description =
    'PyMDECO - Python Meta Data Extractor and Collection Organizer library',
    long_description = LONG_DESCRIPTON,
    license = "GNU Lesser General Public License version 3 or later(LGPLv3)",
    classifiers =
        [
        # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Multimedia',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    platforms=['any'],
    packages = get_subpackages(LIB_NAME),
    options = {'py2exe': {
                           'bundle_files': 1
                        }
              },
    console = [SCRIPT_NAME + ".py"],
    zipfile = None,
    requires=["pyexiv2 (>=0.3.0)", "sphinx (>=1.0.0)"],
    cmdclass={
        'clean': CleanCommand,
        'build': MyBuild,
        'build_doc': MyBuildDoc
    },
)
