#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
###

import sys
import os
import time
import shutil

import bbs.fileutils
import bbs.parse
import bbs.jobs
import BBScorevars
import BBSvars

def is_doing_buildbin(node_hostname):
    return BBScorevars.getNodeSpec(node_hostname, 'pkgType') != "source"

def pkgMustBeRejected(node_hostname, node_id, pkg):
    nodes_path = BBScorevars.nodes_rdir.path
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
    status = bbs.parse.getNextDcfVal(dcf, 'Status')
    dcf.close()
    if status != 'OK':
        return True

    ## workflows and books subbuilds exit here
    if BBScorevars.subbuilds in ["workflows", "books"]:
        return status != 'OK'

    ## Extract Status from CHECK summary.
    checksrc_path = os.path.join(node_path, 'checksrc')
    summary_file = os.path.join(checksrc_path, summary_file0 % 'checksrc')
    try:
        dcf = open(summary_file, 'rb')
    except IOError:
        return True
    status = bbs.parse.getNextDcfVal(dcf, 'Status')
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
    status = bbs.parse.getNextDcfVal(dcf, 'Status')
    dcf.close()
    return status != 'OK'

def copy_outgoing_pkgs(fresh_pkgs_subdir, source_node):
    tmp = fresh_pkgs_subdir.split("/")
    if len(tmp) != 2:
        sys.exit("ERROR: Invalid relative path to fresh pkgs %s (must be of the form node/subdir)" % fresh_pkgs_subdir)
    node_id = tmp[0]
    node_hostname = node_id.split("-")[0]
    fileext = BBScorevars.getNodeSpec(node_hostname, 'pkgFileExt')
    fresh_pkgs_subdir = os.path.join(BBScorevars.nodes_rdir.path, fresh_pkgs_subdir)

    ## Workflow and book packages do not have manuals/ because we do not run
    ## `R CMD check`.
    manuals_dir = "../manuals"
    if BBScorevars.subbuilds in ["workflows", "books"]:
        pass
    elif source_node:
        print("BBS> [stage6] mkdir %s" % manuals_dir)
        os.mkdir(manuals_dir)
    print("BBS> [stage6] BEGIN copying outgoing packages from %s." % fresh_pkgs_subdir)
    pkgType = BBScorevars.getNodeSpec(node_hostname, 'pkgType')
    meat_index_file = os.path.join(BBScorevars.Central_rdir.path, BBScorevars.meat_index_file)
    dcf = open(meat_index_file, 'rb')
    pkgs = bbs.parse.readPkgsFromDCF(dcf, node_id, pkgType)
    dcf.close()
    for pkg in pkgs:
        if pkgMustBeRejected(node_hostname, node_id, pkg):
            continue
        dcf = open(meat_index_file, 'rb')
        version = bbs.parse.getPkgFieldFromDCF(dcf, pkg, 'Version', BBScorevars.meat_index_file)
        dcf.close()
        ## Copy pkg from 'fresh_pkgs_subdir2'.
        pkg_file = "%s_%s.%s" % (pkg, version, fileext)
        pkg_file = os.path.join(fresh_pkgs_subdir, pkg_file)
        print("BBS> [stage6]   - copying %s to OUTGOING folder ..." % pkg_file)
        if os.path.exists(pkg_file):
            shutil.copy(pkg_file, ".")
        else:
            print("BBS> [stage6]     SKIPPED (file %s doesn't exist)" % pkg_file)
        ## Get reference manual from pkg.Rcheck directory.
        if BBScorevars.subbuilds in ["workflows", "books"]:
            pass
        elif source_node:
            pdf_file = "%s/meat/%s.Rcheck/%s-manual.pdf" % \
                       (BBScorevars.getenv('BBS_WORK_TOPDIR'), pkg, pkg)
            print("BBS> [stage6]   - copying %s manual to OUTGOING/manuals folder..." % pkg)
            if os.path.exists(pdf_file):
                shutil.copy(pdf_file, "%s/%s.pdf" % (manuals_dir, pkg))
            else:
                print("BBS> [stage6]     SKIPPED (file %s doesn't exist)" % pdf_file)
    print("BBS> [stage6] END copying outgoing packages from %s." % fresh_pkgs_subdir)
    return

