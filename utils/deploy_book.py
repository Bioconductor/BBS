#!/usr/bin/env python3
##############################################################################

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.bookutils

def _parse_options(argv):
    usage_msg = 'Usage:\n' + \
        '    deploy_book.py <srcpkg-path> <destdir> [--use-rsync]\n'
    if len(argv) < 3 or len(argv) > 4:
        sys.exit(usage_msg)
    use_rsync = False
    if len(argv) == 4:
        if argv[3] != '--use-rsync':
            sys.exit(usage_msg)
        use_rsync = True
    return {'srcpkg_path': argv[1], 'destdir': argv[2], 'use_rsync': use_rsync}

if __name__ == '__main__':
    options = _parse_options(sys.argv)
    srcpkg_path = options['srcpkg_path']
    destdir = options['destdir']
    use_rsync = options['use_rsync']
    bbs.bookutils.deploy_book(srcpkg_path, destdir, use_rsync=use_rsync)

