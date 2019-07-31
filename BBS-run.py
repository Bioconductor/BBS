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
import time
import urllib2

import bbs.fileutils
import bbs.parse
import bbs.jobs
import BBScorevars
import BBSvars
import BBSbase


##############################################################################
## Update NodeInfo
##############################################################################

# 'R --version' writes to the standard output on Unix/Linux/Mac and to
# the standard error on Windows :-/. Hence the '2>&1' in the command. 
def writeRversion():
    file = 'R-version.txt'
    syscmd = '%s --version >%s 2>&1' % (BBSvars.r_cmd, file)
    bbs.jobs.doOrDie(syscmd)
    return

def getRconfigValue(var):
    syscmd = '%s CMD config %s' % (BBSvars.r_cmd, var)
    val = bbs.jobs.getCmdOutput(syscmd)
    if len(val) and val[-1] == '\n':
        val = val[:-1]
    return val

def appendRconfigValue(file, var, is_first=False):
    val = getRconfigValue(var)
    if is_first and os.path.exists(file):
        os.remove(file)
    f = open(file, 'a')
    f.write('%s: %s\n' % (var, val))
    f.close()
    return

def writeRconfig():
    file = 'R-config.txt'
    appendRconfigValue(file, 'MAKE', True)
    C_vars = ['CC', 'CFLAGS', 'CPICFLAGS', 'CPP']
    Cplusplus_vars = ['CXX', 'CXXFLAGS', 'CXXPICFLAGS', 'CXXCPP']
    Cplusplus98_vars = ['CXX98', 'CXX98FLAGS', 'CXX98PICFLAGS', 'CXX98STD']
    Cplusplus11_vars = ['CXX11', 'CXX11FLAGS', 'CXX11PICFLAGS', 'CXX11STD']
    Cplusplus14_vars = ['CXX14', 'CXX14FLAGS', 'CXX14PICFLAGS', 'CXX14STD']
    Fortran77_vars = ['F77', 'FFLAGS', 'FLIBS', 'FPICFLAGS']
    Fortran9x_vars = ['FC', 'FCFLAGS', 'FCPICFLAGS']
    vars = C_vars + \
           Cplusplus_vars + \
           Cplusplus98_vars + \
           Cplusplus11_vars + \
           Cplusplus14_vars + \
           Fortran77_vars + \
           Fortran9x_vars
    for var in vars:
        appendRconfigValue(file, var)
    return

# If the command is not found (like gfortran on churchill) then the '2>&1'
# guarantees that 'file' will be created anyway but with the shell error
# message inside (e.g. '-bash: gfortran: command not found') instead of
# the command output. 
def writeSysCommandVersion(var):
    file = '%s-version.txt' % var
    cmd = getRconfigValue(var)
    if cmd.strip():
        syscmd = '%s --version >%s 2>&1' % (cmd, file)
        bbs.jobs.call(syscmd) # ignore retcode
    return

def makeNodeInfo():
    # Generate the NodeInfo files (the files containing some node related info)
    NodeInfo_subdir = "NodeInfo"
    print "BBS>   Updating BBS_WORK_TOPDIR/%s" % NodeInfo_subdir
    NodeInfo_path = os.path.join(BBSvars.work_topdir, NodeInfo_subdir)
    bbs.fileutils.remake_dir(NodeInfo_path)
    os.chdir(NodeInfo_path)
    writeRversion()
    writeRconfig()
    Rscript = "sessionInfo()"
    bbs.jobs.runJob(BBSbase.Rscript2syscmd(Rscript), \
                    'R-sessionInfo.txt', 60.0, True) # ignore retcode
    Rscript = "data.frame(installed.packages()[,c('Version','Built')])"
    bbs.jobs.runJob(BBSbase.Rscript2syscmd(Rscript), \
                    'R-instpkgs.txt', 60.0, True) # ignore retcode
    writeSysCommandVersion('CC')
    writeSysCommandVersion('CXX')
    writeSysCommandVersion('CXX98')
    writeSysCommandVersion('CXX11')
    writeSysCommandVersion('CXX14')
    writeSysCommandVersion('F77')
    writeSysCommandVersion('FC')
    print "BBS>   cd BBS_WORK_TOPDIR"
    os.chdir(BBSvars.work_topdir)
    BBSvars.Node_rdir.Put(NodeInfo_subdir, True, True)
    return


