#!/usr/bin/env python3
##############################################################################

import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.manifest
import bbs.parse
import bbs.jobs
import bbs.gitutils

gitserver = 'git.bioconductor.org'

varname = 'commit_msg'
if varname not in os.environ or os.environ[varname] == "":
    sys.exit('please set environment variable %s with commit message' % varname)
commit_msg = os.environ[varname]

varname = 'new_date'
if varname not in os.environ or os.environ[varname] == "":
    sys.exit('please set environment variable %s with new Date' % varname)
commit_msg = os.environ[varname]

### Return the first 3 components only (additional components are ignored).
def _split_version(version):
    xyz = version.replace('-', '.').split('.')
    x = int(xyz[0])
    y = int(xyz[1])
    if len(xyz) >= 3:
        z = int(xyz[2])
    else:
        z = 0
    return [x, y, z]

def _unsplit_version(x, y, z):
    return '.'.join([str(x), str(y), str(z)])

def _bump_to_next_z(version):
    x, y, z = _split_version(version)
    z += 1
    return _unsplit_version(x, y, z)

def _replace_version(pkgsrctree, new_version, new_date=None):
    in_file = os.path.join(pkgsrctree, 'DESCRIPTION')
    in_dcf = open(in_file, 'rb')
    out_file = os.path.join(pkgsrctree, 'DESCRIPTION.modified')
    out_dcf = open(out_file, 'wb')
    key1 = 'Version:'
    key2 = 'Date:'
    for line in in_dcf:
        s = bbs.parse.bytes2str(line)
        if s[:len(key1)] == key1:
            line = key1 + ' ' + new_version + '\n'
            line = line.encode()
        if new_date != None and s[:len(key2)] == key2:
            line = key1 + ' ' + new_date + '\n'
            line = line.encode()
        out_dcf.write(line)
    out_dcf.close()
    in_dcf.close()
    os.rename(out_file, in_file)
    return

def _run_git_cmd(pkgsrctree, args, check=True):
    cmd = "%s -C %s %s" % (bbs.gitutils._git_cmd, pkgsrctree, args)
    print("%s$ %s" % (os.getcwd(), cmd))
    retcode = bbs.jobs.call(cmd, check=check)
    print()
    return retcode

def _git_add_DESCRIPTION_and_commit(pkgsrctree):
    _run_git_cmd(pkgsrctree, "--no-pager diff DESCRIPTION")
    #_run_git_cmd(pkgsrctree, "add DESCRIPTION")
    #_run_git_cmd(pkgsrctree, "commit -m '%s'" % commit_msg)
    _run_git_cmd(pkgsrctree, "commit -a -m '%s'" % commit_msg)
    return

def _small_version_bump(pkgsrctree, branch):
    print('---------------------------------------------------------------')
    print("### Small version bump")
    print()
    pkg = bbs.parse.get_Package_from_pkgsrctree(pkgsrctree)
    version = bbs.parse.get_Version_from_pkgsrctree(pkgsrctree)
    new_version = _bump_to_next_z(version)
    _replace_version(pkgsrctree, new_version, new_date)
    _git_add_DESCRIPTION_and_commit(pkgsrctree)
    return

def _push(pkgsrctree):
    print('---------------------------------------------------------------')
    print("### Push changes")
    print()
    _run_git_cmd(pkgsrctree, "push --all")
    return

def _bump_pkg_version(pkg, branch, push):
    repo_url = 'git@%s:packages/%s.git' % (gitserver, pkg)
    bbs.gitutils.update_git_clone(pkg, repo_url, "master", undo_changes=True)
    print()
    _small_version_bump(pkg, branch)
    if push:
        _push(pkg)
    print()
    return

def _bump_all_pkg_versions(pkgs, branch, push):
    i = 0
    for pkg in pkgs:
        i += 1
        print('===============================================================')
        print('Bump version for package %s (%d/%d)' % \
              (pkg, i, len(pkgs)))
        print('---------------------------------------------------------------')
        print()
        _bump_pkg_version(pkg, branch, push)
    return

if __name__ == '__main__':
    usage_msg = 'Usage:\n' + \
        '    small_version_bumps.py branch_name pkg1 pkg2 ...\n' + \
        'or:\n' + \
        '    small_version_bumps.py --push branch_name pkg1 pkg2 ...'
    argc = len(sys.argv)
    if argc <= 1:
        sys.exit(usage_msg)
    arg1 = sys.argv[1]
    push = arg1 == "--push"
    if push:
        pkgs = sys.argv[3:]
        branch = sys.argv[2]
    else:
        pkgs = sys.argv[2:]
        branch = sys.argv[1]
    _bump_all_pkg_versions(pkgs, branch, push)

