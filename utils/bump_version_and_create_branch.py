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

gitserver = "git.bioconductor.org"
commit_msg1 = "bump x.y.z version to even y prior to creation of %s branch"
commit_msg2 = "bump x.y.z version to odd y following creation of %s branch"
commit_msg3 = "bump version in master branch following creation of %s branch"

def _branch_exists(pkg_dir, branch):
    print("### Check if branch %s exists:" % branch)
    print()
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    cmd = "%s -C %s checkout %s" % (git_cmd, pkg_dir, branch)
    print("%s$ %s" % (os.getcwd(), cmd))
    ok = bbs.jobs.call(cmd) == 0
    print()
    cmd = "%s -C %s checkout master" % (git_cmd, pkg_dir)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    return ok

def _replace_version(pkg_dir, new_version):
    in_file = os.path.join(pkg_dir, 'DESCRIPTION')
    in_dcf = open(in_file, 'rb')
    out_file = os.path.join(pkg_dir, 'DESCRIPTION.modified')
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

def _git_add_DESCRIPTION_and_commit(pkg_dir, commit_msg):
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    cmd = "%s -C %s diff DESCRIPTION" % (git_cmd, pkg_dir)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    cmd = "%s -C %s add DESCRIPTION" % (git_cmd, pkg_dir)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    cmd = "%s -C %s commit -m '%s'" % (git_cmd, pkg_dir, commit_msg)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    return

def _first_version_bump(pkg_dir, branch):
    print("### First version bump:")
    print()
    pkg = bbs.parse.getPkgFromDir(pkg_dir)
    if pkg == "BiocVersion":
        print("This is BiocVersion ==> skip first version bump")
        print()
        return
    version = bbs.parse.getVersionFromDir(pkg_dir)
    xyz = version.replace('-', '.').split('.')
    x = int(xyz[0])
    y = int(xyz[1])
    z = int(xyz[2])
    if y == 99:
        x += 1
        y = 0
    else:
        y = (y // 2 + 1) * 2  # bump y to next even
    z = 0
    new_version = '.'.join([str(x), str(y), str(z)])
    _replace_version(pkg_dir, new_version)
    commit_msg = commit_msg1 % branch
    _git_add_DESCRIPTION_and_commit(pkg_dir, commit_msg)
    return

def _create_branch(pkg_dir, branch):
    print("### Create branch:")
    print()
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    cmd = "%s -C %s checkout -b %s" % (git_cmd, pkg_dir, branch)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    cmd = "%s -C %s checkout master" % (git_cmd, pkg_dir)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    return

def _second_version_bump(pkg_dir, branch):
    print("### Second version bump:")
    print()
    pkg = bbs.parse.getPkgFromDir(pkg_dir)
    version = bbs.parse.getVersionFromDir(pkg_dir)
    xyz = version.replace('-', '.').split('.')
    x = int(xyz[0])
    y = int(xyz[1])
    z = int(xyz[2])
    ## Should never happen
    if pkg != "BiocVersion" and y % 2 != 0:
        sys.exit("Abnomaly: y is odd!")
    y += 1
    z = 0
    new_version = '.'.join([str(x), str(y), str(z)])
    _replace_version(pkg_dir, new_version)
    if pkg != "BiocVersion":
        commit_msg = commit_msg2
    else:
        commit_msg = commit_msg3
    commit_msg %= branch
    _git_add_DESCRIPTION_and_commit(pkg_dir, commit_msg)
    return

def _push(pkg_dir):
    print("### Push changes:")
    print()
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    cmd = "%s -C %s push --all" % (git_cmd, pkg_dir)
    print("%s$ %s" % (os.getcwd(), cmd))
    bbs.jobs.call(cmd, check=True)
    print()
    return

def _bump_version_and_create_branch(pkg, branch, push):
    repo_url = 'git@%s:packages/%s.git' % (gitserver, pkg)
    bbs.gitutils.update_git_clone(pkg, repo_url, "master", undo_changes=True)
    print()
    if _branch_exists(pkg, branch):
        print("Branch %s already exists ==> skip package" % branch)
    else:
        _first_version_bump(pkg, branch)
        print()
        _create_branch(pkg, branch)
        print()
        _second_version_bump(pkg, branch)
    print()
    if push:
        _push(pkg)
        print()
    return

def _bump_versions_and_create_branches(pkgs, branch, push):
    i = 0
    for pkg in pkgs:
        i += 1
        print('---------------------------------------------------------------')
        print('Bump version and create branch for package %s (%d/%d)' % \
              (pkg, i, len(pkgs)))
        print()
        _bump_version_and_create_branch(pkg, branch, push)
    return

if __name__ == '__main__':
    usage_msg = 'Usage:\n' + \
        '    bump_version_and_create_branch.py branch_name pkg1 pkg2 ...\n' + \
        'or:\n' + \
        '    bump_version_and_create_branch.py --push branch_name pkg1 pkg2 ...'
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

