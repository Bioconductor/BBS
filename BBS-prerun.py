#! /usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: May 10, 2011
###

import sys
import os
import shutil
import time

import bbs.fileutils
import bbs.parse
import bbs.dcf
import bbs.jobs
import BBScorevars
import BBSvars
import BBSbase


##############################################################################
## 
##############################################################################

def remakeCentralRdir(Central_rdir):
    Central_rdir.RemakeMe(True)
    return


##############################################################################
## Update the meat and upload the svn info file + the meat index (based
## on the manifest file)
##############################################################################

def writeMeatIndex(pkgs, meat_path):
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    out = open(meat_index_path, 'w')
    nout = 0
    for pkg in pkgs:
        pkgdir_path = os.path.join(meat_path, pkg)
        try:
            package = bbs.parse.getPkgFromDir(pkgdir_path)
            version = bbs.parse.getVersionFromDir(pkgdir_path)
            if BBScorevars.mode != "cran":
                maintainer = bbs.parse.getMaintainerFromDir(pkgdir_path)
                maintainer_email = bbs.parse.getMaintainerEmailFromDir(pkgdir_path)
            else:
                maintainer = bbs.parse._getMaintainerFromDir(pkgdir_path)
        except IOError:
            print "BBS>   Missing DESCRIPTION file in pkg dir '%s'. Skip it!" % pkgdir_path
            continue
        except (bbs.parse.DcfFieldNotFoundError, bbs.dcf.dcfrecordsparser.DCFParseError):
            print "BBS>   Bad DESCRIPTION file in pkg dir '%s'. Skip it!" % pkgdir_path
            continue
        if package != pkg:
            desc_file = bbs.parse.getDescFile(pkgdir_path)
            print "BBS>   Unexpected 'Package: %s' in '%s'. Skip it!" % (package, desc_file)
            continue
        out.write('Package: %s\n' % pkg)
        out.write('Version: %s\n' % version)
        out.write('Maintainer: %s\n' % maintainer)
        if BBScorevars.mode != "cran":
            out.write('MaintainerEmail: %s\n' % maintainer_email)
        unsupported = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'UnsupportedPlatforms')
        out.write('UnsupportedPlatforms: %s\n' % unsupported)
        no_examples = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'NoExamplesOnPlatforms')
        out.write('NoExamplesOnPlatforms: %s\n' % no_examples)
        if BBScorevars.mode != "cran":
            alert = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'Alert')
            out.write('Alert: %s\n' % alert)
            alert_on = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'AlertOn')
            out.write('AlertOn: %s\n' % alert_on)
            alert_to = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'AlertTo')
            out.write('AlertTo: %s\n' % alert_to)
        out.write('\n')
        nout = nout + 1
    out.close()
    print "BBS> [writeMeatIndex] %s pkgs written to meat index (out of %s)" % (nout, len(pkgs))
    return meat_index_path

def writeAndUploadMeatIndex(pkgs, meat_path):
    meat_index_path = writeMeatIndex(pkgs, meat_path)
    BBScorevars.Central_rdir.Put(meat_index_path, True)
    return

def writeAndUploadSvnInfo(snapshot_date):
    svn_cmd = os.environ['BBS_SVN_CMD']
    svninfo_dir = os.path.join(BBSvars.work_topdir, "svninfo")
    bbs.fileutils.remake_dir(svninfo_dir)
    ## Create top-level svn-info file
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    svninfo_file = os.path.join(svninfo_dir, "svn-info.txt")
    cmd = '%s info %s >%s' % (svn_cmd, MEAT0_path, svninfo_file)
    bbs.jobs.doOrDie(cmd)
    f = open(svninfo_file, 'a')
    f.write('Snapshot Date: %s\n' % snapshot_date)
    f.close()
    ## Create svn-info file for each package
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    dcf = open(meat_index_path, 'r')
    pkgs = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    for pkg in pkgs:
        pkgdir_path = os.path.join(MEAT0_path, pkg)
        svninfo_file = os.path.join(svninfo_dir, 'svn-info-%s.txt' % pkg)
        cmd = '%s info %s >%s' % (svn_cmd, pkgdir_path, svninfo_file)
        bbs.jobs.doOrDie(cmd)
    update_svnlog()
    BBScorevars.Central_rdir.Put(svninfo_dir, True)
    return

