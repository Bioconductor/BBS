#!/usr/bin/env python3
##############################################################################

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
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
    print("### Check that %s branch does not already exist" % branch)
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

def _bump_version_and_create_branch(pkg, branch, no_bump, push):
    repo_url = 'git@%s:packages/%s.git' % (gitserver, pkg)
    bbs.gitutils.clone_or_pull_repo(pkg, repo_url, "master",
                                    discard_changes=True, cleanup=True)
    print()
    if _branch_exists(pkg, branch):
        print("Branch %s already exists ==> skip package" % branch)
        print()
    else:
        if not no_bump:
            _first_version_bump(pkg, branch)
        _create_branch(pkg, branch)
        if not no_bump:
            _second_version_bump(pkg, branch)
    if push:
        _push(pkg)
    print()
    return

def _bump_versions_and_create_branches(pkgs, branch, no_bump, push):
    do_what = 'Create' if no_bump else 'Bump version and create'
    do_what += ' %s branch' % branch
    i = 0
    for pkg in pkgs:
        i += 1
        for_what = 'for package %s (%d/%d)' % (pkg, i, len(pkgs))
        print('===============================================================')
        print('%s %s' % (do_what, for_what))
        print('---------------------------------------------------------------')
        print()
        _bump_version_and_create_branch(pkg, branch, no_bump, push)
    return

### Return a dict with 4 key->value pairs:
###   Key            Value
###   'no_bump'   -> True or False
###   'push'      -> True or False
###   'branch'    -> string
###   'pkgs'      -> list of strings
def parse_args(argv):
    usage_msg = 'Usage:\n' + \
        '    bump_version_and_create_branch.py [--no-bump] [--push] branch pkg1 pkg2 ...'
    if len(argv) < 2:
        sys.exit(usage_msg)
    argv = argv[1:]
    no_bump_idx = -1
    push_idx = -1
    for i in range(0, len(argv)):
        arg = argv[i]
        if arg == '--no-bump':
            if no_bump_idx != -1:
                sys.exit(usage_msg)
            no_bump_idx = i
            continue
        if arg == '--push':
            if push_idx != -1:
                sys.exit(usage_msg)
            push_idx = i
            continue
    if no_bump_idx == -1:
        no_bump = False
    else:
        no_bump = True
        argv.pop(no_bump_idx)
        if push_idx > no_bump_idx:
            push_idx -= 1
    if push_idx == -1:
        push = False
    else:
        push = True
        argv.pop(push_idx)
    if len(argv) == 0:
        sys.exit(usage_msg)
    branch = argv.pop(0)
    return {'no_bump': no_bump, 'push': push, 'branch': branch, 'pkgs': argv}

if __name__ == '__main__':
    parsed_args = parse_args(sys.argv)
    _bump_versions_and_create_branches(parsed_args['pkgs'],
                                       parsed_args['branch'],
                                       parsed_args['no_bump'],
                                       parsed_args['push'])

