#!/usr/bin/env python3
##############################################################################

import sys
import os
import tarfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.parse
import bbs.jobs

def _deploy_book(pkg, version, dest_dir):
    dest_subdir = os.path.join(dest_dir, pkg)
    print('Deploying %s book at \'%s/\' ...' % (pkg, dest_subdir), end=' ')
    sys.stdout.flush()
    srcpkg_file = '%s_%s.tar.gz' % (pkg, version)
    tar = tarfile.open(srcpkg_file)
    tar.extractall()

    ## First we try to deploy the content of 'inst/doc/book/'. If the
    ## book tarball doesn't contain this folder, then we try to deploy
    ## the content of 'vignettes/book/docs/' instead.
    content_path = os.path.join(pkg, 'inst', 'doc', 'book')
    if not os.path.isdir(content_path):
        content_path2 = os.path.join(pkg, 'vignettes', 'book', 'docs')
        if not os.path.isdir(content_path2):
            errmsg = '%s has no \'%s\' or \'%s\' folder' % \
                     (srcpkg_file, content_path, content_path2)
            raise Exception(errmsg)
        print('(tarball has no \'%s\' folder, deploying \'%s\' instead) ...' % \
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
    dest_dir = sys.argv[1]
    PACKAGES = bbs.parse.parse_DCF('PACKAGES')
    for dcf_record in PACKAGES:
        pkg = dcf_record['Package']
        version = dcf_record['Version']
        _deploy_book(pkg, version, dest_dir)

