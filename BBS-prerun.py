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
import shutil
import time

import bbs.fileutils
import bbs.manifest
import bbs.parse
import bbs.jobs
import bbs.gitutils
import BBSutils
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

### Return 0 if package goes to the "meat index", 1 if it's skipped (in which
### case it wil go to the "skipped index"), and 2 if it's ignored.
def _add_or_skip_or_ignore_package(pkgsrctree, meat_index):
    options = bbs.parse.parse_BBSoptions_from_pkgsrctree(pkgsrctree)
    if BBSvars.buildtype == "bioc-longtests":
        ## Ignore the package if it has no .BBSoptions file, or if the file
        ## has no RunLongTests entry, or if the entry is not TRUE.
        if options == None:
            return 2  # package will be ignored
        run_long_tests = options.get('RunLongTests')
        if run_long_tests == None:
            return 2  # package will be ignored
        if run_long_tests.lower() != "true":
            return 2  # package will be ignored
    DESCRIPTION_path = bbs.parse.get_DESCRIPTION_path(pkgsrctree)
    try:
        ## We set 'merge_records' to True to support DESCRIPTION files with
        ## empty lines. Empty lines in a DESCRIPTION file can be considered
        ## a mild formatting issue, which we tolerate. Such file would be
        ## considered to contain more than 1 DCF record so we merge them.
        DESCRIPTION = bbs.parse.parse_DCF(DESCRIPTION_path, merge_records=True)
    except FileNotFoundError:
        print("BBS>   Missing DESCRIPTION file in '%s/' ==> skip package" % \
              pkgsrctree)
        return 1  # package will be skipped
    except bbs.parse.DcfParsingError:
        print("BBS>   Invalid DESCRIPTION file: %s ==> skip package" % \
              DESCRIPTION_path)
        return 1  # package will be skipped
    try:
        pkgname = DESCRIPTION['Package']
    except KeyError:
        print("BBS>   Field 'Package' not found in '%s' ==> skip package" % \
              DESCRIPTION_path)
        return 1  # package will be skipped
    if pkgname != os.path.basename(pkgsrctree):
        print("BBS>   Unexpected 'Package: %s' in '%s' ==> skip package" % \
              (pkgname, DESCRIPTION_path))
        return 1  # package will be skipped
    try:
        version = DESCRIPTION['Version']
    except KeyError:
        print("BBS>   Field 'Version' not found in '%s' ==> skip package" % \
              DESCRIPTION_path)
        return 1  # package will be skipped
    if not bbs.parse.version_is_valid(version):
        print("BBS>   Invalid 'Version: %s' in '%s' ==> skip package" % \
              (version, DESCRIPTION_path))
        return 1  # package will be skipped
    try:
        if BBSvars.buildtype != "cran":
            maintainer = bbs.parse.get_Maintainer_name_from_pkgsrctree(pkgsrctree)
            maintainer_email = bbs.parse.get_Maintainer_email_from_pkgsrctree(pkgsrctree)
        else:
            maintainer = bbs.parse.get_Maintainer_from_pkgsrctree(pkgsrctree)
    except bbs.parse.DcfFieldNotFoundError:
        print("BBS>   Failed to extract Maintainer information " + \
              "from '%s' ==> skip package" % DESCRIPTION_path)
        return 1  # package will be skipped
    meat_index.write('Package: %s\n' % pkgname)
    meat_index.write('Version: %s\n' % version)
    meat_index.write('Maintainer: %s\n' % maintainer)
    if BBSvars.buildtype != "cran":
        meat_index.write('MaintainerEmail: %s\n' % maintainer_email)
    package_status = DESCRIPTION.get('PackageStatus')
    if package_status != None:
        meat_index.write('PackageStatus: %s\n' % package_status)
    OS_type = DESCRIPTION.get('OS_type')
    OS_type_is_unix = OS_type != none and OS_type.lower().find('unix') >= 0
    if options != None or OS_type_is_unix:
        unsupported = None
        if options != None:
            unsupported = options.get('UnsupportedPlatforms')
        if unsupported == None:
            if OS_type_is_unix:
                unsupported = 'win'
        else:
            if unsupported.lower().find('win') < 0 and OS_type_is_unix:
                unsupported += ', win'
        if unsupported != None:
            meat_index.write('UnsupportedPlatforms: %s\n' % unsupported)
    meat_index.write('\n')
    return 0  # package will be added to the "meat index"

