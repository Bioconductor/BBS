#!/usr/bin/env python3
##############################################################################

import sys
import os
import tarfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.parse
import bbs.jobs

def _deploy_book(pkg, version, destdir):
    book_destroot = os.path.join(destdir, pkg)
    print('Deploying %s book at \'%s/\' ...' % (pkg, book_destroot), end=' ')
    sys.stdout.flush()
    srcpkg_file = '%s_%s.tar.gz' % (pkg, version)
    tar = tarfile.open(srcpkg_file)
    tar.extractall()
    docs_path = os.path.join(pkg, 'vignettes', 'book', 'docs')
    if not os.path.isdir(docs_path):
        errmsg = 'directory \'%s\' not found in %s' % \
                 (docs_path, srcpkg_file)
        raise Exception(errmsg)
    book_localroot = os.path.join(pkg, 'vignettes', 'book', pkg)
    if os.path.exists(book_localroot):
        shutil.rmtree(book_localroot, ignore_errors=True)
    os.rename(docs_path, book_localroot)
    cmd = "rsync --delete -q -ave ssh %s %s" % (book_localroot, destdir)
    bbs.jobs.call(cmd, check=True)
    shutil.rmtree(pkg, ignore_errors=True)
    print('OK')
    sys.stdout.flush()
    return

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: BBS-deploy-books.py <destdir>')
    destdir = sys.argv[1]
    PACKAGES = bbs.parse.parse_DCF('PACKAGES')
    for dcf_record in PACKAGES:
        pkg = dcf_record['Package']
        version = dcf_record['version']
        _deploy_book(pkg, version, destdir)