##############################################################################
## Misc utils
##############################################################################

def writeEndOfRunTicket(ticket):
    print "BBS> START making BBS_EndOfRun.txt Ticket."
    print "BBS>   cd BBS_MEAT_PATH"
    os.chdir(BBSvars.meat_path)
    file_path = "BBS_EndOfRun.txt"
    f = open(file_path, 'w')
    for t in ticket:
        f.write("%s | StartedAt: %s | EndedAt: %s | EllapsedTime: %.1f seconds\n" % t)
    f.close()
    BBSvars.Node_rdir.Put(file_path, True, True)
    print "BBS> END making BBS_EndOfRun.txt Ticket."
    return

def extractTargetPkgListFromMeatIndex():
    pkgType = BBScorevars.getNodeSpec(BBSvars.node_hostname, 'pkgType')
    Central_rdir = BBScorevars.Central_rdir
    dcf = Central_rdir.WOpen(BBScorevars.meat_index_file)
    target_pkgs = bbs.parse.readPkgsFromDCF(dcf, BBSvars.node_hostname, pkgType)
    dcf.close()
    return target_pkgs

def waitForTargetRepoToBeReady():
    Central_rdir = BBScorevars.Central_rdir
    PACKAGES_url = Central_rdir.url + '/src/contrib/PACKAGES'
    nb_attempts = 0
    while True:
        nb_attempts += 1
        try:
            f = urllib2.urlopen(PACKAGES_url)
        except urllib2.HTTPError:
            print "BBS> [waitForTargetRepoToBeReady]",
            print "Unable to access %s. " % PACKAGES_url + \
                  "Looks like the target repo is not ready yet!"
        else:
            break
        if nb_attempts == 30:
            print "BBS> [waitForTargetRepoToBeReady]",
            print "FATAL ERROR: was unable to access %s after %d attempts. " % \
                  (PACKAGES_url, nb_attempts) + "Giving up."
            sys.exit("=> EXIT.")
        print "BBS> [waitForTargetRepoToBeReady]",
        print "-> will wait 3 minutes before trying again ..."
        sys.stdout.flush()
        bbs.jobs.sleep(180.0)
    f.close()
    return


##############################################################################
## STAGE2: Update ALL packages and re-install target packages + dependencies.
##############################################################################

def make_STAGE2_pkg_deps_list(target_pkgs):
    # Make 'target_pkgs.txt' file.
    target_pkgs_file = "target_pkgs.txt"
    out = open(target_pkgs_file, 'w')
    for pkg in target_pkgs:
        out.write("%s\n" % pkg)
    out.close()
    print "BBS> [make_STAGE2_pkg_deps_list]",
    print "%s pkgs written to %s" % (len(target_pkgs), target_pkgs_file)

    # Make 'STAGE2_pkg_deps_list.txt' file.
    Rfunction = "make_STAGE2_pkg_deps_list"
    script_path = os.path.join(BBScorevars.BBS_home,
                               "utils",
                               "make_STAGE2_pkg_deps_list.R")
    STAGE2_pkg_deps_list_path = "STAGE2_pkg_deps_list.txt"
    print "BBS> [make_STAGE2_pkg_deps_list]",
    print "Calling %s() defined in %s to make %s file ..." % \
          (Rfunction, script_path, STAGE2_pkg_deps_list_path),
    # Backslashes in the paths injected in 'Rscript' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslashes.
    script_path2 = script_path.replace('\\', '/')
    target_pkgs_file2 = target_pkgs_file.replace('\\', '/')
    STAGE2_pkg_deps_list_path2 = STAGE2_pkg_deps_list_path.replace('\\', '/')
    # Use short.list=TRUE to skip installation of target packages not needed
    # by another target package for build or check.
    #Rscript = "source('%s');%s('%s',outfile='%s',short.list=TRUE)" % \
    Rscript = "source('%s');%s('%s',outfile='%s')" % \
              (script_path2, Rfunction, target_pkgs_file2,
               STAGE2_pkg_deps_list_path2)
    out_file = Rfunction + ".Rout"
    bbs.jobs.runJob(BBSbase.Rscript2syscmd(Rscript), out_file) # ignore retcode
    print "OK"

    # Load 'STAGE2_pkg_deps_list.txt' file.
    print "BBS> [make_STAGE2_pkg_deps_list] Loading %s file ..." % \
          STAGE2_pkg_deps_list_path,
    f = open(STAGE2_pkg_deps_list_path, 'r')
    pkg_deps_list = {}
    EMPTY_STRING = ''
    for line in f:
        (pkg, deps) = line.split(":")
        deps = deps.strip().split(" ")
        if EMPTY_STRING in deps:
            deps.remove(EMPTY_STRING)
        pkg_deps_list[pkg] = deps
    f.close()
    print "OK (%s pkgs and their deps loaded)" % len(pkg_deps_list)

    print "BBS> [make_STAGE2_pkg_deps_list] DONE."
    return pkg_deps_list

