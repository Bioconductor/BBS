#! /usr/bin/env python
##############################################################################

import sys
import os

import git

home = os.path.expanduser('~')
manifest_git_clone = os.path.join(home, 'git.bioconductor.org', 'manifest')
manifest_git_repo_url = 'git@git.bioconductor.org:admin/manifest.git'

def update_manifest(git_branch=None):
    git.update_git_clone(manifest_git_clone,
                         manifest_git_repo_url,
                         git_branch)
    return

def read_manifest(manifest_path):
    dcf = open(manifest_path, 'r')
    pkgs = []
    for line in dcf:
        if not line.startswith('Package:'):
            continue
        pkg = line[len('Package:'):].strip()
        pkgs.append(pkg)
    dcf.close()
    return pkgs

def update_packages(pkg_dir, manifest_file, git_branch=None, skip=None):
    update_manifest(git_branch)
    manifest_path = os.path.join(manifest_git_clone, manifest_file)
    pkgs = read_manifest(manifest_path)
    if skip == None:
        skip = 0
    i = 0
    for pkg in pkgs:
        i = i + 1
        if i <= skip:
            continue
        print 'BBS> ----------------------------------------------------------'
        print 'BBS> [update_packages] (%d/%d) repo: %s / branch: %s' % \
              (i, len(pkgs), pkg, git_branch)
        print ''
        pkg_git_clone = os.path.join(pkg_dir, pkg)
        pkg_git_repo_url = 'git@git.bioconductor.org:packages/%s.git' % pkg
        git.update_git_clone(pkg_git_clone, pkg_git_repo_url, git_branch)
    return

def update_software(git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'software')
    update_packages(pkg_dir, 'software.txt', git_branch, skip)
    return

def update_data_experiment(git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'data-experiment')
    update_packages(pkg_dir, 'data-experiment.txt', git_branch, skip)
    return

if __name__ == '__main__':
    usage_msg = 'Usage:\n' + \
        '    update_bioc_git_repos.py [manifest|software|data-experiment]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [manifest|software|data-experiment] [master|RELEASE_3_5]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment] <skip>\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment] [master|RELEASE_3_5] <skip>'
    argc = len(sys.argv)
    git_branch = skip = None
    if argc == 2:
        pass
    elif argc == 3:
        arg2 = sys.argv[2]
        try:
            skip = int(arg2)
        except ValueError:
            git_branch = arg2
    elif argc == 4:
        git_branch = sys.argv[2]
        try:
            skip = int(sys.argv[3])
        except ValueError:
            sys.exit('invalid skip (must be an integer value)')
    else:
        sys.exit(usage_msg)
    what = sys.argv[1]
    if what == 'manifest':
        if skip != None:
            sys.exit(usage_msg)
        update_manifest(git_branch)
    elif what == 'software':
        update_software(git_branch, skip)
    elif what == 'data-experiment':
        update_data_experiment(git_branch, skip)
    else:
        sys.exit(usage_msg)

