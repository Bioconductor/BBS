#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Authors:
###   Andrzej Oleś <andrzej.oles@embl.de>
###   Hervé Pagès <hpages.on.github@gmail.com>
###
### Last modification: Nov 5, 2019
###
### bbs.gitutils module
###

import sys
import os
import re
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
import fileutils

### 'out_path' must be the path to file where to capture stdout. If 'wd' is
### specified and 'out_path' is specified as a relative path, then 'out_path'
### will be treated as relative to 'wd'.
def _run(cmd, wd=None, out_path=None, prompt=''):
    if wd != None:
        previous_wd = os.getcwd()
        print('%scd %s' % (prompt, wd))
        os.chdir(wd)
    cmd2 = cmd
    if out_path != None:
        cmd2 += ' >%s' % out_path
        out = open(out_path, 'w')
    else:
        out = None
    print('%s%s' % (prompt, cmd2))
    sys.stdout.flush()
    try:
        ## Nasty things (that I don't really understand) can happen with
        ## subprocess.run() if this code is runned by the Task Scheduler
        ## on Windows (the child process tends to almost always return an
        ## error). Apparently using 'stderr=subprocess.STDOUT' fixes this pb.
        subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, shell=True,
                       check=True)
    except subprocess.CalledProcessError as e:
        run_error = e
    else:
        run_error = None
    if out_path != None:
        out.close()
    if wd != None:
        print('%scd %s' % (prompt, previous_wd))
        sys.stdout.flush()
        os.chdir(previous_wd)
    print()
    if run_error != None:
        raise run_error
    return

def _create_clone(clone_path, repo_url, branch=None, depth=None):
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    cmd = '%s clone' % git_cmd
    if branch != None:
        cmd += ' --branch %s' % branch
    if depth != None:
        cmd += ' --depth %s' % depth
    cmd = '%s %s %s' % (cmd, repo_url, clone_path)
    _run(cmd, prompt='bbs.gitutils._create_clone> ')
    return

def _new_commits_were_pulled(pull_output_path):
    p = re.compile('Already up.to.date')
    out = open(pull_output_path, 'r')
    first_line = out.readline()
    return p.match(first_line.strip()) == None

def _update_clone(clone_path, undo_changes=False, branch=None,
                  snapshot_date=None):
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    if undo_changes:
        cmd = '%s checkout -f' % git_cmd
        _run(cmd, wd=clone_path, prompt='bbs.gitutils._update_clone> ')
    if branch != None:
        ## checkout branch
        cmd = '%s checkout %s' % (git_cmd, branch)
        _run(cmd, wd=clone_path, prompt='bbs.gitutils._update_clone> ')
    if snapshot_date == None:
        cmd = '%s pull' % git_cmd
        out_file = '.git_pull_output.txt'
        _run(cmd, wd=clone_path, out_path=out_file,
             prompt='bbs.gitutils._update_clone> ')
        return _new_commits_were_pulled(os.path.join(clone_path, out_file))
    ## If 'snapshot_date' was supplied we fetch instead of pull so we can
    ## then merge up to snapshot date.
    cmd = '%s fetch' % git_cmd
    out_file = '.git_fetch_output.txt'
    _run(cmd, wd=clone_path, out_path=out_file,
         prompt='bbs.gitutils._update_clone> ')
    ## Andrzej: merge only up to snapshot date
    ##          (see https://stackoverflow.com/a/8223166/2792099)
    ## Hervé: That doesn't seem to work reliably. Switching to a
    ## simple 'git merge' for now...
    #cmd = '%s merge `%s rev-list -n 1 --before="%s" %s`' % (git_cmd, git_cmd, snapshot_date, branch)
    cmd = '%s merge' % git_cmd
    out_file = '.git_merge_output.txt'
    _run(cmd, wd=clone_path, out_path=out_file,
         prompt='bbs.gitutils._update_clone> ')
    return _new_commits_were_pulled(os.path.join(clone_path, out_file))

def update_git_clone(clone_path, repo_url, branch=None, depth=None,
                     undo_changes=False, snapshot_date=None,
                     reclone_if_update_fails=False):
    if os.path.exists(clone_path):
        try:
            branch_has_changed = _update_clone(clone_path, undo_changes, branch,
                                               snapshot_date)
        except subprocess.CalledProcessError as e:
            if not reclone_if_update_fails:
                raise e
            print()
            print("bbs.gitutils.update_git_clone> _update_clone() failed " +
                  "with error code %d!" % e.returncode)
            print("bbs.gitutils.update_git_clone> ==> will try to re-create " +
                  "git clone from scratch ...")
            print("bbs.gitutils.update_git_clone> rm -r %s" % clone_path)
            fileutils.nuke_tree(clone_path)
            print()
        else:
            return branch_has_changed
    _create_clone(clone_path, repo_url, branch, depth)
    return False

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

