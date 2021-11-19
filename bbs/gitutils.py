#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Authors:
###   Andrzej Oleś <andrzej.oles@embl.de>
###   Hervé Pagès <hpages.on.github@gmail.com>
###
### Last modification: Jan 24, 2021
###
### bbs.gitutils module
###

import sys
import os
import re
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
import fileutils

try:
    _git_cmd = os.environ['BBS_GIT_CMD']
except KeyError:
    _git_cmd = 'git'

### 'out_path' must be the path to file where to capture stdout. If 'cwd' is
### specified and 'out_path' is specified as a relative path, then 'out_path'
### will be treated as relative to 'cwd'.
def _run(cmd, cwd=None, out_path=None, prompt=''):
    if cwd != None:
        previous_cwd = os.getcwd()
        print('%scd %s' % (prompt, cwd))
        os.chdir(cwd)
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
    if cwd != None:
        print('%scd %s' % (prompt, previous_cwd))
        sys.stdout.flush()
        os.chdir(previous_cwd)
    print()
    if run_error != None:
        raise run_error
    return

def _run_gitcmd(gitcmd, cwd=None, out_path=None, prompt=''):
    cmd = '%s %s' % (_git_cmd, gitcmd)
    _run(cmd, cwd=cwd, out_path=out_path, prompt=prompt)
    return

def _clone_repo(clone_path, repo_url, branch=None, depth=None):
    gitcmd = 'clone'
    if branch != None:
        gitcmd += ' --branch %s' % branch
    if depth != None:
        gitcmd += ' --depth %s' % depth
    gitcmd = '%s %s %s' % (gitcmd, repo_url, clone_path)
    _run_gitcmd(gitcmd, prompt='bbs.gitutils._clone_repo> ')
    return

def _new_commits_were_pulled(pull_output_path):
    p = re.compile('Already up.to.date')
    out = open(pull_output_path, 'r')
    first_line = out.readline()
    return p.match(first_line.strip()) == None

def _update_repo(clone_path, undo_changes=False, branch=None,
                 snapshot_date=None):
    if undo_changes:
        gitcmd = 'checkout -f'
        _run_gitcmd(gitcmd, cwd=clone_path, prompt='bbs.gitutils._update_repo> ')
    if branch != None:
        ## checkout branch
        gitcmd = 'checkout %s' % branch
        _run_gitcmd(gitcmd, cwd=clone_path, prompt='bbs.gitutils._update_repo> ')
    if snapshot_date == None:
        gitcmd = 'pull'
        out_file = '.git_pull_output.txt'
        _run_gitcmd(gitcmd, cwd=clone_path, out_path=out_file,
                    prompt='bbs.gitutils._update_repo> ')
        return _new_commits_were_pulled(os.path.join(clone_path, out_file))
    ## If 'snapshot_date' was supplied we fetch instead of pull so we can
    ## then merge up to snapshot date.
    gitcmd = 'fetch'
    out_file = '.git_fetch_output.txt'
    _run_gitcmd(gitcmd, cwd=clone_path, out_path=out_file,
                prompt='bbs.gitutils._update_repo> ')
    ## Andrzej: merge only up to snapshot date
    ##          (see https://stackoverflow.com/a/8223166/2792099)
    ## Hervé: That doesn't seem to work reliably. Switching to a
    ## simple 'git merge' for now...
    #gitcmd = 'merge `%s rev-list -n 1 --before="%s" %s`' % (_git_cmd, snapshot_date, branch)
    gitcmd = 'merge'
    out_file = '.git_merge_output.txt'
    _run_gitcmd(gitcmd, cwd=clone_path, out_path=out_file,
                prompt='bbs.gitutils._update_repo> ')
    return _new_commits_were_pulled(os.path.join(clone_path, out_file))

def clone_or_update_repo(clone_path, repo_url, branch=None, depth=None,
                         undo_changes=False, snapshot_date=None,
                         reclone_if_update_fails=False):
    if os.path.exists(clone_path):
        try:
            branch_has_changed = _update_repo(clone_path, undo_changes, branch,
                                              snapshot_date)
        except subprocess.CalledProcessError as e:
            if not reclone_if_update_fails:
                raise e
            print()
            print("bbs.gitutils.clone_or_update_repo> _update_repo() failed " +
                  "with error code %d!" % e.returncode)
            print("bbs.gitutils.clone_or_update_repo> ==> will try to re-clone ...")
            print("bbs.gitutils.clone_or_update_repo> rm -r %s" % clone_path)
            fileutils.nuke_tree(clone_path)
            print()
        else:
            return branch_has_changed
    _clone_repo(clone_path, repo_url, branch, depth)
    return False

def collect_git_clone_meta(clone_path, out_path, snapshot_date):
    previous_cwd = os.getcwd()
    os.chdir(clone_path)

    ## Note that using 'capture_output=True' is equivalent to using
    ## 'stdout=subprocess.PIPE' and 'stderr=subprocess.PIPE'. However
    ## 'capture_output' was only introduced in Python 3.7 so we'll use
    ## the latter in the various calls to subprocess.run() below to remain
    ## compatible with older versions of Python (e.g. Ubuntu 18.04 has
    ## Python 3.6.9).
    ## Also 'text=True' is equivalent to 'universal_newlines=True' but
    ## we use the latter for the same reason.

    ## Get remote URL.
    cmd = '%s remote get-url origin' % _git_cmd
    ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True, universal_newlines=True)
    URL = ret.stdout

    ## Get branch.
    cmd = '%s rev-parse --abbrev-ref HEAD' % _git_cmd
    ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True, universal_newlines=True)
    Branch = ret.stdout

    ## Get Last Commit & Last Commit Date.
    gitlog_format = 'format:"git_last_commit: %h%ngit_last_commit_date: %ad%n"'
    date_format = 'format-local:"%%Y-%%m-%%d %%H:%%M:%%S %s (%%a, %%d %%b %%Y)"' % snapshot_date.split(' ')[2]
    cmd = '%s log --max-count=1 --date=%s --format=%s' % (_git_cmd, date_format, gitlog_format)
    ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True, universal_newlines=True)
    Last_Commit_and_Last_Commit_Date = ret.stdout
    os.chdir(previous_cwd)

    ## Dump meta as DCF file.
    out = open(out_path, 'w')
    out.write('git_url: %s' % URL)
    out.write('git_branch: %s' % Branch)
    out.write('%s' % Last_Commit_and_Last_Commit_Date)
    out.close()
    return

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

