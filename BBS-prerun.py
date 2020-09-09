#!/usr/bin/env python3
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
import bbs.manifest
import bbs.parse
import bbs.dcf
import bbs.jobs
import bbs.gitutils
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

def build_meat_index(pkgs, meat_path):
    print("BBS> [build_meat_index] START building the meat index for " + \
          "the %s packages in the manifest" % len(pkgs))
    sys.stdout.flush()
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    skipped_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.skipped_index_file)
    out = open(meat_index_path, 'w')
    nout = 0
    skipped = open(skipped_index_path, 'w')
    nskipped = 0
    for pkg in pkgs:
        pkgsrctree = os.path.join(meat_path, pkg)
        if BBScorevars.subbuilds == "bioc-longtests":
           run_long_tests = bbs.parse.get_BBSoption_from_pkgsrctree(
                                          pkgsrctree,
                                          'RunLongTests')
           if run_long_tests != "TRUE":
               continue
        try:
            pkgname = bbs.parse.get_Package_from_pkgsrctree(pkgsrctree)
            version = bbs.parse.get_Version_from_pkgsrctree(pkgsrctree)
            if BBScorevars.subbuilds != "cran":
                maintainer = bbs.parse.get_Maintainer_name_from_pkgsrctree(pkgsrctree)
                maintainer_email = bbs.parse.get_Maintainer_email_from_pkgsrctree(pkgsrctree)
            else:
                maintainer = bbs.parse.get_Maintainer_from_pkgsrctree(pkgsrctree)
        except IOError:
            print("BBS>   Missing DESCRIPTION file in pkg dir '%s'. Skip it!" % pkgsrctree)
            sys.stdout.flush()
            skipped.write('Package: %s\n' % pkg)
            skipped.write('\n')
            nskipped = nskipped + 1
            continue
        except (bbs.parse.DcfFieldNotFoundError, bbs.dcf.dcfrecordsparser.DCFParseError):
            print("BBS>   Bad DESCRIPTION file in pkg dir '%s'. Skip it!" % pkgsrctree)
            sys.stdout.flush()
            skipped.write('Package: %s\n' % pkg)
            skipped.write('\n')
            nskipped = nskipped + 1
            continue
        if pkgname != pkg:
            DESCRIPTION_path = bbs.parse.get_DESCRIPTION_path(pkgsrctree)
            print("BBS>   Unexpected 'Package: %s' in '%s'. Skip it!" % \
                  (pkgname, DESCRIPTION_path))
            sys.stdout.flush()
            skipped.write('Package: %s\n' % pkg)
            skipped.write('\n')
            nskipped = nskipped + 1
            continue
        if not bbs.parse.version_is_valid(version):
            DESCRIPTION_path = bbs.parse.get_DESCRIPTION_path(pkgsrctree)
            print("BBS>   Invalid 'Version: %s' in '%s'. Skip it!" % \
                  (version, DESCRIPTION_path))
            sys.stdout.flush()
            skipped.write('Package: %s\n' % pkg)
            skipped.write('\n')
            nskipped = nskipped + 1
            continue
        out.write('Package: %s\n' % pkg)
        out.write('Version: %s\n' % version)
        out.write('Maintainer: %s\n' % maintainer)
        if BBScorevars.subbuilds != "cran":
            out.write('MaintainerEmail: %s\n' % maintainer_email)
        package_status = bbs.parse.get_PackageStatus_pkgsrctree(pkgsrctree)
        out.write('PackageStatus: %s\n' % package_status)
        unsupported = bbs.parse.get_BBSoption_from_pkgsrctree(
                                    pkgsrctree,
                                    'UnsupportedPlatforms')
        out.write('UnsupportedPlatforms: %s\n' % unsupported)
        no_examples = bbs.parse.get_BBSoption_from_pkgsrctree(
                                    pkgsrctree,
                                    'NoExamplesOnPlatforms')
        out.write('NoExamplesOnPlatforms: %s\n' % no_examples)
        force_install = bbs.parse.get_BBSoption_from_pkgsrctree(
                                    pkgsrctree,
                                    'ForceInstall')
        out.write('ForceInstall: %s\n' % force_install)
        if BBScorevars.subbuilds != "cran":
            alert = bbs.parse.get_BBSoption_from_pkgsrctree(pkgsrctree, 'Alert')
            out.write('Alert: %s\n' % alert)
            alert_on = bbs.parse.get_BBSoption_from_pkgsrctree(pkgsrctree, 'AlertOn')
            out.write('AlertOn: %s\n' % alert_on)
            alert_to = bbs.parse.get_BBSoption_from_pkgsrctree(pkgsrctree, 'AlertTo')
            out.write('AlertTo: %s\n' % alert_to)
        out.write('\n')
        nout = nout + 1
    skipped.close()
    out.close()
    print("BBS> [build_meat_index] DONE building the meat index for " + \
          "the %s packages in the manifest" % len(pkgs))
    print("BBS> [build_meat_index] %s pkgs were skipped (out of %s)" % (nskipped, len(pkgs)))
    print("BBS> [build_meat_index] %s pkgs made it to the meat index (out of %s)" % (nout, len(pkgs)))
    sys.stdout.flush()
    return meat_index_path

