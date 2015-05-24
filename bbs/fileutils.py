#!/usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Jan 17, 2008
###
### fileutils module
###

import os
import sys
import re
import shutil
import string

# Equivalent to 'du -sb <path>'
# WARNING: Result will not be acurate on Windows when <path> is (or contains)
# a shortcut
def total_size(path):
    if os.path.islink(path):
        return os.lstat(path).st_size
    size = os.path.getsize(path)
    if os.path.isdir(path):
        for name in os.listdir(path):
            size += total_size(os.path.join(path, name))
    return size

def human_readable_size(size, htmlized=False):
    if size < 1024:
        if size == 1:
            unit = 'byte'
        else:
            unit = 'bytes'
        return '%s %s' % (size, unit)
    for unit in ['KiB', 'MiB', 'GiB']:
        size /= 1024.0
        if size < 1024:
            break
    if htmlized:
        unit = '<A href="http://en.wikipedia.org/wiki/%s" target="_blank">%s</A>' % (unit, unit)
    if size >= 1024:
        return '%.0f %s' % (size, unit)
    return '%.4g %s' % (size, unit)

# Dump an empty file.
def touch(file):
    f = open(file, 'w')
    f.close()
    return

### Replacement for shutil.rmtree() (needed because shutil.rmtree() fails on
### Windows if the tree contains stuff that is Read-only).
def nuke_tree(dir):
    if sys.platform == "win32":
        for path, subdirs, files in os.walk(dir):
            for file in files:
                filename = os.path.join(path, file)
                if not os.access(filename, os.W_OK):
                    os.chmod(filename, 0777)
    shutil.rmtree(dir)
    return

def remake_dir(path):
    if os.path.exists(path):
        nuke_tree(path)
    os.mkdir(path)
    return

# Return list of regular files in dir matching regex.
# Follows symlinks (if they are supported).
def getMatchingFiles(dir=".", regex="", full_names=False):
    p = re.compile(regex)
    matching_files = []
    dir_files = os.listdir(dir)
    for file in dir_files:
        m = p.match(file)
        if not m:
            continue
        full_name = os.path.join(dir, file)
        if not os.path.isfile(full_name):
            continue
        if full_names:
            matching_files.append(full_name)
        else:
            matching_files.append(file)
    return matching_files

# Return the list of srcpkg files found in dir (.tar.gz file).
# The returned list is ordered alphabetically (case ignored).
def listSrcPkgFiles(dir="."):
    # Should we assume that a pkg name always starts with a letter?
    # If YES, then use regex '^([a-zA-Z][^_]*)_([^_]+)\\.tar\\.gz$'
    srcpkg_regex = '^([^_]+)_([^_]+)\\.tar\\.gz$'
    srcpkg_files = getMatchingFiles(dir, srcpkg_regex)
    srcpkg_files.sort(lambda x, y: cmp(string.lower(x), string.lower(y)))
    return srcpkg_files


if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

