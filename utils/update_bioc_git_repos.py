#! /usr/bin/env python
##############################################################################

import sys
import os

import manifest
import git

gitserver = 'git.bioconductor.org'

home = os.path.expanduser('~')
manifest_git_clone = os.path.join(home, 'git.bioconductor.org', 'manifest')
manifest_git_repo_url = 'git@%s:admin/manifest.git' % gitserver

def update_packages(pkg_dir, pkgs, git_branch=None, skip=None):
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
        pkg_git_repo_url = 'git@%s:packages/%s.git' % (gitserver, pkg)
        git.update_git_clone(pkg_git_clone, pkg_git_repo_url, git_branch)
    return

def update_packages_in_current_working_dir(git_branch=None, skip=None):
    key = 'MANIFEST_FILE'
    print 'BBS> Environment variable %s is' % key,
    if key in os.environ and os.environ[key] != "":
        manifest_path = os.environ[key]
        print 'defined and set to:'
        print 'BBS>     %s' % manifest_path
        print 'BBS> ==> Using %s as manifest file...' % manifest_path
        pkgs = manifest.read(manifest_path)
        print 'BBS> Nb of packages listed in manifest file: %d' % len(pkgs)
    else:
        print 'NOT defined (or is set to '
        print 'BBS> the empty string).'
        print 'BBS> ==> Assuming all subdirs in current ' + \
              'directory are git repos'
        print 'BBS>     and updating them...'
        pkgs = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
        print 'BBS> Nb of subdirs in current directory: %d' % len(pkgs)
    print ''
    update_packages('.', pkgs, git_branch, skip)
    return

def update_manifest(git_branch=None):
    print 'BBS> ----------------------------------------------------------'
    print 'BBS> [update_manifest] branch: %s' % git_branch
    print ''
    git.update_git_clone(manifest_git_clone,
                         manifest_git_repo_url,
                         git_branch)
    return

def update_packages_from_manifest(pkg_dir, manifest_file,
                                  git_branch=None, skip=None):
    update_manifest(git_branch)
    manifest_path = os.path.join(manifest_git_clone, manifest_file)
    pkgs = manifest.read(manifest_path)
    update_packages(pkg_dir, pkgs, git_branch, skip)
    return

def update_software(git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'software')
    update_packages_from_manifest(pkg_dir, 'software.txt',
                                  git_branch, skip)
    return

def update_data_experiment(git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'data-experiment')
    update_packages_from_manifest(pkg_dir, 'data-experiment.txt',
                                  git_branch, skip)
    return

def update_workflows(git_branch=None, skip=None):
    pkg_dir = os.path.join(home, 'git.bioconductor.org', 'workflows')
    update_packages_from_manifest(pkg_dir, 'workflows.txt',
                                  git_branch, skip)
    return

if __name__ == '__main__':
    usage_msg = 'Usage:\n' + \
        '    update_bioc_git_repos.py\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [manifest|software|data-experiment|workflows]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [manifest|software|data-experiment|workflows] [master|RELEASE_3_6]\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment|workflows] <skip>\n' + \
        'or:\n' + \
        '    update_bioc_git_repos.py [software|data-experiment|workflows] [master|RELEASE_3_6] <skip>'
    argc = len(sys.argv)
    git_branch = skip = None
    if argc == 1:
        update_packages_in_current_working_dir()
        sys.exit()
    elif argc == 2:
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
    elif what == 'workflows':
        update_workflows(git_branch, skip)
    else:
        sys.exit(usage_msg)

