#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Sep 17, 2019
###
### bbs.fileutils module
###

import os
import sys
import re
import shutil
import string

# Equivalent to 'du -sb <path>'
# WARNING: Result will not be accurate on Windows when <path> is (or contains)
# a shortcut
def total_size(path):
    if not os.path.exists(path):
        return 0
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
                    try:
                        os.chmod(filename, 0o777)
                    except:
                        pass
    shutil.rmtree(dir, ignore_errors=True)
    return

def remake_dir(path):
    if os.path.exists(path):
        nuke_tree(path)
    os.mkdir(path)
    return

## rsync will interprets a path that starts with a drive letter followed by a
## colon (e.g. E:\biocbuild\bbs-3.15-bioc\products-out\install) as a remote
## location. So in order for Cygwin rsync to interpret the path correctly,
## we must first convert it to a cygwin-style path e.g.
## /cygdrive/e/biocbuild/bbs-3.15-bioc/products-out/install
def to_cygwin_style(path):
    if path[1] != ':' or \
       not path[0].isupper() or path[0] in ['A', 'B'] or \
       path[2] not in ['\\', '/']:
        return path
    return '/cygdrive/%s%s' % (path[0].lower(), path[2:].replace('\\', '/'))

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
    matching_files.sort(key=str.lower)
    return matching_files

# Return the list of srcpkg files found in dir (.tar.gz file).
# The returned list is ordered alphabetically (case ignored).
def listSrcPkgFiles(dir="."):
    # Should we assume that a pkg name always starts with a letter?
    # If YES, then use regex '^([a-zA-Z][^_]*)_([^_]+)\\.tar\\.gz$'
    srcpkg_regex = '^([^_]+)_([^_]+)\\.tar\\.gz$'
    return getMatchingFiles(dir, srcpkg_regex)

# Return a list of vignette product files
def toList(arg):
    if not isinstance(arg, (list, tuple)):
        arg = [arg]
    return arg

def renameFileExt(files, exts):
    files = toList(files)
    exts = toList(exts)
    res = []
    for file in files:
        base = os.path.splitext(file)[0]
        for ext in exts:
            res.append(base+'.'+ext)
    if len(res) == 1:
        res = res[0]
    return res

def getVigProdFiles(rmd_files):
    return renameFileExt(rmd_files, ['html', 'R'])

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")
