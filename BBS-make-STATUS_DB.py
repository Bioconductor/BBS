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

import bbs.parse
import BBScorevars
import BBSreportutils

def _read_status_from_summary_file(pkg, node_id, stage):
    summary_file = '%s.%s-summary.dcf' % (pkg, stage)
    summary_path = os.path.join('nodes', node_id, stage, summary_file)
    try:
        summary = bbs.parse.parse_DCF(summary_path, merge_records=True)
    except FileNotFoundError:
        status = 'NA'
    else:
        status = summary['Status']
    return status

def _write_status_to_STATUS_DB(out, pkg, node_id, stage, status):
    out.write('%s#%s#%s: %s\n' % (pkg, node_id, stage, status))
    return

def _write_pkg_results_to_STATUS_DB(pkg, out):
    for node in BBSreportutils.supported_nodes(pkg):
        # INSTALL status
        if BBScorevars.subbuilds != 'bioc-longtests':
            stage = 'install'
            status = _read_status_from_summary_file(pkg, node.id, stage)
            _write_status_to_STATUS_DB(out, pkg, node.id, stage, status)
        # BUILD status
        stage = 'buildsrc'
        status = _read_status_from_summary_file(pkg, node.id, stage)
        _write_status_to_STATUS_DB(out, pkg, node.id, stage, status)
        skipped_is_OK = status in ['TIMEOUT', 'ERROR']
        # CHECK status
        if BBScorevars.subbuilds not in ['workflows', 'books']:
            stage = 'checksrc'
            if skipped_is_OK:
                status = 'skipped'
            else:
                status = _read_status_from_summary_file(pkg, node.id, stage)
            _write_status_to_STATUS_DB(out, pkg, node.id, stage, status)
        # BUILD BIN status
        if BBSreportutils.is_doing_buildbin(node):
            stage = 'buildbin'
            if skipped_is_OK:
                status = 'skipped'
            else:
                status = _read_status_from_summary_file(pkg, node.id, stage)
            _write_status_to_STATUS_DB(out, pkg, node.id, stage, status)
    return

def make_STATUS_DB(allpkgs):
    print('BBS> Writing %s ...' % BBSreportutils.STATUS_DB_file, end=' ')
    sys.stdout.flush()
    out = open(BBSreportutils.STATUS_DB_file, 'w')
    for pkg in allpkgs:
        _write_pkg_results_to_STATUS_DB(pkg, out)
    out.close()
    print('OK')
    return

##############################################################################
### MAIN SECTION
##############################################################################

if __name__ == "__main__":
    print()
    if not os.path.isdir('nodes'):
        print('mmh.. I don\'t see the \'nodes\' subdirectory ' + \
              'in the current directory!')
        print('Make sure to be in \'%s/\' ' % BBScorevars.Central_rdir.path)
        print('before running the BBS-make-STATUS_DB.py script.')
        sys.exit('=> EXIT.')
    print('BBS> ==============================================================')
    print('BBS> [stage7a] STARTING stage7a at %s...' % time.asctime())
    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    BBSreportutils.set_NODES(report_nodes)
    allpkgs = BBSreportutils.get_pkgs_from_meat_index()
    make_STATUS_DB(allpkgs)
    print('BBS> [stage7a] DONE at %s.' % time.asctime())

