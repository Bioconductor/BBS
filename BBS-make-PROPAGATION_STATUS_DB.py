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

import bbs.notify

import BBSutils
import BBSvars
import BBSbase

def make_PROPAGATION_STATUS_DB(final_repo):
    Rfunction = 'makePropagationStatusDb'
    OUTGOING_dir = 'OUTGOING'
    db_filepath = 'PROPAGATION_STATUS_DB.txt'
    script_path = os.path.join(BBSvars.BBS_home,
                               "utils",
                               "makePropagationStatusDb.R")
    Rexpr = "source('%s');%s('%s','%s',db_filepath='%s')" % \
            (script_path, Rfunction, OUTGOING_dir, final_repo, db_filepath)
    cmd = BBSbase.Rexpr2syscmd(Rexpr)
    ## Nasty things (that I don't really understand) can happen with
    ## subprocess.run() if this code is runned by the Task Scheduler
    ## on Windows (the child process tends to almost always return an
    ## error). Apparently using 'stderr=subprocess.STDOUT' fixes this pb.
    try:
        subprocess.run(cmd, stdout=None, stderr=subprocess.STDOUT, shell=True,
                       check=True)
    except subprocess.CalledProcessError as e:
        subject = (f"[BBS] {BBSvars.bioc_version} {BBSvars.buildtype} Postrun "
                   f"Failure")
        msg_body = f"""\
        Postrun failed on the BBS with the following error:

        Error: {e}"""
        bbs.notify.mode = "do-it"
        bbs.notify.sendtextmail("BBS-noreply@bioconductor.org",
                                ["maintainer@bioconductor.org"],
                                subject,
                                msg_body)
        raise e
    return

##############################################################################
### MAIN SECTION
##############################################################################

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc > 1:
        final_repo = sys.argv[1]
    else:
        final_repo = BBSutils.getenv('BBS_FINAL_REPO')
    print()
    if not os.path.isdir('OUTGOING'):
        print('mmh.. I don\'t see the \'OUTGOING\' subdirectory ' + \
              'in the current directory!')
        print('Make sure to be in \'%s/\' ' % BBSvars.Central_rdir.path)
        print('before running the BBS-make-PROPAGATION_STATUS_DB.py script.')
        sys.exit('=> EXIT.')
    print('BBS> ==============================================================')
    print('BBS> [stage6c] STARTING stage6c on %s...' % time.asctime())
    sys.stdout.flush()
    make_PROPAGATION_STATUS_DB(final_repo)
    print('BBS> [stage6c] DONE on %s.' % time.asctime())