def get_installed_pkgs():
    installed_pkgs_path = "installed_pkgs.txt"
    Rscript = "writeLines(rownames(installed.packages()),'%s')" % \
              installed_pkgs_path
    out_file = "get_installed_pkgs.Rout"
    bbs.jobs.runJob(BBSbase.Rscript2syscmd(Rscript), out_file) # ignore retcode
    installed_pkgs = []
    f = open(installed_pkgs_path, 'r')
    for line in f:
        installed_pkgs.append(line.strip())
    f.close()
    print "BBS> [get_installed_pkgs] %s installed pkgs" % len(installed_pkgs)
    return installed_pkgs

def CallRfunctionFromSTAGE2Script(Rfunction, out_file=None):
    print "BBS> [%s] BEGIN ..." % Rfunction
    script_path = BBSvars.STAGE2_r_script
    # Backslahes in the paths injected in 'Rscript' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslahes.
    script_path = script_path.replace('\\', '/')
    Rscript = "source('%s');%s()" % (script_path, Rfunction)
    if out_file == None:
        out_file = '%s.Rout' % Rfunction
    bbs.jobs.runJob(BBSbase.Rscript2syscmd(Rscript), out_file, 3600.0) # ignore retcode
    print "BBS> [%s] END." % Rfunction
    return

def CreateREnvironFiles():
    archs = ("i386", "x64")
    for arch in archs:
        archup = arch.upper()
        filename = "%s/etc/%s/Renviron.site" % (BBSvars.r_home, arch)
        f = open(filename, 'w')
        graphviz_install_dir = os.environ["GRAPHVIZ_INSTALL_DIR_%s" % archup]
        f.write("GRAPHVIZ_INSTALL_DIR=%s\n" % graphviz_install_dir)
        graphviz_install_major = os.environ["GRAPHVIZ_INSTALL_MAJOR_%s" %
          archup]
        f.write("GRAPHVIZ_INSTALL_MAJOR=%s\n" % graphviz_install_major)
        graphviz_install_minor = os.environ["GRAPHVIZ_INSTALL_MINOR_%s" %
          archup]
        f.write("GRAPHVIZ_INSTALL_MINOR=%s\n" % graphviz_install_minor)
        graphviz_install_subminor = os.environ["GRAPHVIZ_INSTALL_SUBMINOR_%s" %
          archup]
        f.write("GRAPHVIZ_INSTALL_SUBMINOR=%s\n" % graphviz_install_subminor)
        f.close()

