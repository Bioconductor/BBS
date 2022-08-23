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
import shutil

import bbs.fileutils
import bbs.parse
import bbs.jobs
import BBSutils
import BBSvars

def is_doing_buildbin(node_hostname):
    return BBSutils.getNodeSpec(node_hostname, 'pkgType') != "source"

def pkgMustBeRejected(node_hostname, node_id, pkg):
    nodes_path = BBSvars.products_in_rdir.path
    node_path = os.path.join(nodes_path, node_id)
    summary_file0 = "%s.%%s-summary.dcf" % pkg

    ## Extract Status from BUILD summary.
    buildsrc_path = os.path.join(node_path, 'buildsrc')
    summary_file = os.path.join(buildsrc_path, summary_file0 % 'buildsrc')
    ## Could happen that summary file is not available (because the node
    ## where that file is coming from didn't finish to build yet or failed
    ## to send the file back).
    try:
        dcf = open(summary_file, 'rb')
    except IOError:
        return True
    status = bbs.parse.get_next_DCF_val(dcf, 'Status')
    dcf.close()
    if status != 'OK':
        return True

    ## workflows and books buildtype exit here
    if BBSvars.buildtype in ["workflows", "books"]:
        return status != 'OK'

    ## Extract Status from CHECK summary.
    if BBSvars.buildtype in ["workflows", "books", "bioc-mac-arm64"]:
        checksrc_path = os.path.join(node_path, 'checksrc')
        summary_file = os.path.join(checksrc_path, summary_file0 % 'checksrc')
        try:
            dcf = open(summary_file, 'rb')
        except IOError:
            return True
        status = bbs.parse.get_next_DCF_val(dcf, 'Status')
        dcf.close()
        if status not in ["OK", "WARNINGS"]:
            return True

    if not is_doing_buildbin(node_hostname):
        return False

    ## Extract Status from BUILD BIN summary.
    buildbin_path = os.path.join(node_path, 'buildbin')
    summary_file = os.path.join(buildbin_path, summary_file0 % 'buildbin')
    try:
        dcf = open(summary_file, 'rb')
    except IOError:
        return True
    status = bbs.parse.get_next_DCF_val(dcf, 'Status')
    dcf.close()
    return status != 'OK'

def copy_outgoing_pkgs(fresh_pkgs_subdir, source_node):
    tmp = fresh_pkgs_subdir.split("/")
    if len(tmp) != 2:
        sys.exit("ERROR: Invalid relative path to fresh pkgs %s (must be of the form node/subdir)" % fresh_pkgs_subdir)
    node_id = tmp[0]
    node_hostname = node_id.split("-")[0]
    fileext = BBSutils.getNodeSpec(node_hostname, 'pkgFileExt')
    fresh_pkgs_subdir = os.path.join(BBSvars.products_in_rdir.path, fresh_pkgs_subdir)

    ## Workflow and book packages do not have manuals/ because we do not run
    ## `R CMD check`.
    manuals_dir = "../manuals"
    if BBSvars.buildtype in ["workflows", "books", "bioc-mac-arm64"]:
        pass
    elif source_node:
        print("BBS> [stage6b] mkdir %s" % manuals_dir)
        os.mkdir(manuals_dir)
    print("BBS> [stage6b] BEGIN copying outgoing packages from %s." % \
          fresh_pkgs_subdir)
    pkgType = BBSutils.getNodeSpec(node_hostname, 'pkgType')
    meat_index_path = os.path.join(BBSvars.Central_rdir.path,
                                   BBSutils.meat_index_file)
    pkgs = bbs.parse.get_meat_packages_for_node(meat_index_path,
                                                node_id, pkgType)
    meat_index = bbs.parse.get_meat_packages(meat_index_path, as_dict=True)
    for pkg in pkgs:
        if pkgMustBeRejected(node_hostname, node_id, pkg):
            continue
        dcf_record = meat_index[pkg]
        version = dcf_record['Version']
        ## Copy pkg from 'fresh_pkgs_subdir2'.
        pkg_file = "%s_%s.%s" % (pkg, version, fileext)
        pkg_path = os.path.join(fresh_pkgs_subdir, pkg_file)
        print("BBS> [stage6b]   - copying %s to OUTGOING folder ..." % pkg_path)
        if os.path.exists(pkg_path):
            #shutil.copy(pkg_path, ".")
            os.link(pkg_path, pkg_file)  # create hard link to avoid making a copy
        else:
            print("BBS> [stage6b]     SKIPPED (file %s doesn't exist)" % pkg_path)
        ## Get reference manual from pkg.Rcheck directory.
        if BBSvars.buildtype in ["workflows", "books", "bioc-mac-arm64"]:
            pass
        elif source_node:
            pdf_file = os.path.join(BBSutils.getenv('BBS_WORK_TOPDIR'),
                                    "meat",
                                    "%s.Rcheck" % pkg,
                                    "%s-manual.pdf" % pkg)
            print("BBS> [stage6b]   - copying %s manual to OUTGOING/manuals folder..." % pkg)
            if os.path.exists(pdf_file):
                dst = os.path.join(manuals_dir, "%s.pdf" % pkg)
                #shutil.copy(pdf_file, dst)
                os.link(pdf_file, dst) # create hard link to avoid making a copy
            else:
                print("BBS> [stage6b]     SKIPPED (file %s doesn't exist)" % pdf_file)
    print("BBS> [stage6b] END copying outgoing packages from %s." % fresh_pkgs_subdir)
    return

def stage6_make_OUTGOING():
    ## Create working directory
    OUTGOING_dir = os.path.join(BBSvars.Central_rdir.path, "OUTGOING")
    print("BBS> [stage6b] remake_dir %s" % OUTGOING_dir)
    bbs.fileutils.remake_dir(OUTGOING_dir)
    ## Loop over each element of the OUTGOING map
    OUTGOING_map = BBSutils.getenv('BBS_OUTGOING_MAP')
    map_elts = OUTGOING_map.split(" ")
    for map_elt in map_elts:
        tmp = map_elt.split(":")
        if len(tmp) != 2:
            sys.exit("ERROR: Invalid OUTGOING map element %s" % map_elt)
        source_node = False
        if tmp[0] == "source":
            source_node = True
        OUTGOING_subdir = os.path.join(OUTGOING_dir, tmp[0])
        print("BBS> [stage6b] mkdir %s" % OUTGOING_subdir)
        os.mkdir(OUTGOING_subdir)
        print("BBS> [stage6b] cd %s/" % OUTGOING_subdir)
        os.chdir(OUTGOING_subdir)
        copy_outgoing_pkgs(tmp[1], source_node)
    return


##############################################################################
### MAIN SECTION
##############################################################################


print()
print("BBS> ==================================================================")
print("BBS> [stage6b] STARTING stage6b on %s..." % time.asctime())
sys.stdout.flush()

stage6_make_OUTGOING()

print("BBS> [stage6b] DONE on %s." % time.asctime())

