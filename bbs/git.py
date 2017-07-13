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
### Last modification: Jul 11, 2017
###
### git module
###

import os
import jobs

def update_git_clone(clone_path, repo_url, branch=None, snapshot_date=None):
    try:
        git_cmd = os.environ['BBS_GIT_CMD']
    except KeyError:
        git_cmd = 'git'
    if not os.path.exists(clone_path):
        cmd = '%s clone --depth 1' % git_cmd
        if branch != None:
            cmd += ' --branch %s' % branch
        cmd = '%s %s %s' % (cmd, repo_url, clone_path)
        print "bbs.git.update_git_clone> %s" % cmd
        jobs.doOrDie(cmd)
        print ""
        return
    old_cwd = os.getcwd()
    print "bbs.git.update_git_clone> cd %s" % clone_path
    os.chdir(clone_path)
    print ""
    if branch != None:
        ## checkout branch
        cmd = '%s checkout %s' % (git_cmd, branch)
        print "bbs.git.update_git_clone> %s" % cmd
        jobs.doOrDie(cmd)
        print ""
    if snapshot_date == None:
        cmd = '%s pull' % git_cmd
    else:
        ## we fetch instead of pull so we can then merge up to snapshot
        ## date (see below)
        cmd = '%s fetch' % git_cmd
    print "bbs.git.update_git_clone> %s" % cmd
    jobs.doOrDie(cmd)
    print ""
    if snapshot_date != None:
        ## merge only up to snapshot date
        ## (see https://stackoverflow.com/a/8223166/2792099)
        cmd = '%s merge `%s rev-list -n 1 --before="%s" %s`' % (git_cmd, git_cmd, snapshot_date, branch)
        print "bbs.git.update_git_clone> %s" % cmd
        jobs.doOrDie(cmd)
        print ""
    os.chdir(old_cwd)
    return

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

