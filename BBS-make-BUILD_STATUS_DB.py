#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Oct 6, 2020
###

import sys
import os
import time

import bbs.parse
import BBSutils
import BBSvars
import BBSreportutils

def _read_status_from_summary_file(pkg, node_id, stage):
    summary_file = '%s.%s-summary.dcf' % (pkg, stage)
    summary_path = os.path.join('products-in', node_id, stage, summary_file)
    try:
        summary = bbs.parse.parse_DCF(summary_path, merge_records=True)
    except FileNotFoundError:
        status = 'NA'
    else:
        status = summary['Status']
    return status

def _write_status_to_BUILD_STATUS_DB(out, pkg, node_id, stage, status):
    out.write('%s#%s#%s: %s\n' % (pkg, node_id, stage, status))
    return

def _write_pkg_results_to_BUILD_STATUS_DB(pkg, out):
    for node in BBSreportutils.supported_nodes(pkg):
        # INSTALL status
        if BBSvars.subbuilds != 'bioc-longtests':
            stage = 'install'
            status = _read_status_from_summary_file(pkg, node.node_id, stage)
            _write_status_to_BUILD_STATUS_DB(out, pkg, node.node_id, stage,
                                             status)
        # BUILD status
        stage = 'buildsrc'
        status = _read_status_from_summary_file(pkg, node.node_id, stage)
        _write_status_to_BUILD_STATUS_DB(out, pkg, node.node_id, stage,
                                         status)
        skipped_is_OK = status in ['TIMEOUT', 'ERROR']
        # CHECK status
        if BBSvars.subbuilds not in ['workflows', 'books']:
            stage = 'checksrc'
            if skipped_is_OK:
                status = 'skipped'
            else:
                status = _read_status_from_summary_file(pkg, node.node_id,
                                                        stage)
            _write_status_to_BUILD_STATUS_DB(out, pkg, node.node_id, stage,
                                             status)
        # BUILD BIN status
        if BBSreportutils.is_doing_buildbin(node):
            stage = 'buildbin'
            if skipped_is_OK:
                status = 'skipped'
            else:
                status = _read_status_from_summary_file(pkg, node.node_id,
                                                        stage)
            _write_status_to_BUILD_STATUS_DB(out, pkg, node.node_id, stage,
                                             status)
    return

def make_BUILD_STATUS_DB(pkgs):
    print('BBS> Writing %s ...' % BBSreportutils.BUILD_STATUS_DB_file, end=' ')
    sys.stdout.flush()
    out = open(BBSreportutils.BUILD_STATUS_DB_file, 'w')
    for pkg in pkgs:
        _write_pkg_results_to_BUILD_STATUS_DB(pkg, out)
    out.close()
    print('OK')
    return

##############################################################################
### MAIN SECTION
##############################################################################

if __name__ == "__main__":
    print()
    if not os.path.isdir('products-in'):
        print('mmh.. I don\'t see the \'products-in\' subdirectory ' + \
              'in the current directory!')
        print('Make sure to be in \'%s/\' ' % BBSvars.Central_rdir.path)
        print('before running the BBS-make-BUILD_STATUS_DB.py script.')
        sys.exit('=> EXIT.')
    print('BBS> ==============================================================')
    print('BBS> [stage6a] STARTING stage6a at %s...' % time.asctime())
    sys.stdout.flush()
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    BBSreportutils.set_NODES(report_nodes)
    pkgs = bbs.parse.get_meat_packages(BBSutils.meat_index_file)
    make_BUILD_STATUS_DB(pkgs)
    print('BBS> [stage6a] DONE at %s.' % time.asctime())

