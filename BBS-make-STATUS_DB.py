#! /usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Feb 5, 2015
###

import sys
import os
import time
import urllib2

import BBScorevars
import BBSreportutils

def get_status_from_summary_file(pkg, node_id, stagecmd):
    file = "%s.%s-summary.dcf" % (pkg, stagecmd)
    rdir = BBScorevars.nodes_rdir.subdir('%s/%s' % (node_id, stagecmd))
    try:
        status = BBSreportutils.WReadDcfVal(rdir, file, 'Status')
    except urllib2.HTTPError:
        if stagecmd == "install":
            return "NotNeeded"
        print "==> FATAL ERROR: cannot get %s status for package %s on %s" % (stagecmd, pkg, node_id)
        sys.exit("==> EXIT")
    return status

def make_STATUS_DB(allpkgs):
    print "BBS> [make_STATUS_DB] BEGIN..."
    out = open(BBSreportutils.STATUS_DB_file, 'w')
    for pkg in allpkgs:
        for node in BBSreportutils.supported_nodes(pkg):
            # INSTALL status
            stagecmd = 'install'
            status = get_status_from_summary_file(pkg, node.id, stagecmd)
            out.write('%s#%s#%s: %s\n' % (pkg, node.id, stagecmd, status))
            # BUILD status
            stagecmd = 'buildsrc'
            status = get_status_from_summary_file(pkg, node.id, stagecmd)
            out.write('%s#%s#%s: %s\n' % (pkg, node.id, stagecmd, status))
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]
            # CHECK status
            stagecmd = 'checksrc'
            if skipped_is_OK:
                status = "skipped"
            else:
                status = get_status_from_summary_file(pkg, node.id, stagecmd)
            out.write('%s#%s#%s: %s\n' % (pkg, node.id, stagecmd, status))
            if BBSreportutils.is_doing_buildbin(node):
                # BUILD BIN status
                stagecmd = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = get_status_from_summary_file(pkg, node.id, stagecmd)
                out.write('%s#%s#%s: %s\n' % (pkg, node.id, stagecmd, status))
    out.close()
    print "BBS> [make_STATUS_DB] END"
    return


##############################################################################
### MAIN SECTION
##############################################################################

print "BBS> [stage7a] STARTING stage7a at %s..." % time.asctime()

central_rdir_path = BBScorevars.Central_rdir.path
if central_rdir_path != None:
    print "BBS> [stage7a] cd %s/" % central_rdir_path
    os.chdir(central_rdir_path)

report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
BBSreportutils.set_NODES(report_nodes)
allpkgs = BBSreportutils.get_pkgs_from_meat_index()
make_STATUS_DB(allpkgs)

print "BBS> [stage7a] DONE at %s." % time.asctime()