def writeAndUploadMeatIndex(pkgs, meat_path):
    meat_index_path = build_meat_index(pkgs, meat_path)
    BBScorevars.Central_rdir.Put(meat_index_path, True, True)
    return

def uploadSkippedIndex(work_topdir):
    skipped_index_path = os.path.join(work_topdir, BBScorevars.skipped_index_file)
    BBScorevars.Central_rdir.Put(skipped_index_path, True, True)
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
    logfile = open(logfilename, 'a+')
    date = time.strftime("%Y-%m-%d")
    logfile.write("%s\t%s\n" % (date, revision))
    logfile.close()
    svninfo_dir = os.path.join(BBSvars.work_topdir, "svninfo")
    shutil.copy(logfilename, svninfo_dir)

def collect_vcs_meta(snapshot_date):
    print("BBS> [collect_vcs_meta] START collecting vcs meta data...")
    sys.stdout.flush()
    vcs = {1: 'svn', 3: 'git'}[BBSvars.MEAT0_type]
    vcs_cmd = {'svn': os.environ['BBS_SVN_CMD'], 'git': os.environ['BBS_GIT_CMD']}[vcs]
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    ## Get list of packages
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    dcf = open(meat_index_path, 'rb')
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
            pkgsrctree = os.path.join(MEAT0_path, pkg)
            svninfo_file = "-%s.".join(vcsmeta_path.rsplit(".", 1)) % pkg
            cmd = '%s info %s >%s' % (vcs_cmd, pkgsrctree, svninfo_file)
            bbs.jobs.doOrDie(cmd)
        update_svnlog()
    if vcs == 'git':
        ## Create git-log file for each package in meat-index.dcf and
        ## skipped-index.dcf
        skipped_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.skipped_index_file)
        dcf = open(skipped_index_path, 'rb')
        skipped_pkgs = bbs.parse.readPkgsFromDCF(dcf)
        dcf.close()
        all_pkgs = pkgs + skipped_pkgs
        for pkg in all_pkgs:
            pkgsrctree = os.path.join(MEAT0_path, pkg)
            git_cmd_pkg = '%s -C %s' % (vcs_cmd, pkgsrctree)
            gitlog_file = "-%s.".join(vcsmeta_path.rsplit(".", 1)) % pkg
            gitlog_format = 'format:"Last Commit: %h%nLast Changed Date: %ad%n"'
            date_format = 'format-local:"%%Y-%%m-%%d %%H:%%M:%%S %s (%%a, %%d %%b %%Y)"' % snapshot_date.split(' ')[2]
            cmd = ' && '.join([
            'echo -n "URL: "',
            '%s remote get-url origin' % git_cmd_pkg,
            'echo -n "Branch: "',
            '%s rev-parse --abbrev-ref HEAD' % git_cmd_pkg,
            '%s log --max-count=1 --date=%s --format=%s' % (git_cmd_pkg, date_format, gitlog_format)
            ])
            cmd = '(%s) >%s' % (cmd, gitlog_file)
            bbs.jobs.doOrDie(cmd)
    BBScorevars.Central_rdir.Put(vcsmeta_dir, True, True)
    print("BBS> [collect_vcs_meta] DONE collecting vcs meta data.")
    sys.stdout.flush()
    return

def update_svn_MEAT0(MEAT0_path, snapshot_date):
    vcs_cmd = os.environ['BBS_SVN_CMD']
    cmd = '%s up --set-depth infinity --non-interactive --username readonly --password readonly %s' % (vcs_cmd, MEAT0_path)
    print("BBS> [update_svn_MEAT0] %s (at %s)" % (cmd, snapshot_date))
    bbs.jobs.doOrDie(cmd)
    return