def prepare_STAGE2_job_queue(target_pkgs, pkg_deps_list, installed_pkgs):
    print "BBS> Preparing STAGE2 job queue ... ",
    stage = 'install'
    jobs = []
    nb_target_pkgs_in_queue = nb_skipped_pkgs = 0
    for pkg in pkg_deps_list.keys():
        version = None
        pkgdumps_prefix = pkg + '.' + stage
        pkgdumps = BBSbase.PkgDumps(None, pkgdumps_prefix)
        if pkg in target_pkgs:
            try:
                version = bbs.parse.getVersionFromDir(pkg)
            except IOError:
                print "BBS>   Can't read %s/DESCRIPTION file!" % pkg
            cmd = BBSbase.getSTAGE2cmd(pkg, version)
            nb_target_pkgs_in_queue += 1
        else:
            if pkg in installed_pkgs:
                cmd = pkgdumps = None
                nb_skipped_pkgs += 1
            else:
                cmd = BBSbase.getSTAGE2cmdForNonTargetPkg(pkg)
        job = BBSbase.InstallPkg_Job(pkg, version, cmd,
                                     pkgdumps, BBSvars.install_rdir)
        jobs.append(job)
    nb_jobs = len(jobs)
    print "OK"
    nb_not_needed = len(target_pkgs) - nb_target_pkgs_in_queue
    nb_non_target_pkgs_in_queue = nb_jobs - nb_target_pkgs_in_queue
    nb_non_target_pkgs_to_install = nb_non_target_pkgs_in_queue - \
                                    nb_skipped_pkgs
    nb_pkgs_to_install = nb_jobs - nb_skipped_pkgs
    print "BBS> Job summary:"
    print "BBS> | %d (out of %d) target pkgs are not supporting pkgs" % \
          (nb_not_needed, len(target_pkgs))
    print "BBS> |   => no need to install them"
    print "BBS> |   => they're not going in the installation queue"
    print "BBS> | %d pkgs in the installation queue (all supporting pkgs):" % \
          nb_jobs
    print "BBS> |   o %d are target pkgs" % nb_target_pkgs_in_queue
    print "BBS> |       => will (re-)install them with 'R CMD INSTALL'"
    print "BBS> |   o %d are non-target pkgs:" % nb_non_target_pkgs_in_queue
    print "BBS> |     - %d are already installed" % nb_skipped_pkgs
    print "BBS> |         => won't re-install them (job will be skipped)"
    print "BBS> |     - %d are not already installed" % \
          nb_non_target_pkgs_to_install
    print "BBS> |         => will install them with"
    print "BBS> |              install.packages(pkg, repos=non_target_repos,"
    print "BBS> |                               dep=FALSE, ...)"
    print "BBS> | Total nb of packages to install: %d" % nb_pkgs_to_install
    print "BBS>"
    job_queue = bbs.jobs.JobQueue(stage, jobs, pkg_deps_list)
    job_queue._nb_pkgs_to_install = nb_pkgs_to_install
    return job_queue

def STAGE2_loop(job_queue, nb_cpu):
    print "BBS> BEGIN STAGE2 loop."
    t1 = time.time()
    nb_installed = bbs.jobs.processJobQueue(job_queue, nb_cpu,
                                            BBScorevars.r_cmd_timeout, True)
    dt = time.time() - t1
    print "BBS> END STAGE2 loop."
    nb_jobs = len(job_queue._jobs)
    nb_pkgs_to_install = job_queue._nb_pkgs_to_install
    nb_failures = nb_pkgs_to_install - nb_installed
    print "BBS> -------------------------------------------------------------"
    print "BBS> STAGE2 SUMMARY:"
    print "BBS>   o Working dir: %s" % os.getcwd()
    print "BBS>   o %d pkg dir(s) queued and processed" % nb_jobs
    print "BBS>   o %d pkg(s) to (re-)install: %d successes / %d failures" % \
          (nb_pkgs_to_install, nb_installed, nb_failures)
    print "BBS>   o Total time: %.2f seconds" % dt
    print "BBS> -------------------------------------------------------------"
    return

