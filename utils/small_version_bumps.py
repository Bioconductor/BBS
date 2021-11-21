#!/usr/bin/env python3
##############################################################################

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
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
new_date = os.environ[varname]

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

def _replace_version(repo_path, new_version, new_date=None):
    in_file = os.path.join(repo_path, 'DESCRIPTION')
    in_dcf = open(in_file, 'rb')
    out_file = os.path.join(repo_path, 'DESCRIPTION.modified')
    out_dcf = open(out_file, 'wb')
    key1 = 'Version:'
    key2 = 'Date:'
    for line in in_dcf:
        s = bbs.parse.bytes2str(line)
        if s[:len(key1)] == key1:
            line = key1 + ' ' + new_version + '\n'
            line = line.encode()
        if new_date != None and s[:len(key2)] == key2:
            line = key2 + ' ' + new_date + '\n'
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

def _git_add_DESCRIPTION_and_commit(repo_path):
    # If 'repo_path' is not a git repo, 'git --no-pager diff DESCRIPTION'
    # will spit out many screens of ugly output!
    if not bbs.gitutils.is_git_repo(repo_path):
        sys.exit('ERROR: \'%s\' is not a git repo' % repo_path)
    _run_git_cmd(repo_path, "--no-pager diff DESCRIPTION")
    #_run_git_cmd(repo_path, "add DESCRIPTION")
    #_run_git_cmd(repo_path, "commit -m '%s'" % commit_msg)
    _run_git_cmd(repo_path, "commit -a -m '%s'" % commit_msg)
    return

def _small_version_bump(repo_path, branch):
    print('---------------------------------------------------------------')
    print("### Small version bump")
    print()
    pkg = bbs.parse.get_Package_from_pkgsrctree(repo_path)
    version = bbs.parse.get_Version_from_pkgsrctree(repo_path)
    new_version = _bump_to_next_z(version)
    _replace_version(repo_path, new_version, new_date)
    _git_add_DESCRIPTION_and_commit(repo_path)
    return

def _push(repo_path):
    print('---------------------------------------------------------------')
    print("### Push changes")
    print()
    _run_git_cmd(repo_path, "push --all")
    return

def _bump_pkg_version(repo_path, branch, push):
    print()
    _small_version_bump(repo_path, branch)
    if push:
        _push(repo_path)
    return

def _bump_all_pkg_versions(repo_paths, branch, push):
    i = 0
    for repo_path in repo_paths:
        i += 1
        print('===============================================================')
        print('Bump version for package %s (%d/%d)' % \
              (repo_path, i, len(repo_paths)))
        print('---------------------------------------------------------------')
        print()
        _bump_pkg_version(repo_path, branch, push)
    return

def _get_repo_paths_and_branch_and_push(argv):
    usage_msg = 'Usage:\n' + \
        '    small_version_bumps.py [--branch <branch-name>] repo_path1 repo_path2 ... [--push]'
    if len(argv) == 0:
        sys.exit(usage_msg)  # should never happen
    repo_paths = argv[1:]
    branch = None
    push = False
    # Extract 'push'.
    if len(repo_paths) >= 1:
        push = repo_paths[-1] == '--push'
        if push:
            repo_paths = repo_paths[:-1]
    if '--push' in repo_paths:
        sys.exit(usage_msg)
    # Extract 'branch'.
    if len(repo_paths) >= 1 and repo_paths[0] == '--branch':
        if len(repo_paths) == 1:
            sys.exit(usage_msg)
        branch = repo_paths[1]
        repo_paths = repo_paths[2:]
    if '--branch' in repo_paths:
        sys.exit(usage_msg)
    return (repo_paths, branch, push)

if __name__ == '__main__':
    (repo_paths, branch, push) = _get_repo_paths_and_branch_and_push(sys.argv)
    if len(repo_paths) <= 1:
        if len(repo_paths) == 0:
            repo_path = '.'
        else:
            repo_path = repo_paths[0]
        _bump_pkg_version(repo_path, branch, push)
    else:
        _bump_all_pkg_versions(repo_paths, branch, push)