def update_svnlog():
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    svn_cmd = os.environ['BBS_SVN_CMD']
    cmd = '%s info %s' % (svn_cmd, MEAT0_path)
    output = bbs.jobs.getCmdOutput(cmd)
    lines = output.split("\n")
    for line in lines:
        if "Revision:" in line:
            revision = line.split(" ")[1]
            break
    logfilename = os.path.join(BBSvars.work_topdir, "svnlog.txt")
    logfile = open(logfilename, "a+")
    date = time.strftime("%Y-%m-%d")
    logfile.write("%s\t%s\n" % (date, revision))
    logfile.close()
    svninfo_dir = os.path.join(BBSvars.work_topdir, "svninfo")
    shutil.copy(logfilename, svninfo_dir)


def snapshotMEAT0(MEAT0_path):
    snapshot_date = bbs.jobs.currentDateString()
    if BBSvars.update_MEAT0 == 1:
        update_script = os.path.join(MEAT0_path, 'update-BBS-meat.sh')
        if os.path.exists(update_script):
            print "BBS> [snapshotMEAT0] cd BBS_MEAT0_RDIR"
            os.chdir(MEAT0_path)
            cmd = update_script
        else:
            svn_cmd = os.environ['BBS_SVN_CMD']
            cmd = '%s up %s' % (svn_cmd, MEAT0_path)
        print "BBS> [snapshotMEAT0] %s (at %s)" % (cmd, snapshot_date)
        bbs.jobs.doOrDie(cmd)
    return snapshot_date

def writeAndUploadMeatInfo(work_topdir):
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    snapshot_date = snapshotMEAT0(MEAT0_path)
    #os.chdir(work_topdir)
    ## "svninfo/" and "meat-index.txt"
    manifest_path = os.path.join(MEAT0_path, BBSvars.manifest_file)
    print "BBS> [writeAndUploadMeatInfo] Get pkg list from %s" % manifest_path
    dcf = open(manifest_path, 'r')
    pkgs = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    writeAndUploadMeatIndex(pkgs, MEAT0_path)
    writeAndUploadSvnInfo(snapshot_date)
    return


##############################################################################

### Used typically for extracting CRAN src pkg tarballs
def extractSrcPkgTarballs(dest_dir):
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    srcpkg_files = bbs.fileutils.listSrcPkgFiles(MEAT0_path)
    bbs.fileutils.remake_dir(dest_dir)
    pkgs = []
    for srcpkg_file in srcpkg_files:
        pkg = bbs.parse.getPkgFromPath(srcpkg_file)
        srcpkg_filepath = os.path.join(MEAT0_path, srcpkg_file)
        BBSbase.Untar(srcpkg_filepath, dest_dir)
        pkgs.append(pkg)
    return pkgs

### Get the CRAN packages from cobra (NOT currently used)
def GetCranPkgs(work_topdir):
    print "BBS> [prerun:get-cran-pkgs] cd BBS_WORK_TOPDIR"
    os.chdir(work_topdir)
    pkgs_dir = "pkgs"
    if os.path.exists(pkgs_dir):
        print "BBS> [prerun:get-cran-pkgs] rm -r %s" % pkgs_dir
        bbs.fileutils.nuke_tree(pkgs_dir)
    print "BBS> [prerun:get-cran-pkgs] Download CRAN packages to BBS_WORK_TOPDIR/pkgs"
    cmd = "/usr/bin/rsync -ae ssh webadmin@cobra:'/extra/www/cran-mirror/src/contrib/*.tar.gz' %s" % pkgs_dir
    bbs.jobs.doOrDie(cmd)
    os.chdir(pkgs_dir)
    srcpkg_files = bbs.fileutils.listSrcPkgFiles()
    for srcpkg_file in srcpkg_files:
        print "BBS> [prerun:get-cran-pkgs] tar zxf %s" % srcpkg_file
        BBSbase.Untar(srcpkg_file)
    return

def MakeReposPACKAGES(rdir):
    cmdTemplate = r'echo "library(tools);write_PACKAGES(\".\")"'
    cmdTemplate += '| %s --slave'
    cmdStr = cmdTemplate % BBSvars.r_cmd
    bbs.jobs.doOrDie(cmdStr)
    rdir.Put('PACKAGES', True)
    return


##############################################################################
## Make the target-repo and populate it with the no-vignettes srcpkg files.
##############################################################################

# TODO: Merge STAGE1_loop() and STAGE3_loop() (from BBS-run.py)
# into one single function

