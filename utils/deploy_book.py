#!/usr/bin/env python3
##############################################################################

import sys
import os
import tarfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.parse
import bbs.jobs

def deploy_book(srcpkg_path, dest_dir, use_rsync=False):
    pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
    dest_subdir = os.path.join(dest_dir, pkg)
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
        cmd = "rsync --delete -q -ave ssh %s %s" % (tmp_path, dest_dir)
        bbs.jobs.call(cmd, check=True)
    else:
        if os.path.exists(dest_subdir):
            shutil.rmtree(dest_subdir, ignore_errors=True)
        os.rename(content_path, dest_subdir)
    shutil.rmtree(pkg, ignore_errors=True)
    print('OK')
    sys.stdout.flush()
    return


##############################################################################
### MAIN SECTION
##############################################################################

def _parse_options(argv):
    usage_msg = 'Usage:\n' + \
        '    deploy_book.py <srcpkg-path> <dest-dir> [--use-rsync]\n'
    if len(argv) < 3 or len(argv) > 4:
        sys.exit(usage_msg)
    use_rsync = False
    if len(argv) == 4:
        if argv[3] != '--use-rsync':
            sys.exit(usage_msg)
        use_rsync = True
    return {'srcpkg_path': argv[1], 'dest_dir': argv[2], 'use_rsync': use_rsync}

if __name__ == '__main__':
    options = _parse_options(sys.argv)
    srcpkg_path = options['srcpkg_path']
    dest_dir = options['dest_dir']
    use_rsync = options['use_rsync']
    deploy_book(srcpkg_path, dest_dir, use_rsync=use_rsync)

