#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: May 18, 2018
###

import sys
import os
import time

import bbs.rdir
import BBScorevars
import BBSreportutils

def get_status_from_summary_file(pkg, node_id, stage):
    file = "%s.%s-summary.dcf" % (pkg, stage)
    rdir = BBScorevars.nodes_rdir.subdir('%s/%s' % (node_id, stage))
    try:
        status = BBSreportutils.WReadDcfVal(rdir, file, 'Status')
    except bbs.rdir.WOpenError:
        if stage == "install":
            return "NotNeeded"
        return "NA"
    return status

def make_STATUS_DB(allpkgs):
    print("BBS> [make_STATUS_DB] BEGIN...")
    out = open(BBSreportutils.STATUS_DB_file, 'w')
    for pkg in allpkgs:
        for node in BBSreportutils.supported_nodes(pkg):

            # INSTALL status
            if BBScorevars.subbuilds != "bioc-longtests":
                stage = 'install'
                status = get_status_from_summary_file(pkg, node.id, stage)
                out.write('%s#%s#%s: %s\n' % (pkg, node.id, stage, status))

            # BUILD status
            stage = 'buildsrc'
            status = get_status_from_summary_file(pkg, node.id, stage)
            out.write('%s#%s#%s: %s\n' % (pkg, node.id, stage, status))
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]

            # CHECK status
            if BBScorevars.subbuilds != "workflows":
                stage = 'checksrc'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = get_status_from_summary_file(pkg, node.id, stage)
                out.write('%s#%s#%s: %s\n' % (pkg, node.id, stage, status))

            # BUILD BIN status
            if BBSreportutils.is_doing_buildbin(node):
                stage = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = get_status_from_summary_file(pkg, node.id, stage)
                out.write('%s#%s#%s: %s\n' % (pkg, node.id, stage, status))
    out.close()
    print("BBS> [make_STATUS_DB] END")
    return


##############################################################################
### MAIN SECTION
##############################################################################

print("BBS> [stage7a] STARTING stage7a at %s..." % time.asctime())

central_rdir_path = BBScorevars.Central_rdir.path
if central_rdir_path != None:
    print("BBS> [stage7a] cd %s/" % central_rdir_path)
    os.chdir(central_rdir_path)

report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
BBSreportutils.set_NODES(report_nodes)
allpkgs = BBSreportutils.get_pkgs_from_meat_index()
make_STATUS_DB(allpkgs)

print("BBS> [stage7a] DONE at %s." % time.asctime())

