#!/usr/bin/env python3
##############################################################################

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.manifest
import bbs.parse
import bbs.jobs
import bbs.gitutils

gitserver = "git.bioconductor.org"
commit_msg1 = "bump x.y.z version to even y prior to creation of %s branch"
commit_msg2 = "bump x.y.z version to odd y following creation of %s branch"
commit_msg3 = "bump version in master branch following creation of %s branch"

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

def _bump_to_next_even_y(version):
    x, y, z = _split_version(version)
    if y == 99:
        x += 1
        y = 0
    else:
        y = (y // 2 + 1) * 2  # bump y to next even
    z = 0
    return _unsplit_version(x, y, z)

def _bump_to_next_y(version, pkg=None):
    x, y, z = _split_version(version)
    ## Should never happen
    if pkg != "BiocVersion" and y % 2 != 0:
        sys.exit("Abnomaly: y is odd!")
    y += 1
    z = 0
    return _unsplit_version(x, y, z)

def _replace_version(repo_path, new_version):
    in_file = os.path.join(repo_path, 'DESCRIPTION')
    in_dcf = open(in_file, 'rb')
    out_file = os.path.join(repo_path, 'DESCRIPTION.modified')
    out_dcf = open(out_file, 'wb')
    key = 'Version:'
    for line in in_dcf:
        s = bbs.parse.bytes2str(line)
        if s[:len(key)] == key:
            line = key + ' ' + new_version + '\n'
            line = line.encode()
        out_dcf.write(line)
    out_dcf.close()
    in_dcf.close()
    os.rename(out_file, in_file)
    return

def _run_git_cmd(repo_path, args, check=True):
    cmd = "%s -C %s %s" % (bbs.gitutils._git_cmd, repo_path, args)
    print("%s$ %s" % (os.getcwd(), cmd))
    retcode = bbs.jobs.call(cmd, check=check)
    print()
    return retcode

def _git_add_DESCRIPTION_and_commit(repo_path, commit_msg):
    _run_git_cmd(repo_path, "--no-pager diff DESCRIPTION")
    _run_git_cmd(repo_path, "add DESCRIPTION")
    _run_git_cmd(repo_path, "commit -m '%s'" % commit_msg)
    return

def _branch_exists(repo_path, branch):
    print('---------------------------------------------------------------')
    print("### Check if branch %s exists" % branch)
    print()
    retcode = _run_git_cmd(repo_path, "checkout %s" % branch, check=False)
    _run_git_cmd(repo_path, "checkout master")
    return retcode == 0

def _first_version_bump(repo_path, branch):
    print('---------------------------------------------------------------')
    print("### First version bump")
    print()
    pkg = bbs.parse.get_Package_from_pkgsrctree(repo_path)
    if pkg == "BiocVersion":
        print("This is BiocVersion ==> skip first version bump")
        print()
        return
    version = bbs.parse.get_Version_from_pkgsrctree(repo_path)
    new_version = _bump_to_next_even_y(version)
    _replace_version(repo_path, new_version)
    commit_msg = commit_msg1 % branch
    _git_add_DESCRIPTION_and_commit(repo_path, commit_msg)
    return

def _create_branch(repo_path, branch):
    print('---------------------------------------------------------------')
    print("### Create branch")
    print()
    _run_git_cmd(repo_path, "checkout -b %s" % branch)
    _run_git_cmd(repo_path, "checkout master")
    return

def _second_version_bump(repo_path, branch):
    print('---------------------------------------------------------------')
    print("### Second version bump")
    print()
    pkg = bbs.parse.get_Package_from_pkgsrctree(repo_path)
    version = bbs.parse.get_Version_from_pkgsrctree(repo_path)
    new_version = _bump_to_next_y(version, pkg)
    _replace_version(repo_path, new_version)
    if pkg != "BiocVersion":
        commit_msg = commit_msg2
    else:
        commit_msg = commit_msg3
    commit_msg %= branch
    _git_add_DESCRIPTION_and_commit(repo_path, commit_msg)
    return

def _push(repo_path):
    print('---------------------------------------------------------------')
    print("### Push changes")
    print()
    _run_git_cmd(repo_path, "push --all")
    return

def _bump_version_and_create_branch(pkg, branch, push):
    repo_url = 'git@%s:packages/%s.git' % (gitserver, pkg)
    bbs.gitutils.clone_or_pull_repo(pkg, repo_url, "master",
                                    discard_changes=True, cleanup=True)
    print()
    if _branch_exists(pkg, branch):
        print("Branch %s already exists ==> skip package" % branch)
        print()
    else:
        _first_version_bump(pkg, branch)
        _create_branch(pkg, branch)
        _second_version_bump(pkg, branch)
    if push:
        _push(pkg)
    print()
    return

def _bump_versions_and_create_branches(pkgs, branch, push):
    i = 0
    for pkg in pkgs:
        i += 1
        print('===============================================================')
        print('Bump version and create branch for package %s (%d/%d)' % \
              (pkg, i, len(pkgs)))
        print('---------------------------------------------------------------')
        print()
        _bump_version_and_create_branch(pkg, branch, push)
    return

if __name__ == '__main__':
    usage_msg = 'Usage:\n' + \
        '    bump_version_and_create_branch.py [--push] branch pkg1 pkg2 ...'
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
    _bump_versions_and_create_branches(pkgs, branch, push)