def STAGE1_loop(pkgdir_paths, dest_rdir, nb_cpu):
    print "BBS> [STAGE1_loop] BEGIN loop."
    total = len(pkgdir_paths)
    job_queue = []
    for pkgdir_path in pkgdir_paths:
        try:
            pkg = bbs.parse.getPkgFromDir(pkgdir_path)
            version = bbs.parse.getVersionFromDir(pkgdir_path)
            srcpkg_file = bbs.parse.getSrcPkgFileFromDir(pkgdir_path)
        except IOError:
            print "BBS>   Can't read DESCRIPTION file!"
        else:
            cmd = BBSbase.getSTAGE1cmd(pkgdir_path)
            pkgdumps_prefix = pkg + '.buildnovig'
            pkgdumps = BBSbase.PkgDumps(srcpkg_file, pkgdumps_prefix)
            job = BBSbase.BuildPkg_Job(pkg, version, cmd, pkgdumps, dest_rdir)
            job_queue.append(job)
    nb_jobs = len(job_queue)
    t0 = time.time()
    nb_products = bbs.jobs.processJobQueue(job_queue, None, nb_cpu,
                                           600.0, True)
    dt = time.time() - t0
    print "BBS> [STAGE1_loop] END loop."
    print "BBS> -------------------------------------------------------------"
    print "BBS> STAGE1 SUMMARY:"
    print "BBS>     o Working dir: %s" % os.getcwd()
    print "BBS>     o %d pkg(s) listed in file %s" % (total, BBScorevars.meat_index_file)
    print "BBS>     o %d pkg dir(s) queued and processed" % nb_jobs
    print "BBS>     o %d srcpkg file(s) produced" % nb_products
    print "BBS>     o Total time: %.2f seconds" % dt
    print "BBS> -------------------------------------------------------------"
    return

def makeTargetRepo(rdir):
    print "BBS> [makeTargetRepo] STARTING makeTargetRepo..."
    print "BBS> [makeTargetRepo] mkdir %s" % rdir.label
    rdir.MakeMe()
    #FIXME: The 2 lines below don't seem to be able to remove anything!
    print "BBS> [makeTargetRepo] rm -f %s/*" % rdir.label
    rdir.Call('rm -f *')
    print "BBS> [makeTargetRepo] cd BBS_MEAT_PATH"
    os.chdir(BBSvars.meat_path)
    print "BBS> [makeTargetRepo] Get list of pkgs from %s" % BBScorevars.meat_index_file
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    dcf = open(meat_index_path, 'r')
    pkgdir_paths = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    STAGE1_loop(pkgdir_paths, rdir, BBSvars.nb_cpu)
    MakeReposPACKAGES(rdir)
    print "BBS> [makeTargetRepo] DONE."
    return


##############################################################################
## MAIN SECTION
##############################################################################

if __name__ == "__main__":
    print
    print
    print
    print "BBS> =============================================================="
    print "BBS> =============================================================="
    print "BBS> %s" % time.asctime()
    print "BBS> =============================================================="
    print
    argc = len(sys.argv)
    if argc > 1:
        arg1 = sys.argv[1]
    else:
        arg1 = ""
    work_topdir = BBSvars.work_topdir
    meat_path = BBSvars.meat_path
    Central_rdir = BBScorevars.Central_rdir

    subtask = "make-central-rdir"
    if arg1 == "" or arg1 == subtask:
        print "BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime())
        remakeCentralRdir(Central_rdir)
        print "BBS> [prerun] DONE %s at %s." % (subtask, time.asctime())

    subtask = "upload-meat-info"
    if BBSvars.MEAT0_type == 1 and (arg1 == "" or arg1 == subtask):
        print "BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime())
        writeAndUploadMeatInfo(work_topdir)
        ## Using rsync is better than "svn export": (1) it's incremental,
        ## (2) it works remotely, (3) it works with "nested working copies
        ## (like we have for the data-experiment MEAT0) and, (4) it's even
        ## slightly faster!
        BBSvars.MEAT0_rdir.syncLocalDir(BBSvars.meat_path, True)
        print "BBS> [prerun] DONE %s at %s." % (subtask, time.asctime())

    subtask = "extract-meat"
    if BBSvars.MEAT0_type == 2 and (arg1 == "" or arg1 == subtask):
        print "BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime())
        pkgs = extractSrcPkgTarballs(meat_path)
        writeAndUploadMeatIndex(pkgs, meat_path)
        print "BBS> [prerun] DONE %s at %s." % (subtask, time.asctime())

    subtask = "make-target-repo"
    if arg1 == "" or arg1 == subtask:
        print "BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime())
        Contrib_rdir = Central_rdir.subdir('src/contrib')
        makeTargetRepo(Contrib_rdir)
        print "BBS> [prerun] DONE %s at %s." % (subtask, time.asctime())

