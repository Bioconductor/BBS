#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: May 24, 2021
###

import sys
import os
import time
import subprocess

import BBSvars
import BBSbase

def make_PROPAGATION_STATUS_DB(staging_repo):
    Rfunction = 'makePropagationStatusDb'
    OUTGOING_dir = 'OUTGOING'
    db_filepath = 'PROPAGATION_STATUS_DB.txt'
    script_path = os.path.join(BBSvars.BBS_home,
                               "utils",
                               "makePropagationStatusDb.R")
    Rexpr = "source('%s');%s('%s','%s','%s')" % \
            (script_path, Rfunction, OUTGOING_dir, staging_repo, db_filepath)
    cmd = BBSbase.Rexpr2syscmd(Rexpr)
    ## Nasty things (that I don't really understand) can happen with
    ## subprocess.run() if this code is runned by the Task Scheduler
    ## on Windows (the child process tends to almost always return an
    ## error). Apparently using 'stderr=subprocess.STDOUT' fixes this pb.
    subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, shell=True,
                   check=True)
    return

##############################################################################
### MAIN SECTION
##############################################################################

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc > 1:
        staging_repo = sys.argv[1]
    else:
        staging_repo = os.environ['BBS_STAGING_REPO']
    print()
    if not os.path.isdir('OUTGOING\'):
        print('mmh.. I don\'t see the \'OUTGOING\' subdirectory ' + \
              'in the current directory!')
        print('Make sure to be in \'%s/\' ' % BBSvars.Central_rdir.path)
        print('before running the BBS-make-PROPAGATION_STATUS_DB.py script.')
        sys.exit('=> EXIT.')
    print('BBS> ==============================================================')
    print('BBS> [stage6bb] STARTING stage6bb at %s...' % time.asctime())
    make_PROPAGATION_STATUS_DB(staging_repo)
    print('BBS> [stage6bb] DONE at %s.' % time.asctime())

