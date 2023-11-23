#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Nov 22, 2023
###
### bbs.bookutils module
###

import sys
import os
import tarfile
import shutil

sys.path.insert(0, os.path.dirname(__file__))
import parse
import jobs

def deploy_book(srcpkg_path, destdir, use_rsync=False):
    if not use_rsync and not os.path.isdir(destdir):
        errmsg = "Can't deploy book to '%s': No such directory" % destdir
        raise NotADirectoryError(errmsg)
    pkg = parse.get_pkgname_from_srcpkg_path(srcpkg_path)
    dest_subdir = os.path.join(destdir, pkg)
    print("Deploying content from book tarball '%s' to '%s/' ..." % \
          (srcpkg_path, dest_subdir), end=' ')
    sys.stdout.flush()
    shutil.rmtree(pkg, ignore_errors=True)  # if leftover from previous run
    tar = tarfile.open(srcpkg_path)
    tar.extractall()

    ## First we try to deploy the content of 'inst/doc/book/'. If the
    ## book tarball doesn't contain this folder, then we try to deploy
    ## the content of 'vignettes/book/docs/' instead.
    content_path = os.path.join(pkg, 'inst', 'doc', 'book')
    if not os.path.isdir(content_path):
        content_path2 = os.path.join(pkg, 'vignettes', 'book', 'docs')
        if not os.path.isdir(content_path2):
            errmsg = "%s has no '%s' " % (srcpkg_path, content_path) + \
                     "or '%s' folder. " % content_path2 + \
                     "Can't deploy book!"
            raise NotADirectoryError(errmsg)
        print("(tarball has no '%s' folder, deploying '%s' instead) ..." % \
              (content_path, content_path2), end=' ')
        content_path = content_path2

    ## Deploy book content.
    if use_rsync:
        tmp_path = os.path.join(pkg, pkg)
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path, ignore_errors=True)
        os.rename(content_path, tmp_path)
        cmd = "rsync --delete -q -ave ssh %s %s" % (tmp_path, destdir)
        jobs.call(cmd, check=True)
    else:
        if os.path.exists(dest_subdir):
            shutil.rmtree(dest_subdir, ignore_errors=True)
        os.rename(content_path, dest_subdir)
    shutil.rmtree(pkg, ignore_errors=True)
    print('OK')
    sys.stdout.flush()
    return

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

