#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Authors:
###   Andrzej Oleś <andrzej.oles@embl.de>
###   Hervé Pagès <hpages@fredhutch.org>
###
### Last modification: May 08, 2018
###
### gitutils module
###

import sys
import os
import jobs
import fileutils

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
    print "bbs.gitutils._create_clone> %s" % cmd
    jobs.doOrDie(cmd)
    print ""
    return

def _update_clone(clone_path, repo_url, branch=None, snapshot_date=None):
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    old_cwd = os.getcwd()
    print "bbs.gitutils._update_clone> cd %s" % clone_path
    os.chdir(clone_path)
    print ""
    if branch != None:
        ## checkout branch
        cmd = '%s checkout %s' % (git_cmd, branch)
        print "bbs.gitutils._update_clone> %s" % cmd
        retcode = jobs.call(cmd)
        if retcode != 0:
            print "bbs.gitutils._update_clone> cd %s" % old_cwd
            os.chdir(old_cwd)
            return retcode
        print ""
    if snapshot_date == None:
        cmd = '%s pull' % git_cmd
    else:
        ## we fetch instead of pull so we can then merge up to snapshot
        ## date (see below)
        cmd = '%s fetch' % git_cmd
    print "bbs.gitutils._update_clone> %s" % cmd
    retcode = jobs.call(cmd)
    if retcode != 0:
        print "bbs.gitutils._update_clone> cd %s" % old_cwd
        os.chdir(old_cwd)
        return retcode
    print ""
    if snapshot_date != None:
        ## Andrzej: merge only up to snapshot date
        ##          (see https://stackoverflow.com/a/8223166/2792099)
        ## Hervé: That doesn't seem to work reliably. Switching to a
        ## simple 'git merge' for now...
        #cmd = '%s merge `%s rev-list -n 1 --before="%s" %s`' % (git_cmd, git_cmd, snapshot_date, branch)
        cmd = '%s merge' % git_cmd
        print "bbs.gitutils._update_clone> %s" % cmd
        retcode = jobs.call(cmd)
        if retcode != 0:
            print "bbs.gitutils._update_clone> cd %s" % old_cwd
            os.chdir(old_cwd)
            return retcode
        print ""
    print "bbs.gitutils._update_clone> cd %s" % old_cwd
    os.chdir(old_cwd)
    return 0

def update_git_clone(clone_path, repo_url, branch=None, depth=None, snapshot_date=None, reclone_if_update_fails=False):
    if os.path.exists(clone_path):
        retcode = _update_clone(clone_path, repo_url, branch, snapshot_date)
        if retcode == 0:
            return
        print ""
        print "bbs.gitutils.update_git_clone> _update_clone() failed " + \
              "with error code %d!" % retcode
        if not reclone_if_update_fails:
            sys.exit("bbs.gitutils.update_git_clone> EXIT")
        print "bbs.gitutils.update_git_clone> ==> will try to re-create " + \
              "git clone from scratch ..."
        print "bbs.gitutils.update_git_clone> rm -r %s" % clone_path
        fileutils.nuke_tree(clone_path)
        print ""
    _create_clone(clone_path, repo_url, branch, depth)
    return

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

