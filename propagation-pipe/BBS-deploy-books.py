#!/usr/bin/env python3
##############################################################################

import sys
import os
import tarfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.jobs

def _append_package(pkgversions, pkg, version,
                    recno, rec_firstlineno, rec_lastlineno, dcf):
    if pkg == None or version == None:
        errmsg = 'Package or Version field is missing in ' + \
                 'record %d (lines %d-%d)\n  in DCF file \'%s\'' % \
                 (recno, rec_firstlineno, rec_lastlineno, dcf)
        raise Exception(errmsg)
    pkgversions.append((pkg.strip(), version.strip()))
    return

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

### Load package list as ('Package', 'Version') pairs.
def _get_package_list(dcf):
    f = open(dcf, 'r')
    pkgversions = []
    recno = 0
    rec_firstlineno = 0
    lineno = 0
    pkg = version = None
    for line in f:
        lineno += 1
        if line.strip() != '':
            ## Skip comment lines.
            if line.startswith('#'):
                continue
            if rec_firstlineno == 0:
                recno += 1
                rec_firstlineno = lineno
            if line.startswith('Package:'):
                pkg = line[len('Package:'):]
            elif line.startswith('Version:'):
                version = line[len('Version:'):]
        elif rec_firstlineno != 0:
            _append_package(pkgversions, pkg, version,
                            recno, rec_firstlineno, lineno - 1, dcf)
            rec_firstlineno = 0
            pkg = version = None
    if rec_firstlineno != 0:
        _append_package(pkgversions, pkg, version,
                        recno, rec_firstlineno, lineno - 1, dcf)
    f.close()
    return pkgversions

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: BBS-deploy-books.py <destdir>')
    destdir = sys.argv[1]
    pkgversions = _get_package_list('PACKAGES')
    for (pkg, version) in pkgversions:
        _deploy_book(pkg, version, destdir)

