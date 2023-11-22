#!/usr/bin/env python3
##############################################################################

import sys
import os
import time
import tarfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.parse
import bbs.jobs

def _deploy_book(pkg, version, dest_dir):
    srcpkg_file = '%s_%s.tar.gz' % (pkg, version)
    dest_subdir = os.path.join(dest_dir, pkg)
    print("Deploying content from book tarball '%s' to '%s/' ..." % \
          (srcpkg_file, dest_subdir), end=' ')
    sys.stdout.flush()
    if not os.path.exists(srcpkg_file):
        errmsg = "oops.. couldn't find book tarball '%s' " % srcpkg_file + \
                 "in\ndirectory:\n\n  %s\n\n" % os.getcwd() + \
                 "Most likely this means that the package index " + \
                 "(PACKAGES file) is out-of-sync\nwith the content of " + \
                 "the directory.\n\nDid you run prepareRepos-books.sh " + \
                 "before trying to deploy the books?"
        raise FileExistsError(errmsg)
    tar = tarfile.open(srcpkg_file)
    tar.extractall()

    ## First we try to deploy the content of 'inst/doc/book/'. If the
    ## book tarball doesn't contain this folder, then we try to deploy
    ## the content of 'vignettes/book/docs/' instead.
    content_path = os.path.join(pkg, 'inst', 'doc', 'book')
    if not os.path.isdir(content_path):
        content_path2 = os.path.join(pkg, 'vignettes', 'book', 'docs')
        if not os.path.isdir(content_path2):
            errmsg = "%s has no '%s' " % (srcpkg_file, content_path) + \
                     "or '%s' folder. " % content_path2 + \
                     "Can't deploy this book!"
            raise NotADirectoryError(errmsg)
        print("(tarball has no '%s' folder, deploying '%s' instead) ..." % \
              (content_path, content_path2), end=' ')
        content_path = content_path2

    ## Deploy book content.
    tmp_path = os.path.join(pkg, pkg)
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path, ignore_errors=True)
    os.rename(content_path, tmp_path)
    cmd = "rsync --delete -q -ave ssh %s %s" % (tmp_path, dest_dir)
    bbs.jobs.call(cmd, check=True)

    shutil.rmtree(pkg, ignore_errors=True)
    print('OK')
    sys.stdout.flush()
    return

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: BBS-deploy-books.py <dest_dir>')
    print()
    print('BBS> ==============================================================')
    print('BBS> START deploying books on %s...' % time.asctime())
    sys.stdout.flush()
    dest_dir = sys.argv[1]
    PACKAGES = bbs.parse.parse_DCF('PACKAGES')
    for dcf_record in PACKAGES:
        pkg = dcf_record['Package']
        version = dcf_record['Version']
        _deploy_book(pkg, version, dest_dir)
    print('BBS> DONE deploying books on %s.' % time.asctime())