def build_meat_index(pkgs, meat_path):
    doing_what = 'creating the meat index for the %s target package' % len(pkgs)
    if BBSvars.buildtype == "bioc-incremental":
        doing_what += '(s) that have changed'
    else:
        doing_what += 's in the manifest'
    print('BBS> [build_meat_index] START %s at %s...' % \
          (doing_what, time.asctime()))
    sys.stdout.flush()
    meat_index_path = os.path.join(BBSvars.work_topdir,
                                   BBSutils.meat_index_file)
    skipped_index_path = os.path.join(BBSvars.work_topdir,
                                      BBSutils.skipped_index_file)
    meat_index = open(meat_index_path, 'w')
    skipped_index = open(skipped_index_path, 'w')
    nadded = nskipped = 0
    for pkg in pkgs:
        pkgsrctree = os.path.join(meat_path, pkg)
        retcode = _add_or_skip_or_ignore_package(pkgsrctree, meat_index)
        meat_index.flush()
        if retcode == 2:
            ## Ignore package.
            continue
        if retcode == 1:
            ## Skip package.
            sys.stdout.flush()
            skipped_index.write('Package: %s\n' % pkg)
            skipped_index.write('\n')
            skipped_index.flush()
            nskipped = nskipped + 1
            continue
        ## Package was added to "meat index".
        nadded = nadded + 1
    skipped_index.close()
    meat_index.close()
    print('BBS> [build_meat_index] DONE %s at %s.' % \
          (doing_what, time.asctime()))
    if BBSvars.buildtype == "bioc-longtests":
        nignored = len(pkgs) - nadded - nskipped
        print("BBS>   --> %d pkgs were ignored" % nignored, end=" ")
        print("(because not subscribed to Long Tests builds)")
    print("BBS>   --> %d pkgs were skipped" % nskipped)
    print("BBS>   --> %d pkgs made it to the meat index" % nadded)
    print()
    sys.stdout.flush()
    return meat_index_path

def buildAndUploadMeatIndex(pkgs, meat_path):
    meat_index_path = build_meat_index(pkgs, meat_path)
    BBSvars.Central_rdir.Put(meat_index_path, True, True)
    return

def uploadSkippedIndex(work_topdir):
    skipped_index_path = os.path.join(work_topdir, BBSutils.skipped_index_file)
    BBSvars.Central_rdir.Put(skipped_index_path, True, True)
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
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    ## Get list of packages
    meat_index_path = os.path.join(BBSvars.work_topdir,
                                   BBSutils.meat_index_file)
    pkgs = bbs.parse.get_meat_packages(meat_index_path)
    ## Create top-level metadata file
    vcsmeta_path = os.path.join(BBSvars.work_topdir, BBSvars.vcsmeta_file)
    vcsmeta_dir = os.path.dirname(vcsmeta_path)
    bbs.fileutils.remake_dir(vcsmeta_dir)
    f = open(vcsmeta_path, 'a')
    f.write('Snapshot Date: %s\n' % snapshot_date)
    f.close()
    if BBSvars.MEAT0_type == 1:
        ## Get the meat from svn.
        svn_cmd = os.environ['BBS_SVN_CMD']
        ## Top-level svn-info file
        cmd = '%s info %s >>%s' % (svn_cmd, MEAT0_path, vcsmeta_path)
        bbs.jobs.doOrDie(cmd)
        ## Create svn-info file for each package
        for pkg in pkgs:
            pkgsrctree = os.path.join(MEAT0_path, pkg)
            svninfo_file = "-%s.".join(vcsmeta_path.rsplit(".", 1)) % pkg
            cmd = '%s info %s >%s' % (svn_cmd, pkgsrctree, svninfo_file)
            bbs.jobs.doOrDie(cmd)
        update_svnlog()
    elif BBSvars.MEAT0_type == 3:
        ## Get the meat from git.
        ## Create git-log file for each package in meat-index.dcf and
        ## skipped-index.dcf
        skipped_index_path = os.path.join(BBSvars.work_topdir,
                                          BBSutils.skipped_index_file)
        skipped_pkgs = bbs.parse.get_meat_packages(skipped_index_path)
        allpkgs = pkgs + skipped_pkgs
        for pkg in allpkgs:
            pkgsrctree = os.path.join(MEAT0_path, pkg)
            gitlog_file = "-%s.".join(vcsmeta_path.rsplit(".", 1)) % pkg
            bbs.gitutils.collect_git_clone_meta(pkgsrctree, gitlog_file, snapshot_date)
    else:
        sys.exit("ERROR: Invalid BBS_MEAT0_TYPE: %d" % BBSvars.MEAT0_type)
    BBSvars.Central_rdir.Put(vcsmeta_dir, True, True)
    print("BBS> [collect_vcs_meta] DONE collecting vcs meta data.")
    sys.stdout.flush()
    return

def update_svn_MEAT0(MEAT0_path, snapshot_date):
    svn_cmd = os.environ['BBS_SVN_CMD']
    cmd = '%s up --set-depth infinity --non-interactive --username readonly --password readonly %s' % (svn_cmd, MEAT0_path)
    print("BBS> [update_svn_MEAT0] %s (at %s)" % (cmd, snapshot_date))
    bbs.jobs.doOrDie(cmd)
    return