def update_git_MEAT0(MEAT0_path=None, snapshot_date=None,
                     git_branch=None, manifest_git_branch=None):
    if MEAT0_path == None:
        MEAT0_path = BBSvars.MEAT0_rdir.path
    if snapshot_date == None:
        snapshot_date = bbs.jobs.currentDateString()
    if git_branch == None:
        git_branch = BBSvars.git_branch
    if manifest_git_branch == None:
        manifest_git_branch = BBSvars.manifest_git_branch
    print("BBS> =============================================================")
    print("BBS> BEGIN update_git_MEAT0()")
    print("BBS>   MEAT0_path: %s" % MEAT0_path)
    print("BBS>   snapshot_date: %s" % snapshot_date)
    print("BBS>   git_branch: %s" % git_branch)
    print("BBS>   manifest_git_branch: %s" % manifest_git_branch)
    print("BBS> -------------------------------------------------------------")
    print()
    bbs.gitutils.update_git_clone(BBSvars.manifest_clone_path,
                             BBSvars.manifest_git_repo_url,
                             manifest_git_branch,
                             depth=1,
                             reclone_if_update_fails=True)
    ## iterate over manifest to update pkg dirs
    pkgs = bbs.manifest.read(BBSvars.manifest_path)
    i = 0
    for pkg in pkgs:
        i += 1
        print("BBS> ----------------------------------------------------------")
        print("BBS> [update_git_MEAT0] (%d/%d) repo: %s / branch: %s" % \
              (i, len(pkgs), pkg, git_branch))
        print()
        pkg_git_clone = os.path.join(MEAT0_path, pkg)
        pkg_git_repo_url = 'https://git.bioconductor.org/packages/%s' % pkg
        bbs.gitutils.update_git_clone(pkg_git_clone,
                                 pkg_git_repo_url,
                                 git_branch,
                                 depth=1,
                                 snapshot_date=snapshot_date,
                                 reclone_if_update_fails=True)
        print()
    print("BBS> -------------------------------------------------------------")
    print("BBS> END update_git_MEAT0()")
    print("BBS> ==============================================================")
    print()
    sys.stdout.flush()
    return

def update_MEAT0(MEAT0_path):
    print("BBS>")
    snapshot_date = bbs.jobs.currentDateString()
    if BBSvars.update_MEAT0 == 1:
        update_script = os.path.join(MEAT0_path, 'update-BBS-meat.sh')
        if os.path.exists(update_script):
            print("BBS> [update_MEAT0] cd BBS_MEAT0_RDIR")
            os.chdir(MEAT0_path)
            cmd = update_script
            print("BBS> [update_MEAT0] %s (at %s)" % (cmd, snapshot_date))
            bbs.jobs.doOrDie(cmd)
        elif BBSvars.MEAT0_type == 1:
            update_svn_MEAT0(MEAT0_path, snapshot_date)
        elif BBSvars.MEAT0_type == 3:
            update_git_MEAT0(MEAT0_path, snapshot_date)
    return snapshot_date

def writeAndUploadMeatInfo(work_topdir):
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    snapshot_date = update_MEAT0(MEAT0_path)
    manifest_path = BBSvars.manifest_path
    print("BBS> [writeAndUploadMeatInfo] Get pkg list from %s" % manifest_path)
    pkgs = bbs.manifest.read(manifest_path)
    writeAndUploadMeatIndex(pkgs, MEAT0_path)
    collect_vcs_meta(snapshot_date)
    uploadSkippedIndex(work_topdir)
    return

##############################################################################

### Used typically for extracting CRAN src pkg tarballs
def extractSrcPkgTarballs(dest_dir):
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    srcpkg_files = bbs.fileutils.listSrcPkgFiles(MEAT0_path)
    bbs.fileutils.remake_dir(dest_dir)
    pkgs = []
    for srcpkg_file in srcpkg_files:
        pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_file)
        srcpkg_filepath = os.path.join(MEAT0_path, srcpkg_file)
        BBSbase.Untar(srcpkg_filepath, dest_dir)
        pkgs.append(pkg)
    return pkgs

### Get the CRAN packages from cobra (NOT currently used)
def GetCranPkgs(work_topdir):
    print("BBS> [prerun:get-cran-pkgs] cd BBS_WORK_TOPDIR")
    os.chdir(work_topdir)
    pkgs_dir = "pkgs"
    if os.path.exists(pkgs_dir):
        print("BBS> [prerun:get-cran-pkgs] rm -r %s" % pkgs_dir)
        bbs.fileutils.nuke_tree(pkgs_dir)
    print("BBS> [prerun:get-cran-pkgs] Download CRAN packages to BBS_WORK_TOPDIR/pkgs")
    cmd = "/usr/bin/rsync -ae ssh webadmin@cobra:'/extra/www/cran-mirror/src/contrib/*.tar.gz' %s" % pkgs_dir
    bbs.jobs.doOrDie(cmd)
    os.chdir(pkgs_dir)
    srcpkg_files = bbs.fileutils.listSrcPkgFiles()
    for srcpkg_file in srcpkg_files:
        print("BBS> [prerun:get-cran-pkgs] tar zxf %s" % srcpkg_file)
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

