#!/usr/bin/env python3
##############################################################################

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.parse
import bbs.bookutils

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: BBS-deploy-books.py <destdir>')
    print()
    print('BBS> ==============================================================')
    print('BBS> START deploying books on %s ...' % time.asctime())
    sys.stdout.flush()
    destdir = sys.argv[1]
    PACKAGES = bbs.parse.parse_DCF('PACKAGES')
    for dcf_record in PACKAGES:
        pkg = dcf_record['Package']
        version = dcf_record['Version']
        srcpkg_file = '%s_%s.tar.gz' % (pkg, version)
        if not os.path.exists(srcpkg_file):
            errmsg = "oops.. couldn't find book tarball '%s' " % srcpkg_file + \
                     "in\ndirectory:\n\n  %s\n\n" % os.getcwd() + \
                     "Most likely this means that the package index " + \
                     "(PACKAGES file) is out-of-sync\nwith the content of " + \
                     "the directory.\n\nDid you run prepareRepos-books.sh " + \
                     "before trying to deploy the books?"
            raise FileExistsError(errmsg)
        bbs.bookutils.deploy_book(srcpkg_file, destdir, use_rsync=True)
    print('BBS> DONE deploying books on %s.' % time.asctime())