def STAGE2():
    print "BBS> [STAGE2] STARTING STAGE2 at %s..." % time.asctime()
    # We want to make sure the target repo is ready before we actually start
    # (if it's not ready yet it probably means that the prerun.sh script did
    # not finish on the main node, in which case we want to wait before we
    # sync the local meat dir with the central MEAT0 dir).
    waitForTargetRepoToBeReady()

    meat_path = BBSvars.meat_path
    BBSvars.MEAT0_rdir.syncLocalDir(meat_path, True)
    if BBSvars.MEAT0_type == 2:
        srcpkg_files = bbs.fileutils.listSrcPkgFiles(meat_path)
        for srcpkg_file in srcpkg_files:
            srcpkg_filepath = os.path.join(meat_path, srcpkg_file)
            BBSbase.Untar(srcpkg_filepath, meat_path)
            os.remove(srcpkg_filepath)

    print "BBS> [STAGE2] cd BBS_WORK_TOPDIR/gitlog"
    gitlog_path = BBSvars.gitlog_path
    BBSvars.GITLOG_rdir.syncLocalDir(gitlog_path, True)

    print "BBS> [STAGE2] cd BBS_WORK_TOPDIR/STAGE2_tmp"
    STAGE2_tmp = os.path.join(BBSvars.work_topdir, "STAGE2_tmp")
    bbs.fileutils.remake_dir(STAGE2_tmp)
    os.chdir(STAGE2_tmp)

    # Re-create architecture-specific Renviron.site files on multi-arch
    # build machines.
    if ('BBS_STAGE2_MODE' in os.environ and
      os.environ['BBS_STAGE2_MODE'] == 'multiarch' and
      BBScorevars.subbuilds == "bioc"):
        CreateREnvironFiles()

    # Try to update all installed packages.
    CallRfunctionFromSTAGE2Script("updateNonTargetPkgs",
                                  "updateNonTargetPkgs1.Rout")

    # Extract list of target packages.
    target_pkgs = extractTargetPkgListFromMeatIndex()

    # Get 'pkg_deps_list' and 'installed_pkgs'.
    pkg_deps_list = make_STAGE2_pkg_deps_list(target_pkgs)
    installed_pkgs = get_installed_pkgs()

    # Inject additional fields into DESCRIPTION.
    print "BBS> [STAGE2] cd BBS_MEAT_PATH"
    print "BBS> [STAGE2] Injecting fields into DESCRIPTION"
    os.chdir(meat_path)
    for pkg in target_pkgs:

        gitlog_file = os.path.join(BBSvars.gitlog_path, "git-log-%s.dcf" % pkg)
        if not os.path.exists(gitlog_file):
            print "BBS> %s file does not exist --> skipping." % gitlog_file
            continue 

        desc_file = os.path.join(BBSvars.meat_path, pkg, 'DESCRIPTION')
        if not os.path.exists(desc_file):
            print "BBS> %s file does not exist --> skipping." % desc_file
            continue 

        bbs.parse.injectFieldsInDESCRIPTION(desc_file, gitlog_file)

    # Then re-install the supporting packages.
    print "BBS> [STAGE2] Re-install supporting packages"
    os.chdir(meat_path)
    BBSvars.install_rdir.RemakeMe(True)
    job_queue = prepare_STAGE2_job_queue(target_pkgs, pkg_deps_list,
                                         installed_pkgs)
    STAGE2_loop(job_queue, BBSvars.nb_cpu)

    print "BBS> [STAGE2] cd BBS_WORK_TOPDIR/STAGE2_tmp"
    os.chdir(STAGE2_tmp)
    # Try again to update all installed packages (some updates could have
    # failed in the previous attempt because of dependency issues).
    CallRfunctionFromSTAGE2Script("updateNonTargetPkgs",
                                  "updateNonTargetPkgs2.Rout")

    print "BBS> [STAGE2] DONE at %s." % time.asctime()
    return


##############################################################################
## STAGE3: Build the srcpkg files.
##############################################################################

def prepare_STAGE3_job_queue(pkgdir_paths):
    print "BBS> Preparing STAGE3 job queue ... ",
    stage = 'buildsrc'
    jobs = []
    for pkgdir_path in pkgdir_paths:
        try:
            pkg = bbs.parse.getPkgFromDir(pkgdir_path)
            version = bbs.parse.getVersionFromDir(pkgdir_path)
            srcpkg_file = bbs.parse.getSrcPkgFileFromDir(pkgdir_path)
        except IOError:
            print "BBS>   Can't read DESCRIPTION file!"
        else:
            cmd = BBSbase.getSTAGE3cmd(pkgdir_path)
            pkgdumps_prefix = pkg + '.' + stage
            pkgdumps = BBSbase.PkgDumps(srcpkg_file, pkgdumps_prefix)
            job = BBSbase.BuildPkg_Job(pkg, version, cmd,
                                       pkgdumps, BBSvars.buildsrc_rdir)
            jobs.append(job)
    print "OK"
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(pkgdir_paths)
    return job_queue

