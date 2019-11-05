#!/usr/bin/env python3
##############################################################################

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import bbs.manifest
import bbs.gitutils

gitserver = 'git.bioconductor.org'

home = os.path.expanduser('~')
manifest_git_clone = os.path.join(home, 'git.bioconductor.org', 'manifest')
manifest_git_repo_url = 'git@%s:admin/manifest.git' % gitserver

def update_packages(pkg_dir, pkgs, pkg_git_branch=None, skip=None):
    if skip == None:
        skip = 0
    i = 0
    for pkg in pkgs:
        i += 1
        if i <= skip:
            continue
        print('BBS> ----------------------------------------------------------')
        print('BBS> [update_packages] (%d/%d) repo: %s / branch: %s' % \
              (i, len(pkgs), pkg, pkg_git_branch))
        print()
        pkg_git_clone = os.path.join(pkg_dir, pkg)
        pkg_git_repo_url = 'git@%s:packages/%s.git' % (gitserver, pkg)
        bbs.gitutils.update_git_clone(pkg_git_clone, pkg_git_repo_url,
                                      pkg_git_branch)
    return

def update_packages_in_current_working_dir(pkg_git_branch=None, skip=None):
    key = 'MANIFEST_FILE'
    print('BBS> Environment variable %s is' % key, end=' ')
    if key in os.environ and os.environ[key] != "":
        manifest_path = os.environ[key]
        print('defined and set to:')
        print('BBS>     %s' % manifest_path)
        print('BBS> ==> Using %s as manifest file...' % manifest_path)
        pkgs = bbs.manifest.read(manifest_path)
        print('BBS> Nb of packages listed in manifest file: %d' % len(pkgs))
    else:
        print('NOT defined (or is set to ')
        print('BBS> the empty string).')
        print('BBS> ==> Assuming all subdirs in current ' + \
              'directory are git repos')
        print('BBS>     and updating them...')
        pkgs = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
        print('BBS> Nb of subdirs in current directory: %d' % len(pkgs))
    print()
    update_packages('.', pkgs, pkg_git_branch, skip)
    return

def update_manifest(manifest_git_branch=None):
    print('BBS> ----------------------------------------------------------')
    print('BBS> [update_manifest] branch: %s' % manifest_git_branch)
    print()
    bbs.gitutils.update_git_clone(manifest_git_clone,
                                  manifest_git_repo_url,
                                  manifest_git_branch)
    return

def update_packages_from_manifest(pkg_dir, manifest_file,
                                  pkg_git_branch=None,
                                  manifest_git_branch=None,
                                  skip=None):
    if manifest_git_branch == None:
        manifest_git_branch = pkg_git_branch
    update_manifest(manifest_git_branch)
    manifest_path = os.path.join(manifest_git_clone, manifest_file)
    pkgs = bbs.manifest.read(manifest_path)
    update_packages(pkg_dir, pkgs, pkg_git_branch, skip)
    return

def update_software(pkg_git_branch=None, manifest_git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'software')
    update_packages_from_manifest(pkg_dir, 'software.txt',
                                  pkg_git_branch, manifest_git_branch, skip)
    return

def update_data_experiment(pkg_git_branch=None, manifest_git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'data-experiment')
    update_packages_from_manifest(pkg_dir, 'data-experiment.txt',
                                  pkg_git_branch, manifest_git_branch, skip)
    return

def update_workflows(pkg_git_branch=None, manifest_git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'workflows')
    update_packages_from_manifest(pkg_dir, 'workflows.txt',
                                  pkg_git_branch, manifest_git_branch, skip)
    return

if __name__ == '__main__':
    usage_msg = 'Usage:\n' + \
        '    update_bioc_git_repos.py\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [manifest|software|data-experiment|workflows]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [manifest|software|data-experiment|workflows] [master|RELEASE_3_6]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment|workflows] [master|RELEASE_3_6 [master|RELEASE_3_6]]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment|workflows] <skip>\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment|workflows] [master|RELEASE_3_6 [master|RELEASE_3_6]] <skip>\n' + \
        'NOTE: The 2nd branch specification indicates the branch of the manifest.'
    argc = len(sys.argv)
    if argc == 1:
        update_packages_in_current_working_dir()
        sys.exit()
    ## 'argc' is at least 2
    git_branch1 = git_branch2 = skip = None
    try:
        skip = int(sys.argv[-1])
    except ValueError:
        pass
    else:
        if argc <= 2:
            sys.exit(usage_msg)
        argc -= 1
    ## 'argc' is still at least 2
    what = sys.argv[1]
    if argc > 2:
        git_branch1 = sys.argv[2]
        if argc > 3:
            git_branch2 = sys.argv[3]
            if argc > 4:
                sys.exit('invalid skip (must be an integer value)')
    if what == 'manifest':
        if argc > 3 or skip != None:
            sys.exit(usage_msg)
        update_manifest(git_branch1)
    elif what == 'software':
        update_software(git_branch1, git_branch2, skip)
    elif what == 'data-experiment':
        update_data_experiment(git_branch1, git_branch2, skip)
    elif what == 'workflows':
        update_workflows(git_branch1, git_branch2, skip)
    else:
        sys.exit(usage_msg)