def make_outgoing_biarch_pkgs(fresh_pkgs_subdir1, fresh_pkgs_subdir2):
    tmp1 = fresh_pkgs_subdir1.split("/")
    if len(tmp1) != 2:
        sys.exit("ERROR: Invalid relative path to fresh pkgs %s (must be of the form node/subdir)" % fresh_pkgs_subdir1)
    node1_id = tmp1[0]
    node1_hostname = node1_id.split("-")[0]
    tmp2 = fresh_pkgs_subdir2.split("/")
    if len(tmp2) != 2:
        sys.exit("ERROR: Invalid relative path to fresh pkgs %s (must be of the form node/subdir)" % fresh_pkgs_subdir2)
    node2_id = tmp2[0]
    node2_hostname = node2_id.split("-")[0]
    ## Check that node1 and node2 are registered as Windows i386 and x64
    ## builders, respectively
    pkgType1 = BBScorevars.getNodeSpec(node1_hostname, 'pkgType')
    if pkgType1 != "win.binary":
        sys.exit("ERROR: %s pkgType is not \"win.binary\"" % node1_hostname)
    pkgType2 = BBScorevars.getNodeSpec(node2_hostname, 'pkgType')
    if pkgType2 != "win64.binary":
        sys.exit("ERROR: %s pkgType is not \"win64.binary\"" % node2_hostname)
    fileext = BBScorevars.getNodeSpec(node1_hostname, 'pkgFileExt')
    fileext2 = BBScorevars.getNodeSpec(node2_hostname, 'pkgFileExt')
    if fileext2 != fileext:
        sys.exit("ERROR: %s pkgFileExt and %s pkgFileExt differ" % (node1_hostname, node2_hostname))
    fresh_pkgs_subdir1 = os.path.join(BBScorevars.nodes_rdir.path, fresh_pkgs_subdir1)
    fresh_pkgs_subdir2 = os.path.join(BBScorevars.nodes_rdir.path, fresh_pkgs_subdir2)
    print("BBS> [stage6] BEGIN making outgoing bi-arch packages from %s and %s." % (fresh_pkgs_subdir1, fresh_pkgs_subdir2))
    ## Get lists of supported pkgs for node1 and node2
    meat_index_file = os.path.join(BBScorevars.Central_rdir.path, BBScorevars.meat_index_file)
    dcf = open(meat_index_file, 'rb')
    pkgs1 = bbs.parse.readPkgsFromDCF(dcf, node1_id, pkgType1)
    dcf.close()
    dcf = open(meat_index_file, 'rb')
    pkgs2 = bbs.parse.readPkgsFromDCF(dcf, node2_id, pkgType2)
    dcf.close()
    ## Loop on list of supported pkgs
    pkgs0 = set(pkgs1 + pkgs2)
    nb_products = 0
    t1 = time.time()
    for pkg in pkgs0:
        dcf = open(meat_index_file, 'rb')
        version = bbs.parse.getPkgFieldFromDCF(dcf, pkg, 'Version', BBScorevars.meat_index_file)
        dcf.close()
        binpkg_file = "%s_%s.%s" % (pkg, version, fileext)
        if pkg not in pkgs1:
            if pkgMustBeRejected(node2_hostname, node2_id, pkg):
                continue
            ## Copy pkg from 'fresh_pkgs_subdir2'
            binpkg_file2 = os.path.join(fresh_pkgs_subdir2, binpkg_file)
            shutil.copy(binpkg_file2, ".")
            nb_products += 1
            continue
        if pkg not in pkgs2:
            if pkgMustBeRejected(node1_hostname, node1_id, pkg):
                continue
            ## Copy pkg from 'fresh_pkgs_subdir1'
            binpkg_file1 = os.path.join(fresh_pkgs_subdir1, binpkg_file)
            shutil.copy(binpkg_file1, ".")
            nb_products += 1
            continue
        if pkgMustBeRejected(node1_hostname, node1_id, pkg) or pkgMustBeRejected(node2_hostname, node2_id, pkg):
            continue
        ## Merge
        syscmd = '%s/utils/merge-win-bin-pkgs.sh %s %s %s %s cleanup' % (BBScorevars.BBS_home, pkg, version, fresh_pkgs_subdir1, fresh_pkgs_subdir2)
        bbs.jobs.doOrDie(syscmd)
        nb_products += 1
    dt = time.time() - t1
    print("BBS> [stage6] END making outgoing bi-arch packages from %s and %s." % (fresh_pkgs_subdir1, fresh_pkgs_subdir2))
    print("BBS> -------------------------------------------------------------")
    print("BBS> [stage6] MERGE(%s, %s) SUMMARY:" % (node1_id, node2_id))
    print("BBS>     o Working dir: %s" % os.getcwd())
    print("BBS>     o %d pkg(s) supported on Windows" % len(pkgs0))
    print("BBS>     o %d binpkg file(s) produced" % nb_products)
    print("BBS>     o Total time: %.2f seconds" % dt)
    print("BBS> -------------------------------------------------------------")
    return

def stage6_make_OUTGOING():
    ## Create working directory
    OUTGOING_dir = os.path.join(BBScorevars.Central_rdir.path, "OUTGOING")
    print("BBS> [stage6] remake_dir %s" % OUTGOING_dir)
    bbs.fileutils.remake_dir(OUTGOING_dir)
    ## Loop over each element of the OUTGOING map
    OUTGOING_map = BBScorevars.getenv('BBS_OUTGOING_MAP')
    map_elts = OUTGOING_map.split(" ")
    for map_elt in map_elts:
        tmp = map_elt.split(":")
        if len(tmp) != 2:
            sys.exit("ERROR: Invalid OUTGOING map element %s" % map_elt)
        source_node = False
        if tmp[0] == "source":
            source_node = True
        OUTGOING_subdir = os.path.join(OUTGOING_dir, tmp[0])
        print("BBS> [stage6] mkdir %s" % OUTGOING_subdir)
        os.mkdir(OUTGOING_subdir)
        print("BBS> [stage6] cd %s/" % OUTGOING_subdir)
        os.chdir(OUTGOING_subdir)
        tmp2 = tmp[1].split("+")
        if len(tmp2) == 1:
            copy_outgoing_pkgs(tmp[1], source_node)
        elif len(tmp2) == 2:
            make_outgoing_biarch_pkgs(tmp2[0], tmp2[1])
        else:
            sys.exit("ERROR: Invalid OUTGOING map element %s" % map_elt)
    return


##############################################################################
### MAIN SECTION
##############################################################################


print()
print("BBS> ==================================================================")
print("BBS> [stage6] STARTING stage6 at %s..." % time.asctime())

stage6_make_OUTGOING()

print("BBS> [stage6] DONE at %s." % time.asctime())