def STAGE3_loop(job_queue, nb_cpu):
    print "BBS> BEGIN STAGE3 loop."
    t1 = time.time()
    nb_products = bbs.jobs.processJobQueue(job_queue, nb_cpu,
                                           BBScorevars.r_cmd_timeout, True)
    dt = time.time() - t1
    print "BBS> END STAGE3 loop."
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print "BBS> -------------------------------------------------------------"
    print "BBS> STAGE3 SUMMARY:"
    print "BBS>   o Working dir: %s" % os.getcwd()
    print "BBS>   o %d pkg(s) listed in file BBS_CENTRAL_BASEURL/%s" % \
          (total, BBScorevars.meat_index_file)
    print "BBS>   o %d pkg dir(s) queued and processed" % nb_jobs
    print "BBS>   o %d srcpkg file(s) produced" % nb_products
    print "BBS>   o Total time: %.2f seconds" % dt
    print "BBS> -------------------------------------------------------------"
    return

def STAGE3():
    print "BBS> [STAGE3] STARTING STAGE3 at %s..." % time.asctime()
    BBSvars.buildsrc_rdir.RemakeMe(True)
    makeNodeInfo()
    print "BBS> [STAGE3] cd BBS_MEAT_PATH"
    target_pkgs = extractTargetPkgListFromMeatIndex()
    meat_path = BBSvars.meat_path
    if BBScorevars.subbuilds == "bioc-longtests":
        bbs.fileutils.remake_dir(meat_path)
        os.chdir(meat_path)
        for pkg in target_pkgs:
            rdir = BBSvars.MEAT0_rdir.subdir(pkg)
            local_dir = os.path.join(meat_path, pkg)
            rdir.syncLocalDir(local_dir, True)
    else:
        os.chdir(meat_path)
    job_queue = prepare_STAGE3_job_queue(target_pkgs)
    STAGE3_loop(job_queue, BBSvars.nb_cpu)
    print "BBS> [STAGE3] DONE at %s." % time.asctime()
    return


##############################################################################
## STAGE4: Check the srcpkg files.
##############################################################################

# IMPLEMENT ME: Use BBSvars.buildsrc_rdir.List()
# and compare with srcpkg_files. If local srcpkg files are missing,
# then raise an error.
def CheckLocalSrcpkgFiles(srcpkg_files):
    sys.exit("IMPLEMENT ME!")
    return

def prepare_STAGE4_job_queue(srcpkg_paths):
    print "BBS> Preparing STAGE4 job queue ... ",
    stage = 'checksrc'
    jobs = []
    for srcpkg_path in srcpkg_paths:
        cmd = BBSbase.getSTAGE4cmd(srcpkg_path)
        if cmd == None:
            continue
        pkg = bbs.parse.getPkgFromPath(srcpkg_path)
        version = bbs.parse.getVersionFromPath(srcpkg_path)
        check_dir = pkg + '.Rcheck'
        pkgdumps_prefix = pkg + '.' + stage
        pkgdumps = BBSbase.PkgDumps(check_dir, pkgdumps_prefix)
        job = BBSbase.CheckSrc_Job(pkg, version, cmd,
                                   pkgdumps, BBSvars.checksrc_rdir)
        jobs.append(job)
    print "OK"
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(srcpkg_paths)
    return job_queue

def STAGE4_loop(job_queue, nb_cpu):
    print "BBS> BEGIN STAGE4 loop."
    t1 = time.time()
    bbs.jobs.processJobQueue(job_queue, nb_cpu,
                             BBScorevars.r_cmd_timeout, True)
    dt = time.time() - t1
    print "BBS> END STAGE4 loop."
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print "BBS> -------------------------------------------------------------"
    print "BBS> STAGE4 SUMMARY:"
    print "BBS>   o Working dir: %s" % os.getcwd()
    print "BBS>   o %d srcpkg file(s) in working dir" % total
    print "BBS>   o %d srcpkg file(s) queued and processed" % nb_jobs
    print "BBS>   o Total time: %.2f seconds" % dt
    print "BBS> -------------------------------------------------------------"
    return

def STAGE4():
    print "BBS> [STAGE4] STARTING STAGE4 at %s..." % time.asctime()
    BBSvars.checksrc_rdir.RemakeMe(True)
    print "BBS> [STAGE4] cd BBS_MEAT_PATH"
    os.chdir(BBSvars.meat_path)
    print "BBS> [STAGE4] Get list of srcpkg files found in current dir"
    srcpkg_paths = bbs.fileutils.listSrcPkgFiles()
    #CheckLocalSrcpkgFiles(srcpkg_paths)
    job_queue = prepare_STAGE4_job_queue(srcpkg_paths)
    STAGE4_loop(job_queue, BBSvars.check_nb_cpu)
    print "BBS> [STAGE4] DONE at %s." % time.asctime()
    return