def update_git_MEAT0(MEAT0_path, snapshot_date,
                     git_branch=None, manifest_git_branch=None):
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
    bbs.gitutils.clone_or_pull_repo(BBSvars.manifest_clone_path,
                                BBSvars.manifest_git_repo_url,
                                manifest_git_branch,
                                depth=1,
                                reclone_if_pull_fails=True)
    ## iterate over manifest to update pkg dirs
    pkgs = bbs.manifest.read(BBSvars.manifest_path)
    changed_pkgs = []
    i = 0
    for pkg in pkgs:
        i += 1
        print("BBS> ----------------------------------------------------------")
        print("BBS> [update_git_MEAT0] (%d/%d) repo: %s / branch: %s" % \
              (i, len(pkgs), pkg, git_branch))
        print()
        pkg_git_clone = os.path.join(MEAT0_path, pkg)
        pkg_git_repo_url = 'https://git.bioconductor.org/packages/%s' % pkg
        if BBSvars.buildtype == "bioc-incremental":
            snapshot_date = None
        pkg_has_changed = bbs.gitutils.clone_or_pull_repo(pkg_git_clone,
                                pkg_git_repo_url,
                                git_branch,
                                depth=1,
                                snapshot_date=snapshot_date,
                                reclone_if_pull_fails=True)
        if pkg_has_changed:
            changed_pkgs.append(pkg)
        if BBSvars.buildtype == "bioc-incremental":
            if pkg_has_changed:
                print("==> package has changed")
            else:
                print("==> package has not changed")
        print()
    print("BBS> -------------------------------------------------------------")
    print("BBS> END update_git_MEAT0()")
    print("BBS> %d/%d package(s) have changed since last pull" % \
          (len(changed_pkgs), len(pkgs)))
    print("BBS> ==============================================================")
    print()
    sys.stdout.flush()
    return changed_pkgs

def update_MEAT0(MEAT0_path, snapshot_date):
    print("BBS>")
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
        else:
            sys.exit("ERROR: Invalid BBS_MEAT0_TYPE: %d" % BBSvars.MEAT0_type)
    return

def writeAndUploadMeatInfo(work_topdir):
    MEAT0_path = BBSvars.MEAT0_rdir.path # Hopefully this is local!
    snapshot_date = bbs.jobs.currentDateString()
    if BBSvars.buildtype == "bioc-incremental":
        pkgs = update_git_MEAT0(MEAT0_path, snapshot_date)
    else:
        update_MEAT0(MEAT0_path, snapshot_date)
        manifest_path = BBSvars.manifest_path
        pkgs = bbs.manifest.read(manifest_path)
    buildAndUploadMeatIndex(pkgs, MEAT0_path)
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

def write_PACKAGES(rdir):
    doing_what = 'creating PACKAGES index file for target repo'
    print('BBS> START %s at %s...' % (doing_what, time.asctime()))
    sys.stdout.flush()
    Rexpr = r'library(tools);write_PACKAGES(\".\")'
    bbs.jobs.doOrDie(BBSbase.Rexpr2syscmd(Rexpr))
    ## write_PACKAGES() won't create an empty PACKAGES file if no packages
    ## are found so we create one.
    if not os.path.exists('PACKAGES'):
        f = open('PACKAGES', 'w')
        f.close()
    rdir.Put('PACKAGES', True, True)
    print('BBS> DONE %s at %s.' % (doing_what, time.asctime()))
    sys.stdout.flush()
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
    nb_products = bbs.jobs.processJobQueue(job_queue, nb_cpu, 900.0,
                                           verbose=True)
    dt = time.time() - t1
    print("BBS> END STAGE1 loop.")
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print("BBS> -------------------------------------------------------------")
    print("BBS> STAGE1 SUMMARY:")
    print("BBS>     o Working dir: %s" % os.getcwd())
    print("BBS>     o %d pkg(s) listed in file %s" % \
          (total, BBSutils.meat_index_file))
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
    print("BBS> [makeTargetRepo] Get list of pkgs from %s" % BBSutils.meat_index_file)
    meat_index_path = os.path.join(BBSvars.work_topdir,
                                   BBSutils.meat_index_file)
    pkgs = bbs.parse.get_meat_packages(meat_index_path)
    job_queue = prepare_STAGE1_job_queue(pkgs, rdir)
    ## STAGE1 will run 'tar zcf' commands to generate the no-vignettes source
    ## tarballs. Running too many concurrent 'tar zcf' commands seems harmful
    ## so we limit the nb of cpus to 2.
    #STAGE1_loop(job_queue, BBSvars.nb_cpu)
    STAGE1_loop(job_queue, 2)
    write_PACKAGES(rdir)
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
    Central_rdir = BBSvars.Central_rdir

    subtask = "make-central-rdir"
    if arg1 == "" or arg1 == subtask:
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        remakeCentralRdir(Central_rdir)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "upload-meat-info"
    if (arg1 == "" or arg1 == subtask) and \
       (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        writeAndUploadMeatInfo(work_topdir)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "create-local-meat-dir"
    if (arg1 == "" or arg1 == subtask) and \
       (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
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
        buildAndUploadMeatIndex(pkgs, meat_path)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))

    subtask = "make-target-repo"
    if arg1 == "" or arg1 == subtask:
        print("BBS> [prerun] STARTING %s at %s..." % (subtask, time.asctime()))
        Contrib_rdir = Central_rdir.subdir('src/contrib')
        makeTargetRepo(Contrib_rdir)
        print("BBS> [prerun] DONE %s at %s." % (subtask, time.asctime()))
