#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Authors:
###   Andrzej Oleś <andrzej.oles@embl.de>
###   Hervé Pagès <hpages.on.github@gmail.com>
###
### Last modification: Nov 19, 2021
###
### bbs.gitutils module
###

import sys
import os
import re
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
import fileutils
import jobs

try:
    _git_cmd = os.environ['BBS_GIT_CMD']
except KeyError:
    _git_cmd = 'git'

verbose = True

def _print_msg(msg):
    if verbose:
        print(msg)
        sys.stdout.flush()
    return

### 'out_path' must be the path to file where to capture stdout. If 'cwd' is
### specified and 'out_path' is specified as a relative path, then 'out_path'
### will be treated as relative to 'cwd'.
def _run(cmd, cwd=None, out_path=None, prompt=''):
    if cwd != None:
        previous_cwd = os.getcwd()
        _print_msg('%scd %s' % (prompt, cwd))
        os.chdir(cwd)
    cmd2 = cmd
    if out_path != None:
        cmd2 += ' >%s' % out_path
        out = open(out_path, 'w')
    else:
        out = None
    _print_msg('%s%s' % (prompt, cmd2))
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
        _print_msg('%scd %s' % (prompt, previous_cwd))
        os.chdir(previous_cwd)
    _print_msg('')
    if run_error != None:
        raise run_error
    return

def _run_gitcmd(gitcmd, cwd=None, out_path=None, prompt=''):
    cmd = '%s %s' % (_git_cmd, gitcmd)
    _run(cmd, cwd=cwd, out_path=out_path, prompt=prompt)
    return

def _clone_repo(repo_path, repo_url, branch=None, depth=None):
    gitcmd = 'clone'
    if branch != None:
        gitcmd += ' --branch %s' % branch
    if depth != None:
        gitcmd += ' --depth %s' % depth
    gitcmd = '%s %s %s' % (gitcmd, repo_url, repo_path)
    _run_gitcmd(gitcmd, prompt='bbs.gitutils._clone_repo> ')
    return

def _try_hard_to_clone_repo(repo_path, repo_url, branch=None, depth=None,
                            nb_attempts=10):
    prompt = 'bbs.gitutils._try_hard_to_clone_repo> '
    if os.path.exists(repo_path):
        _print_msg('%srm -r %s' % (prompt, repo_path))
        fileutils.nuke_tree(repo_path)
        _print_msg('')
    attempt_count = 0
    while True:
        attempt_count += 1
        try:
            _clone_repo(repo_path, repo_url, branch, depth)
        except subprocess.CalledProcessError as e:
            _print_msg('%s%s() failed with error code %d!' % \
                       (prompt, '_clone_repo', e.returncode))
            if attempt_count == nb_attempts:
                _print_msg('%s==> giving up after %d attempts.' % \
                           (prompt, attempt_count))
                raise e
            _print_msg('%s==> will wait 5 seconds before trying again...' % \
                       prompt)
            jobs.sleep(5.0)
            _print_msg('')
        else:
            break
    return

def is_git_repo(repo_path):
    global verbose
    old_verbose = verbose
    verbose = False
    gitcmd = 'status --porcelain'
    try:
        _run_gitcmd(gitcmd, cwd=repo_path)
    except subprocess.CalledProcessError:
        ok = False
    else:
        ok = True
    verbose = old_verbose
    return ok

def _repo_has_local_changes(repo_path):
    prompt = 'bbs.gitutils._repo_has_local_changes> '
    gitcmd = 'status --porcelain'
    out_file = '.git_status_output.txt'
    _run_gitcmd(gitcmd, cwd=repo_path, out_path=out_file, prompt=prompt)
    status_output_path = os.path.join(repo_path, out_file)
    out = open(status_output_path, 'r')
    first_line = out.readline()
    out.close()
    _print_msg('%srm %s' % (prompt, status_output_path))
    os.remove(status_output_path)
    return len(first_line) != 0 and first_line[0] != '?'