##############################################################################
## STAGE5: Build the binpkg files.
##############################################################################

def prepare_STAGE5_job_queue(srcpkg_paths):
    print "BBS> Preparing STAGE5 job queue ... ",
    stage = 'buildbin'
    jobs = []
    for srcpkg_path in srcpkg_paths:
        cmd = BBSbase.getSTAGE5cmd(srcpkg_path)
        if cmd == None:
            continue
        pkg = bbs.parse.getPkgFromPath(srcpkg_path)
        version = bbs.parse.getVersionFromPath(srcpkg_path)
        fileext = BBScorevars.getNodeSpec(BBSvars.node_hostname, 'pkgFileExt')
        binpkg_file = "%s_%s.%s" % (pkg, version, fileext)
        pkgdumps_prefix = pkg + '.' + stage
        pkgdumps = BBSbase.PkgDumps(binpkg_file, pkgdumps_prefix)
        job = BBSbase.BuildPkg_Job(pkg, version, cmd,
                                   pkgdumps, BBSvars.buildbin_rdir)
        jobs.append(job)
    print "OK"
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(srcpkg_paths)
    return job_queue

def STAGE5_loop(job_queue, nb_cpu):
    print "BBS> BEGIN STAGE5 loop."
    t1 = time.time()
    nb_products = bbs.jobs.processJobQueue(job_queue, nb_cpu,
                                           BBScorevars.r_cmd_timeout, True)
    dt = time.time() - t1
    print "BBS> END STAGE5 loop."
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print "BBS> -------------------------------------------------------------"
    print "BBS> STAGE5 SUMMARY:"
    print "BBS>   o Working dir: %s" % os.getcwd()
    print "BBS>   o %d srcpkg file(s) in working dir" % total
    print "BBS>   o %d srcpkg file(s) queued and processed" % nb_jobs
    print "BBS>   o %d binpkg file(s) produced" % nb_products
    print "BBS>   o Total time: %.2f seconds" % dt
    print "BBS> -------------------------------------------------------------"
    return

def STAGE5():
    print "BBS> [STAGE5] STARTING STAGE5 at %s..." % time.asctime()
    BBSvars.buildbin_rdir.RemakeMe(True)
    print "BBS> [STAGE5] cd BBS_MEAT_PATH"
    os.chdir(BBSvars.meat_path)
    print "BBS> [STAGE5] Get list of srcpkg files found in current dir"
    srcpkg_paths = bbs.fileutils.listSrcPkgFiles()
    #CheckLocalSrcpkgFiles(srcpkg_paths)
    job_queue = prepare_STAGE5_job_queue(srcpkg_paths)
    STAGE5_loop(job_queue, BBSvars.nb_cpu)
    print "BBS> [STAGE5] DONE at %s." % time.asctime()
    return

##############################################################################
## MAIN SECTION
##############################################################################

if __name__ == "__main__":
    print
    print "BBS> =============================================================="
    argc = len(sys.argv)
    if argc > 1:
        arg1 = sys.argv[1]
    else:
        arg1 = ""
    if argc > 2:
        arg2 = sys.argv[2]
    else:
        arg2 = ""
    if arg1 in ["", "no-bin"]:
        BBSvars.Node_rdir.RemakeMe(True)
    ticket = []
    ## STAGE2: preinstall dependencies
    if arg1 in ["", "no-bin"] or "STAGE2" in sys.argv:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE2()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE2', started_at, ended_at, dt))
    ## STAGE3: build source packages
    if arg1 in ["", "no-bin"] or "STAGE3" in sys.argv:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE3()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE3', started_at, ended_at, dt))
    ## STAGE4: check source packages
    if arg1 in ["", "no-bin"] or "STAGE4" in sys.argv:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE4()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE4', started_at, ended_at, dt))
    ## STAGE5: build bin packages
    if arg1 == "" or "STAGE5" in sys.argv:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE5()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE5', started_at, ended_at, dt))
    writeEndOfRunTicket(ticket)
