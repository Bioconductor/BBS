#!/usr/bin/env python3
##############################################################################

import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.gitutils

gitserver = 'git.bioconductor.org'

def _infer_repo_name_from_path(repo_path):
    repo_name = os.path.basename(repo_path)
    if repo_name == '':
        repo_name = os.path.basename(os.path.dirname(repo_path))
    last_char = repo_name[-1:]
    if last_char in ['', '.', ' ']:
        raise ValueError('cannot infer repo name from supplied path')
    return repo_name

def _get_repo_path_and_branch(argv):
    usage_msg = 'Usage:\n' + \
        '    clone_or_pull_repo.py [--branch <branch-name>] [<path-to-repo>]'
    argc = len(argv)
    if argc == 0 or argc >= 5:
        sys.exit(usage_msg)
    repo_path = '.'
    if argc <= 2:
        branch = None
        if argc == 2:
            repo_path = argv[1]
    else:
        if argv[1] != '--branch':
            sys.exit(usage_msg)
        branch = argv[2]
        if argc == 4:
            repo_path = argv[3]
    return (repo_path, branch)

def _validate_repo_path(repo_path):
    try:
        local_changes = bbs.gitutils._repo_has_local_changes(repo_path)
    except NotADirectoryError as e:
        print(e)
        print()
        sys.exit('ERROR: the supplied path is not a directory')
    except subprocess.CalledProcessError as e:
        print(e)
        print()
        sys.exit('ERROR: the supplied path is not a git repo')
    if local_changes:
        print()
        sys.exit('ERROR: the repo has local (uncommitted) changes')
    return

if __name__ == '__main__':
    (repo_path, branch) = _get_repo_path_and_branch(sys.argv)
    bbs.gitutils.verbose = False
    if os.path.exists(repo_path):
        _validate_repo_path(repo_path)
        bbs.gitutils._pull_repo(repo_path, branch=branch, cleanup=True)
    else:
        # We try to infer the repo name from the supplied path.
        repo_name = _infer_repo_name_from_path(repo_path)
        repo_url = 'git@%s:packages/%s.git' % (gitserver, repo_name)
        try:
            bbs.gitutils._clone_repo(repo_path, repo_url, branch)
        except subprocess.CalledProcessError as e:
            print(e)
            print()
            sys.exit('ERROR: failed to clone %s' % repo_url)