def _new_commits_pulled(pull_output_path):
    p = re.compile('Already up.to.date')
    out = open(pull_output_path, 'r')
    first_line = out.readline()
    out.close()
    return p.match(first_line.strip()) == None

def _pull_repo(repo_path, branch=None, cleanup=False):
    prompt = 'bbs.gitutils._pull_repo> '
    if branch != None:
        ## checkout branch
        gitcmd = 'checkout %s' % branch
        _run_gitcmd(gitcmd, cwd=repo_path, prompt=prompt)
    gitcmd = 'pull'
    out_file = '.git_pull_output.txt'
    _run_gitcmd(gitcmd, cwd=repo_path, out_path=out_file, prompt=prompt)
    pull_output_path = os.path.join(repo_path, out_file)
    new_commits_pulled = _new_commits_pulled(pull_output_path)
    if cleanup:
        _print_msg('%srm %s' % (prompt, pull_output_path))
        os.remove(pull_output_path)
    return new_commits_pulled

def _fetch_and_merge_repo(repo_path, branch=None, snapshot_date=None,
                          cleanup=False):
    prompt = 'bbs.gitutils._fetch_and_merge_repo> '
    if branch != None:
        ## checkout branch
        gitcmd = 'checkout %s' % branch
        _run_gitcmd(gitcmd, cwd=repo_path, prompt=prompt)
    gitcmd = 'fetch'
    #out_file = '.git_fetch_output.txt'
    #_run_gitcmd(gitcmd, cwd=repo_path, out_path=out_file, prompt=prompt)
    _run_gitcmd(gitcmd, cwd=repo_path, prompt=prompt)
    if snapshot_date == None:
        gitcmd = 'merge'
    else:
        ## Andrzej: merge only up to snapshot date
        ##          (see https://stackoverflow.com/a/8223166/2792099)
        ## Hervé: That doesn't seem to work reliably. Switching to a
        ## simple 'git merge' for now...
        #gitcmd = 'merge `%s rev-list -n 1 --before="%s" %s`' % (_git_cmd, snapshot_date, branch)
        gitcmd = 'merge'
    out_file = '.git_merge_output.txt'
    _run_gitcmd(gitcmd, cwd=repo_path, out_path=out_file, prompt=prompt)
    merge_output_path = os.path.join(repo_path, out_file)
    new_commits_pulled = _new_commits_pulled(merge_output_path)
    if cleanup:
        _print_msg('%srm %s' % (prompt, merge_output_path))
        os.remove(merge_output_path)
    return new_commits_pulled

def clone_or_pull_repo(repo_path, repo_url, branch=None, depth=None,
                       discard_changes=False, snapshot_date=None,
                       reclone_if_pull_fails=False,
                       cleanup=False):
    prompt = 'bbs.gitutils.clone_or_pull_repo> '
    if discard_changes:
        gitcmd = 'checkout -f'
        _run_gitcmd(gitcmd, cwd=repo_path, prompt=prompt)
    if os.path.exists(repo_path):
        ## Try to pull or fetch+merge.
        try:
            if snapshot_date == None:
                what = '_pull_repo'
                branch_has_changed = _pull_repo(repo_path, branch, cleanup)
            else:
                what = '_fetch_and_merge_repo'
                branch_has_changed = _fetch_and_merge_repo(repo_path, branch,
                                                snapshot_date, cleanup)
        except subprocess.CalledProcessError as e:
            if not reclone_if_pull_fails:
                raise e
            _print_msg('')
            _print_msg('%s%s() failed with error code %d!' % \
                       (prompt, what, e.returncode))
            _print_msg('%s==> will try to re-clone ...' % prompt)
        else:
            return branch_has_changed
    ## Now try to clone.
    _try_hard_to_clone_repo(repo_path, repo_url, branch, depth)
    return True

def collect_git_clone_meta(repo_path, out_path, snapshot_date):
    previous_cwd = os.getcwd()
    os.chdir(repo_path)

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

