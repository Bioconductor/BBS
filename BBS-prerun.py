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
        package_status = bbs.parse.getPackageStatusFromDir(pkgdir_path)
        out.write('PackageStatus: %s\n' % package_status)
        unsupported = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'UnsupportedPlatforms')
        out.write('UnsupportedPlatforms: %s\n' % unsupported)
        no_examples = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'NoExamplesOnPlatforms')
        out.write('NoExamplesOnPlatforms: %s\n' % no_examples)
        force_install = bbs.parse.getBBSoptionFromDir(pkgdir_path, 'ForceInstall')
        out.write('ForceInstall: %s\n' % force_install)
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
    BBScorevars.Central_rdir.Put(meat_index_path, True, True)
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

def writeAndUploadVcsMeta(snapshot_date):
    vcs = {1: 'svn', 3: 'git'}[BBSvars.MEAT0_type]
    vcs_cmd = {'svn': os.environ['BBS_SVN_CMD'], 'git': os.environ['BBS_GIT_CMD']}[vcs]
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    ## Get list of packages
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    dcf = open(meat_index_path, 'r')
    pkgs = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    ## Create top-level metadata file
    vcsmeta_path = os.path.join(BBSvars.work_topdir, BBSvars.vcsmeta_file)
    vcsmeta_dir = os.path.dirname(vcsmeta_path)
    bbs.fileutils.remake_dir(vcsmeta_dir)
    f = open(vcsmeta_path, 'a')
    f.write('Snapshot Date: %s\n' % snapshot_date)
    f.close()
    if vcs == 'svn':
        ## Top-level svn-info file
        cmd = '%s info %s >>%s' % (vcs_cmd, MEAT0_path, vcsmeta_path)
        bbs.jobs.doOrDie(cmd)
        ## Create svn-info file for each package
        for pkg in pkgs:
            pkgdir_path = os.path.join(MEAT0_path, pkg)
            svninfo_file = "-%s.".join(vcsmeta_path.rsplit(".", 1)) % pkg
            cmd = '%s info %s >%s' % (vcs_cmd, pkgdir_path, svninfo_file)
            bbs.jobs.doOrDie(cmd)
        update_svnlog()
    if vcs == 'git':
        ## Create git-log file for each package
        for pkg in pkgs:
            pkgdir_path = os.path.join(MEAT0_path, pkg)
            git_cmd_pkg = '%s -C %s' % (vcs_cmd, pkgdir_path)
            gitlog_file = "-%s.".join(vcsmeta_path.rsplit(".", 1)) % pkg
            gitlog_format = 'format:"Last Commit: %h%nLast Changed Date: %ad%n"'
            date_format = 'format-local:"%%Y-%%m-%%d %%H:%%M:%%S %s (%%a, %%d %%b %%Y)"' % snapshot_date.split(' ')[2]
            cmd = ' && '.join([
            'echo -n "URL: "',
            '%s remote get-url origin' % git_cmd_pkg,
            '%s log --max-count=1 --date=%s --format=%s' % (git_cmd_pkg, date_format, gitlog_format)
            ])
            cmd = '(%s) >%s' % (cmd, gitlog_file)
            bbs.jobs.doOrDie(cmd)
    BBScorevars.Central_rdir.Put(vcsmeta_dir, True, True)
    return

def update_svn_MEAT0(MEAT0_path, snapshot_date):
    vcs_cmd = os.environ['BBS_SVN_CMD']
    cmd = '%s up --set-depth infinity --non-interactive --username readonly --password readonly %s' % (vcs_cmd, MEAT0_path)
    print "BBS> [update_svn_MEAT0] %s (at %s)" % (cmd, snapshot_date)
    bbs.jobs.doOrDie(cmd)
    return

def update_git_MEAT0(MEAT0_path=None, snapshot_date=None):
    if MEAT0_path == None:
        MEAT0_path = BBSvars.MEAT0_rdir.path
    if snapshot_date == None:
        snapshot_date = bbs.jobs.currentDateString()
    vcs_cmd = os.environ['BBS_GIT_CMD']
    manifest_path = BBSvars.manifest_path
    manifest_dir = os.path.dirname(manifest_path)

    if not os.path.exists(manifest_dir):
        ## clone manifest repo
        cmd = '%s clone %s %s' % (vcs_cmd, BBSvars.manifest_git_repo_url, manifest_dir)
        print "BBS> [update_git_MEAT0] %s" % cmd
        bbs.jobs.doOrDie(cmd)

    ## update manifest
    manifest_git_branch = BBSvars.manifest_git_branch
    git_cmd = '%s -C %s' % (vcs_cmd, manifest_dir)
    git_branch = BBSvars.git_branch
    cmd = ' && '.join([
    '%s pull' % git_cmd,
    '%s checkout %s' % (git_cmd, manifest_git_branch)
    ])
    print "BBS> [update_git_MEAT0] %s (at %s)" % (cmd, snapshot_date)
    bbs.jobs.doOrDie(cmd)

    ## iterate over manifest to update pkg dirs
    dcf = open(manifest_path, 'r')
    pkgs = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    for pkg in pkgs:
        pkgdir_path = os.path.join(MEAT0_path, pkg)
        git_cmd = '%s -C %s' % (vcs_cmd, pkgdir_path)
        if os.path.exists(pkgdir_path):
            cmd = '%s fetch' % git_cmd
        else:
            cmd = '%s -C %s clone https://git.bioconductor.org/packages/%s' % (vcs_cmd, MEAT0_path, pkg)
        cmd = ' && '.join([cmd, '%s checkout %s' % (git_cmd, git_branch)])
        print "BBS> [update_git_MEAT0] %s" % cmd
        bbs.jobs.doOrDie(cmd)
        ## merge only up to snapshot date, see https://stackoverflow.com/a/8223166/2792099
        cmd = '%s merge `%s rev-list -n 1 --before="%s" %s`' % (git_cmd, git_cmd, snapshot_date, git_branch)
        print "BBS> [update_git_MEAT0] %s" % cmd
        bbs.jobs.doOrDie(cmd)
    return

def snapshotMEAT0(MEAT0_path):
    snapshot_date = bbs.jobs.currentDateString()
    if BBSvars.update_MEAT0 == 1:
        update_script = os.path.join(MEAT0_path, 'update-BBS-meat.sh')
        if os.path.exists(update_script):
            print "BBS> [snapshotMEAT0] cd BBS_MEAT0_RDIR"
            os.chdir(MEAT0_path)
            cmd = update_script
            print "BBS> [snapshotMEAT0] %s (at %s)" % (cmd, snapshot_date)
            bbs.jobs.doOrDie(cmd)
        else if BBSvars.MEAT0_type == 1:
            update_svn_MEAT0(MEAT0_path, snapshot_date)
        else if BBSvars.MEAT0_type == 3:
            update_git_MEAT0(MEAT0_path, snapshot_date)
    return snapshot_date

def writeAndUploadMeatInfo(work_topdir):
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    snapshot_date = snapshotMEAT0(MEAT0_path)
    manifest_path = BBSvars.manifest_path
    print "BBS> [writeAndUploadMeatInfo] Get pkg list from %s" % manifest_path
    dcf = open(manifest_path, 'r')
    pkgs = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    writeAndUploadMeatIndex(pkgs, MEAT0_path)
    writeAndUploadVcsMeta(snapshot_date)
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
    rdir.Put('PACKAGES', True, True)
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
    if (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3) and (arg1 == "" or arg1 == subtask):
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