def prepare_STAGE1_job_queue(pkgsrctrees, dest_rdir):
    print("BBS> Preparing STAGE1 job queue ... ", end=" ")
    stage = 'buildnovig'
    jobs = []
    for pkgsrctree in pkgsrctrees:
        try:
            pkg = bbs.parse.get_Package_from_pkgsrctree(pkgsrctree)
            version = bbs.parse.get_Version_from_pkgsrctree(pkgsrctree)
            srcpkg_file = bbs.parse.make_srcpkg_file_from_pkgsrctree(pkgsrctree)
        except IOError:
            print("BBS>   Can't read DESCRIPTION file!")
        else:
            cmd = BBSbase.getSTAGE1cmd(pkgsrctree)
            pkgdumps_prefix = pkg + '.' + stage;
            pkgdumps = BBSbase.PkgDumps(srcpkg_file, pkgdumps_prefix)
            job = BBSbase.BuildPkg_Job(pkg, version, cmd, pkgdumps, dest_rdir)
            jobs.append(job)
    print("OK")
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(pkgsrctrees)
    return job_queue

def STAGE1_loop(job_queue, nb_cpu):
    print("BBS> BEGIN STAGE1 loop.")
    t1 = time.time()
    nb_products = bbs.jobs.processJobQueue(job_queue, nb_cpu, 900.0, True)
    dt = time.time() - t1
    print("BBS> END STAGE1 loop.")
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print("BBS> -------------------------------------------------------------")
    print("BBS> STAGE1 SUMMARY:")
    print("BBS>     o Working dir: %s" % os.getcwd())
    print("BBS>     o %d pkg(s) listed in file %s" % \
          (total, BBScorevars.meat_index_file))
    print("BBS>     o %d pkg dir(s) queued and processed" % nb_jobs)
    print("BBS>     o %d srcpkg file(s) produced" % nb_products)
    print("BBS>     o Total time: %.2f seconds" % dt)
    print("BBS> -------------------------------------------------------------")
    return

def makeTargetRepo(rdir):
    print("BBS> [makeTargetRepo] STARTING makeTargetRepo...")
    print("BBS> [makeTargetRepo] mkdir %s" % rdir.label)
    rdir.MakeMe()
    #FIXME: The 2 lines below don't seem to be able to remove anything!
    print("BBS> [makeTargetRepo] rm -f %s/*" % rdir.label)
    rdir.Call('rm -f *')
    print("BBS> [makeTargetRepo] cd BBS_MEAT_PATH")
    os.chdir(BBSvars.meat_path)
    print("BBS> [makeTargetRepo] Get list of pkgs from %s" % BBScorevars.meat_index_file)
    meat_index_path = os.path.join(BBSvars.work_topdir, BBScorevars.meat_index_file)
    dcf = open(meat_index_path, 'rb')
    pkgsrctrees = bbs.parse.readPkgsFromDCF(dcf)
    dcf.close()
    job_queue = prepare_STAGE1_job_queue(pkgsrctrees, rdir)
    ## STAGE1 will run 'tar zcf' commands to generate the no-vignettes source
    ## tarballs. Running too many concurrent 'tar zcf' commands seems harmful
    ## so we limit the nb of cpus to 2.
    #STAGE1_loop(job_queue, BBSvars.nb_cpu)
    STAGE1_loop(job_queue, 2)
    MakeReposPACKAGES(rdir)
    print("BBS> [makeTargetRepo] DONE.")
    return


##############################################################################
## MAIN SECTION
##############################################################################

if __name__ == "__main__":
    print()
    print()
    print()
    print("BBS> ==============================================================")
    print("BBS> ==============================================================")
    print("BBS> %s" % time.asctime())
    print("BBS> ==============================================================")
    print()
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
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        remakeCentralRdir(Central_rdir)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "upload-meat-info"
    if (arg1 == "" or arg1 == subtask) and (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        writeAndUploadMeatInfo(work_topdir)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "create-local-meat-dir"
    if (arg1 == "" or arg1 == subtask) and (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        ## Using rsync is better than "svn export": (1) it's incremental,
        ## (2) it works remotely, (3) it works with "nested working copies
        ## (like we have for the data-experiment MEAT0) and, (4) it's even
        ## slightly faster!
        BBSvars.MEAT0_rdir.syncLocalDir(BBSvars.meat_path, True)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "extract-meat"
    if (arg1 == "" or arg1 == subtask) and BBSvars.MEAT0_type == 2:
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        pkgs = extractSrcPkgTarballs(meat_path)
        writeAndUploadMeatIndex(pkgs, meat_path)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "make-target-repo"
    if arg1 == "" or arg1 == subtask:
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        Contrib_rdir = Central_rdir.subdir('src/contrib')
        makeTargetRepo(Contrib_rdir)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))
