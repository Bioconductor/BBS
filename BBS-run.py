#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: May 31, 2023
###

import sys
import os
import time
import urllib.request
from functools import lru_cache

import bbs.fileutils
import bbs.parse
import bbs.jobs
import BBSutils
import BBSvars
import BBSbase

if not BBSvars.synchronous_transmission:
    products_out_buf = os.path.join(BBSvars.work_topdir, 'products-out')

def make_stage_out_dir(stage):
    out_dir = os.path.join(products_out_buf, stage)
    if os.path.exists(products_out_buf):
        bbs.fileutils.remake_dir(out_dir, ignore_errors=True)
    else:
        os.mkdir(products_out_buf)
        os.mkdir(out_dir)
    print('BBS>   products-out subdir: %s' % out_dir)
    return out_dir

def make_products_push_cmd(out_dir, rdir):
    if sys.platform == "win32":
        out_dir = bbs.fileutils.to_cygwin_style(out_dir)
    dest = rdir.get_full_remote_path()
    return '%s -av %s/ %s' % (BBSvars.rsync_rsh_cmd, out_dir, dest)


##############################################################################
## Update NodeInfo
##############################################################################

# 'R --version' writes to the standard output on Unix/Linux/Mac and to
# the standard error on Windows :-/. Hence the '2>&1' in the command.
def write_R_version():
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

def write_R_config():
    file = 'R-config.txt'
    appendRconfigValue(file, 'MAKE', True)
    C_vars = ['CC', 'CFLAGS', 'CPICFLAGS']
    Cplusplus_vars = ['CXX', 'CXXFLAGS', 'CXXPICFLAGS']
    #Cplusplus98_vars = ['CXX98', 'CXX98FLAGS', 'CXX98PICFLAGS', 'CXX98STD']
    Cplusplus11_vars = ['CXX11', 'CXX11FLAGS', 'CXX11PICFLAGS', 'CXX11STD']
    Cplusplus14_vars = ['CXX14', 'CXX14FLAGS', 'CXX14PICFLAGS', 'CXX14STD']
    Cplusplus17_vars = ['CXX17', 'CXX17FLAGS', 'CXX17PICFLAGS', 'CXX17STD']
    #Fortran77_vars = ['F77', 'FFLAGS', 'FLIBS', 'FPICFLAGS']
    #Fortran9x_vars = ['FC', 'FCFLAGS', 'FCPICFLAGS']
    #vars = C_vars + \
    #       Cplusplus_vars + \
    #       Cplusplus98_vars + \
    #       Cplusplus11_vars + \
    #       Cplusplus14_vars + \
    #       Fortran77_vars + \
    #       Fortran9x_vars
    vars = C_vars + \
           Cplusplus_vars + \
           Cplusplus11_vars + \
           Cplusplus14_vars + \
           Cplusplus17_vars
    for var in vars:
        appendRconfigValue(file, var)
    return

# If the command is not found (like gfortran on churchill) then the '2>&1'
# guarantees that 'file' will be created anyway but with the shell error
# message inside (e.g. '-bash: gfortran: command not found') instead of
# the command output.
def write_sys_command_version(var, config=True):
    file = '%s-version.txt' % var
    if config:
        cmd = getRconfigValue(var)
    else:
        cmd = var
    if cmd.strip():
        syscmd = '%s --version >%s 2>&1' % (cmd, file)
        bbs.jobs.call(syscmd) # ignore retcode
    return

def makeNodeInfo():
    # Generate the NodeInfo files (the files containing some node related info)
    NodeInfo_subdir = 'NodeInfo'
    print('BBS>   Updating BBS_WORK_TOPDIR/%s' % NodeInfo_subdir)
    NodeInfo_path = os.path.join(BBSvars.work_topdir, NodeInfo_subdir)
    bbs.fileutils.remake_dir(NodeInfo_path)
    os.chdir(NodeInfo_path)
    write_R_version()
    write_R_config()
    write_sys_command_version('CC')
    write_sys_command_version('CXX')
    #write_sys_command_version('CXX98')
    write_sys_command_version('CXX11')
    write_sys_command_version('CXX14')
    write_sys_command_version('CXX17')
    #write_sys_command_version('F77')
    #write_sys_command_version('FC')
    write_sys_command_version('JAVA')
    write_sys_command_version('pandoc', False)
    Rexpr = 'sessionInfo()'
    bbs.jobs.runJob(BBSbase.Rexpr2syscmd(Rexpr), \
                    'R-sessionInfo.txt', 60.0, True) # ignore retcode
    Rexpr = "options(width=500);print(installed.packages()[,c('LibPath','Version','Built')],quote=FALSE)"
    bbs.jobs.runJob(BBSbase.Rexpr2syscmd(Rexpr), \
                    'R-instpkgs.txt', 120.0, True) # ignore retcode
    print('BBS>   cd BBS_WORK_TOPDIR')
    os.chdir(BBSvars.work_topdir)
    if BBSvars.no_transmission:
        BBSutils.copyTheDamnedThingNoMatterWhat(NodeInfo_subdir,
                                                products_out_buf)
    else:
        BBSvars.Node_rdir.Put(NodeInfo_subdir, True, True)
    return


##############################################################################
## Misc utils
##############################################################################

def write_BBS_EndOfRun_ticket(ticket):
    print('BBS> START writing BBS_EndOfRun.txt ticket.')
    print('BBS>   cd BBS_MEAT_PATH')
    os.chdir(BBSvars.meat_path)
    file_path = 'BBS_EndOfRun.txt'
    f = open(file_path, 'w')
    for t in ticket:
        f.write('%s | nb_cpu=%d | StartedAt: %s | EndedAt: %s | EllapsedTime: %.1f seconds\n' % t)
    f.close()
    if BBSvars.no_transmission:
        BBSutils.copyTheDamnedThingNoMatterWhat(file_path, products_out_buf)
    else:
        BBSvars.Node_rdir.Put(file_path, True, True)
    print('BBS> END writing BBS_EndOfRun.txt ticket.')
    return

## Get list of target packages from meat index file located on central
## builder. Memoized.
@lru_cache  # clear cache with get_list_of_target_pkgs.cache_clear()
def get_list_of_target_pkgs():
    print('BBS> [get_list_of_target_pkgs]', end=' ')
    meat_index_path = BBSutils.downloadFile(BBSutils.meat_index_file,
                                            BBSvars.central_base_url,
                                            BBSvars.meat_path)
    node_hostname = BBSvars.node_hostname
    node_Arch = BBSutils.getNodeSpec(node_hostname, 'Arch')
    node_pkgType = BBSutils.getNodeSpec(node_hostname, 'pkgType')
    return bbs.parse.get_meat_packages_for_node(meat_index_path,
                                                node_hostname,
                                                node_Arch,
                                                node_pkgType)

def getSrcPkgFilesFromSuccessfulSTAGE3(stage_label):
    print('BBS> Get list of source tarballs to %s ...' % stage_label, end=' ')
    sys.stdout.flush()
    target_pkgs = get_list_of_target_pkgs()
    stage = 'buildsrc'
    ok_statuses = ['OK', 'WARNINGS']
    srcpkg_files = []
    for target_pkg in target_pkgs:
        summary_file = '%s.%s-summary.dcf' % (target_pkg, stage)
        try:
            dcf = open(summary_file, 'rb')
        except IOError:
            continue
        status = bbs.parse.get_next_DCF_val(dcf, 'Status')
        srcpkg_file = bbs.parse.get_next_DCF_val(dcf, 'PackageFile')
        dcf.close()
        if status in ok_statuses:
            srcpkg_files.append(srcpkg_file)
    print('OK')
    sys.stdout.flush()
    return srcpkg_files

def waitForTargetRepoToBeReady():
    PACKAGES_url = BBSvars.central_base_url + '/src/contrib/PACKAGES'
    nb_attempts = 0
    while True:
        nb_attempts += 1
        try:
            f = urllib.request.urlopen(PACKAGES_url)
        except urllib.error.HTTPError:
            print('BBS> [waitForTargetRepoToBeReady]', end=' ')
            print('Unable to access %s. ' % PACKAGES_url + \
                  'Looks like the target repo is not ready yet!')
        else:
            break
        if nb_attempts == 30:
            print('BBS> [waitForTargetRepoToBeReady]', end=' ')
            print('FATAL ERROR: was unable to access %s after %d attempts. ' % \
                  (PACKAGES_url, nb_attempts) + 'Giving up.')
            sys.exit('=> EXIT.')
        print('BBS> [waitForTargetRepoToBeReady]', end=' ')
        print('-> will wait 3 minutes before trying again ...')
        sys.stdout.flush()
        bbs.jobs.sleep(180.0)
    f.close()
    return


##############################################################################
## STAGE2: Update ALL packages and re-install target packages + dependencies.
##############################################################################

def build_pkg_dep_graph(target_pkgs):
    # Generate file 'target_pkgs.txt'.
    target_pkgs_file = 'target_pkgs.txt'
    out = open(target_pkgs_file, 'w')
    for pkg in target_pkgs:
        out.write('%s\n' % pkg)
    out.close()
    print('BBS> [build_pkg_dep_graph]', end=' ')
    print('%s pkgs written to %s' % (len(target_pkgs), target_pkgs_file))

    # Generate file 'pkg_dep_graph.txt'.
    Rfunction = 'build_pkg_dep_graph'
    script_path = os.path.join(BBSvars.BBS_home,
                               'utils',
                               'build_pkg_dep_graph.R')
    print('BBS> [build_pkg_dep_graph]', end=' ')
    print('Calling %s() defined in %s to generate file %s ...' % \
          (Rfunction, script_path, BBSutils.pkg_dep_graph_file), end=' ')
    sys.stdout.flush()
    # Backslashes in the paths injected in 'Rexpr' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslashes.
    script_path2 = script_path.replace('\\', '/')
    target_pkgs_file2 = target_pkgs_file.replace('\\', '/')
    STAGE2_pkg_dep_graph_path2 = BBSutils.pkg_dep_graph_file.replace('\\', '/')
    # Use short.list=TRUE for "smart STAGE2" i.e. to skip installation of
    # target packages not needed by another target package for build or check.
    #Rexpr = "source('%s');%s('%s',outfile='%s',short.list=TRUE)" % \
    Rexpr = "source('%s');%s('%s',outfile='%s')" % \
              (script_path2, Rfunction, target_pkgs_file2,
               STAGE2_pkg_dep_graph_path2)
    out_file = Rfunction + '.Rout'
    cmd = BBSbase.Rexpr2syscmd(Rexpr)
    retcode = bbs.jobs.runJob(cmd, out_file)
    if retcode != 0:
        print('ERROR!')
        print('BBS> [build_pkg_dep_graph] Command %s' % cmd, end=' ')
        print('returned an error (%d)' % retcode, end=' ')
        sys.stdout.flush()
        sys.exit('=> EXIT.')
    print('OK')

    # Send file 'pkg_dep_graph.txt' to central build node.
    if BBSvars.no_transmission:
        BBSutils.copyTheDamnedThingNoMatterWhat(BBSutils.pkg_dep_graph_file,
                                                products_out_buf)
    else:
        BBSvars.Node_rdir.Put(BBSutils.pkg_dep_graph_file, True, True)

    # Load file 'pkg_dep_graph.txt'.
    print('BBS> [build_pkg_dep_graph] Loading %s file ...' % \
          BBSutils.pkg_dep_graph_file, end=' ')
    pkg_dep_graph = bbs.parse.load_pkg_dep_graph(BBSutils.pkg_dep_graph_file)
    print('OK (%s pkgs and their deps loaded)' % len(pkg_dep_graph))

    print('BBS> [build_pkg_dep_graph] DONE.')
    return pkg_dep_graph

def get_installed_pkgs():
    installed_pkgs_path = 'installed_pkgs.txt'
    Rexpr = "writeLines(rownames(installed.packages()),'%s')" % \
            installed_pkgs_path
    out_file = 'get_installed_pkgs.Rout'
    bbs.jobs.runJob(BBSbase.Rexpr2syscmd(Rexpr), out_file) # ignore retcode
    installed_pkgs = []
    f = open(installed_pkgs_path, 'r')
    for line in f:
        installed_pkgs.append(line.strip())
    f.close()
    print('BBS> [get_installed_pkgs] %s installed pkgs' % len(installed_pkgs))
    return installed_pkgs

#def CreateREnvironFiles():
#    archs = ('i386', 'x64')
#    for arch in archs:
#        archup = arch.upper()
#        filename = '%s/etc/%s/Renviron.site' % (BBSvars.r_home, arch)
#        f = open(filename, 'w')
#        graphviz_install_dir = os.environ['GRAPHVIZ_INSTALL_DIR_%s' % archup]
#        f.write('GRAPHVIZ_INSTALL_DIR=%s\n' % graphviz_install_dir)
#        graphviz_install_major = os.environ['GRAPHVIZ_INSTALL_MAJOR_%s' %
#          archup]
#        f.write('GRAPHVIZ_INSTALL_MAJOR=%s\n' % graphviz_install_major)
#        graphviz_install_minor = os.environ['GRAPHVIZ_INSTALL_MINOR_%s' %
#          archup]
#        f.write('GRAPHVIZ_INSTALL_MINOR=%s\n' % graphviz_install_minor)
#        graphviz_install_subminor = os.environ['GRAPHVIZ_INSTALL_SUBMINOR_%s' %
#          archup]
#        f.write('GRAPHVIZ_INSTALL_SUBMINOR=%s\n' % graphviz_install_subminor)
#        f.close()

def prepare_STAGE2_job_queue(target_pkgs, pkg_dep_graph,
                             installed_pkgs, out_dir):
    print('BBS> Preparing STAGE2 job queue ...', end=' ')
    sys.stdout.flush()
    stage = 'install'
    jobs = []
    nb_target_pkgs_in_queue = nb_skipped_pkgs = 0
    for pkg in pkg_dep_graph.keys():
        version = None
        pkgdumps_prefix = pkg + '.' + stage
        pkgdumps = BBSbase.PkgDumps(None, pkgdumps_prefix)
        if pkg in target_pkgs:
            version = bbs.parse.get_Version_from_pkgsrctree(pkg)
            cmd = BBSbase.getSTAGE2cmd(pkg, version)
            nb_target_pkgs_in_queue += 1
        else:
            if pkg in installed_pkgs:
                cmd = pkgdumps = None
                nb_skipped_pkgs += 1
            else:
                cmd = BBSbase.get_install_cmd_for_non_target_pkg(pkg)
        job = BBSbase.InstallPkg_Job(pkg, version, cmd, pkgdumps, out_dir)
        jobs.append(job)
    nb_jobs = len(jobs)
    print('OK')
    sys.stdout.flush()
    nb_not_needed = len(target_pkgs) - nb_target_pkgs_in_queue
    nb_non_target_pkgs_in_queue = nb_jobs - nb_target_pkgs_in_queue
    nb_non_target_pkgs_to_install = nb_non_target_pkgs_in_queue - \
                                    nb_skipped_pkgs
    nb_pkgs_to_install = nb_jobs - nb_skipped_pkgs
    print('BBS> Job summary:')
    print('BBS> | %d (out of %d) target pkgs are not supporting pkgs' % \
          (nb_not_needed, len(target_pkgs)))
    print('BBS> |   => no need to install them')
    print('BBS> |   => they\'re not going in the installation queue')
    print('BBS> | %d pkgs in the installation queue (all supporting pkgs):' % \
          nb_jobs)
    print('BBS> |   o %d are target pkgs' % nb_target_pkgs_in_queue)
    print('BBS> |       => will (re-)install them with \'R CMD INSTALL\'')
    print('BBS> |   o %d are non-target pkgs:' % nb_non_target_pkgs_in_queue)
    print('BBS> |     - %d are already installed' % nb_skipped_pkgs)
    print('BBS> |         => won\'t re-install them (job will be skipped)')
    print('BBS> |     - %d are not already installed' % \
          nb_non_target_pkgs_to_install)
    print('BBS> |         => will install them with')
    print('BBS> |              install.packages(pkg, repos=non_target_repos,')
    print('BBS> |                               dep=FALSE, ...)')
    print('BBS> | Total nb of packages to install: %d' % nb_pkgs_to_install)
    print('BBS>')
    job_queue = bbs.jobs.JobQueue(stage, jobs, pkg_dep_graph)
    job_queue._nb_pkgs_to_install = nb_pkgs_to_install
    return job_queue

def STAGE2_loop(job_queue, nb_cpu, out_dir):
    print('BBS> BEGIN STAGE2 loop.')
    t1 = time.time()
    if BBSvars.asynchronous_transmission:
        rdir = BBSvars.install_rdir
        products_push_cmd = make_products_push_cmd(out_dir, rdir)
        products_push_log = os.path.join(products_out_buf, 'install-push.log')
    else:
        products_push_cmd = products_push_log = None
    nb_installed = bbs.jobs.processJobQueue(job_queue, nb_cpu,
                                            BBSvars.INSTALL_timeout,
                                            products_push_cmd,
                                            products_push_log,
                                            verbose=True)
    dt = time.time() - t1
    print('BBS> END STAGE2 loop.')
    nb_jobs = len(job_queue._jobs)
    nb_pkgs_to_install = job_queue._nb_pkgs_to_install
    nb_failures = nb_pkgs_to_install - nb_installed
    print('BBS> -------------------------------------------------------------')
    print('BBS> STAGE2 SUMMARY:')
    print('BBS>   o Working dir: %s' % os.getcwd())
    print('BBS>   o %d pkg dir(s) queued and processed' % nb_jobs)
    print('BBS>   o %d pkg(s) to (re-)install: %d successes / %d failures' % \
          (nb_pkgs_to_install, nb_installed, nb_failures))
    print('BBS>   o Total time: %.2f seconds' % dt)
    print('BBS> -------------------------------------------------------------')
    return

def STAGE2():
    print('BBS> [STAGE2] STARTING STAGE2 at %s' % time.asctime())
    # We want to make sure the target repo is ready before we actually start
    # (if it's not ready yet it probably means that the prerun.sh script did
    # not finish on the main node, in which case we want to wait before we
    # sync the local meat dir with the central MEAT0 dir).
    waitForTargetRepoToBeReady()
    if not BBSvars.no_transmission:
        BBSvars.install_rdir.RemakeMe(True)
    if BBSvars.synchronous_transmission:
        out_dir = BBSvars.install_rdir
    else:
        out_dir = make_stage_out_dir('install')

    meat_path = BBSvars.meat_path
    if BBSvars.no_transmission:
        # Secondary nodes that use BBS_PRODUCT_TRANSMISSION_MODE="none"
        # are typically "external nodes" and they are not allowed to
        # rsync the meat. So they must get the meat by downloading the
        # source tarballs from BBSvars.central_base_url + '/src/contrib
        if os.path.exists(meat_path):
            bbs.fileutils.remake_dir(meat_path, ignore_errors=True)
        else:
            os.mkdir(meat_path)
        contrib_url = BBSvars.central_base_url + '/src/contrib'
        target_repo_path = os.path.join(BBSvars.work_topdir, 'target-repo')
        BBSbase.cloneCRANstylePkgRepo(contrib_url, target_repo_path,
                                      update_only=True)
        BBSbase.extractLocalCRANstylePkgRepo(target_repo_path, meat_path)
    else:
        BBSvars.MEAT0_rdir.syncLocalDir(meat_path, True)

    if BBSvars.MEAT0_type == 2:
        srcpkg_files = bbs.fileutils.listSrcPkgFiles(meat_path)
        for srcpkg_file in srcpkg_files:
            srcpkg_filepath = os.path.join(meat_path, srcpkg_file)
            BBSbase.Untar(srcpkg_filepath, meat_path)
            os.remove(srcpkg_filepath)

    if BBSvars.MEAT0_type == 3 and not BBSvars.no_transmission:
        print('BBS> [STAGE2] cd BBS_WORK_TOPDIR/gitlog')
        gitlog_path = BBSutils.getenv('BBS_GITLOG_PATH')
        BBSvars.GITLOG_rdir.syncLocalDir(gitlog_path, True)

    print('BBS> [STAGE2] cd BBS_WORK_TOPDIR/STAGE2_tmp')
    STAGE2_tmp = os.path.join(BBSvars.work_topdir, 'STAGE2_tmp')
    bbs.fileutils.remake_dir(STAGE2_tmp)
    os.chdir(STAGE2_tmp)

    # Re-create architecture-specific Renviron.site files on multi-arch
    # build machines.
    #if ('BBS_STAGE2_MODE' in os.environ and
    #  os.environ['BBS_STAGE2_MODE'] == 'multiarch' and
    #  BBSvars.buildtype == 'bioc'):
    #    CreateREnvironFiles()

    if BBSvars.buildtype in ['bioc', 'bioc-testing']:
        # Update non-target packages.
        print('BBS> [STAGE2] Update non-target packages (1st run) ...', end=' ')
        sys.stdout.flush()
        cmd = BBSbase.get_update_cmd_for_non_target_pkgs()
        bbs.jobs.runJob(cmd, 'updateNonTargetPkgs1.Rout', 3600.0)
        print('OK')
        sys.stdout.flush()

    # Extract list of target packages.
    target_pkgs = get_list_of_target_pkgs()

    # Get 'pkg_dep_graph' and 'installed_pkgs'.
    pkg_dep_graph = build_pkg_dep_graph(target_pkgs)
    installed_pkgs = get_installed_pkgs()

    print('BBS> [STAGE2] cd BBS_MEAT_PATH')
    os.chdir(meat_path)
    if BBSvars.MEAT0_type == 3 and not BBSvars.no_transmission:
        # Inject the git fields into the DESCRIPTION files. No need to do
        # this if BBS_PRODUCT_TRANSMISSION_MODE="none" because in this case
        # the DESCRIPTION files already contain those fields.
        print('BBS> [STAGE2] Injecting git fields into',
              '*/DESCRIPTION files ...', end=' ')
        for pkg in target_pkgs:
            gitlog_file = os.path.join(gitlog_path, 'git-log-%s.dcf' % pkg)
            if not os.path.exists(gitlog_file):
                print('(%s not found --> skip)' % gitlog_file, end=' ')
                continue
            desc_file = os.path.join(BBSvars.meat_path, pkg, 'DESCRIPTION')
            if not os.path.exists(desc_file):
                print('(%s not found --> skip)' % desc_file, end=' ')
                continue
            bbs.parse.injectGitFieldsIntoDESCRIPTION(desc_file, gitlog_file)
        print('OK')

    print('BBS> [STAGE2] Injecting Date/Publication into',
          '*/DESCRIPTION files ...', end=' ')
    for pkg in target_pkgs:
        desc_file = os.path.join(BBSvars.meat_path, pkg, 'DESCRIPTION')
        date = time.strftime("%Y-%m-%d")
        bbs.parse.injectPublicationDateIntoDESCRIPTION(desc_file, date)
    print('OK')

    # Then re-install the supporting packages.
    print('BBS> [STAGE2] Re-install supporting packages')
    os.chdir(meat_path)
    job_queue = prepare_STAGE2_job_queue(target_pkgs, pkg_dep_graph,
                                         installed_pkgs, out_dir)
    STAGE2_loop(job_queue, BBSvars.install_nb_cpu, out_dir)

    print('BBS> [STAGE2] cd BBS_WORK_TOPDIR/STAGE2_tmp')
    os.chdir(STAGE2_tmp)

    if BBSvars.buildtype in ['bioc', 'bioc-testing']:
        # Try again to update non-target packages (some updates could have
        # failed in the previous attempt because of dependency issues).
        print('BBS> [STAGE2] Update non-target packages (2nd run) ...', end=' ')
        sys.stdout.flush()
        cmd = BBSbase.get_update_cmd_for_non_target_pkgs()
        bbs.jobs.runJob(cmd, 'updateNonTargetPkgs2.Rout', 3600.0)
        print('OK')
        sys.stdout.flush()

    makeNodeInfo()

    print('BBS> [STAGE2] DONE at %s.' % time.asctime())
    return


##############################################################################
## STAGE3: Build the srcpkg files.
##############################################################################

def prepare_STAGE3_job_queue(pkgsrctrees, out_dir):
    print("BBS> Preparing STAGE3 job queue ...", end=" ")
    sys.stdout.flush()
    stage = 'buildsrc'
    jobs = []
    for pkgsrctree in pkgsrctrees:
        try:
            pkg = bbs.parse.get_Package_from_pkgsrctree(pkgsrctree)
            version = bbs.parse.get_Version_from_pkgsrctree(pkgsrctree)
            srcpkg_file = bbs.parse.make_srcpkg_file_from_pkgsrctree(pkgsrctree)
        except IOError:
            print("BBS>   Can't read DESCRIPTION file!")
        else:
            cmd = BBSbase.getSTAGE3cmd(pkgsrctree)
            pkgdumps_prefix = pkg + '.' + stage
            pkgdumps = BBSbase.PkgDumps(srcpkg_file, pkgdumps_prefix)
            job = BBSbase.BuildPkg_Job(pkg, version, cmd, pkgdumps, out_dir)
            jobs.append(job)
    print("OK")
    sys.stdout.flush()
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(pkgsrctrees)
    return job_queue

def STAGE3_loop(job_queue, nb_cpu, out_dir):
    print("BBS> BEGIN STAGE3 loop.")
    t1 = time.time()
    if BBSvars.asynchronous_transmission:
        rdir = BBSvars.buildsrc_rdir
        products_push_cmd = make_products_push_cmd(out_dir, rdir)
        products_push_log = os.path.join(products_out_buf, 'buildsrc-push.log')
    else:
        products_push_cmd = products_push_log = None
    nb_products = bbs.jobs.processJobQueue(job_queue, nb_cpu,
                                           BBSvars.BUILD_timeout,
                                           products_push_cmd,
                                           products_push_log,
                                           verbose=True)
    dt = time.time() - t1
    print("BBS> END STAGE3 loop.")
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print("BBS> -------------------------------------------------------------")
    print("BBS> STAGE3 SUMMARY:")
    print("BBS>   o Working dir: %s" % os.getcwd())
    print("BBS>   o %d pkg(s) listed in file BBS_CENTRAL_BASEURL/%s" % \
          (total, BBSutils.meat_index_file))
    print("BBS>   o %d pkg dir(s) queued and processed" % nb_jobs)
    print("BBS>   o %d srcpkg file(s) produced" % nb_products)
    print("BBS>   o Total time: %.2f seconds" % dt)
    print("BBS> -------------------------------------------------------------")
    return

def STAGE3():
    print("BBS> [STAGE3] STARTING STAGE3 at %s" % time.asctime())
    if BBSvars.synchronous_transmission:
        out_dir = BBSvars.buildsrc_rdir
        out_dir.RemakeMe(True)
    else:
        out_dir = make_stage_out_dir('buildsrc')

    # Even though we already generated the NodeInfo folder at end of STAGE2,
    # we generate it again now just in case we are running builds that
    # skipped STAGE2 (e.g. bioc-longtests builds).
    makeNodeInfo()
    print("BBS> [STAGE3] cd BBS_MEAT_PATH")
    target_pkgs = get_list_of_target_pkgs()
    meat_path = BBSvars.meat_path
    if BBSvars.buildtype == "bioc-longtests":
        bbs.fileutils.remake_dir(meat_path, ignore_errors=True)
        os.chdir(meat_path)
        for pkg in target_pkgs:
            rdir = BBSvars.MEAT0_rdir.subdir(pkg)
            local_dir = os.path.join(meat_path, pkg)
            rdir.syncLocalDir(local_dir, True)
    else:
        os.chdir(meat_path)
    job_queue = prepare_STAGE3_job_queue(target_pkgs, out_dir)
    STAGE3_loop(job_queue, BBSvars.buildsrc_nb_cpu, out_dir)
    print("BBS> [STAGE3] DONE at %s." % time.asctime())
    return


##############################################################################
## STAGE4: Check the srcpkg files.
##############################################################################

def prepare_STAGE4_job_queue(srcpkg_paths, out_dir):
    print("BBS> Preparing STAGE4 job queue ...", end=" ")
    sys.stdout.flush()
    stage = 'checksrc'
    jobs = []
    for srcpkg_path in srcpkg_paths:
        cmd = BBSbase.getSTAGE4cmd(srcpkg_path)
        pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
        version = bbs.parse.get_version_from_srcpkg_path(srcpkg_path)
        Rcheck_dir = pkg + '.Rcheck'
        pkgdumps_prefix = pkg + '.' + stage
        pkgdumps = BBSbase.PkgDumps(Rcheck_dir, pkgdumps_prefix)
        job = BBSbase.CheckSrc_Job(pkg, version, cmd, pkgdumps, out_dir)
        jobs.append(job)
    print("OK")
    sys.stdout.flush()
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(srcpkg_paths)
    return job_queue

def STAGE4_loop(job_queue, nb_cpu, out_dir):
    print("BBS> BEGIN STAGE4 loop.")
    t1 = time.time()
    if BBSvars.asynchronous_transmission:
        rdir = BBSvars.checksrc_rdir
        products_push_cmd = make_products_push_cmd(out_dir, rdir)
        products_push_log = os.path.join(products_out_buf, 'checksrc-push.log')
    else:
        products_push_cmd = products_push_log = None
    bbs.jobs.processJobQueue(job_queue, nb_cpu,
                             BBSvars.CHECK_timeout,
                             products_push_cmd,
                             products_push_log,
                             verbose=True)
    dt = time.time() - t1
    print("BBS> END STAGE4 loop.")
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print("BBS> -------------------------------------------------------------")
    print("BBS> STAGE4 SUMMARY:")
    print("BBS>   o Working dir: %s" % os.getcwd())
    print("BBS>   o %d srcpkg file(s) in working dir" % total)
    print("BBS>   o %d srcpkg file(s) queued and processed" % nb_jobs)
    print("BBS>   o Total time: %.2f seconds" % dt)
    print("BBS> -------------------------------------------------------------")
    return

def STAGE4():
    print("BBS> [STAGE4] STARTING STAGE4 at %s" % time.asctime())
    if BBSvars.synchronous_transmission:
        out_dir = BBSvars.checksrc_rdir
        out_dir.RemakeMe(True)
    else:
        out_dir = make_stage_out_dir('checksrc')

    print("BBS> [STAGE4] cd BBS_MEAT_PATH")
    os.chdir(BBSvars.meat_path)
    srcpkg_paths = getSrcPkgFilesFromSuccessfulSTAGE3("CHECK")
    job_queue = prepare_STAGE4_job_queue(srcpkg_paths, out_dir)
    STAGE4_loop(job_queue, BBSvars.checksrc_nb_cpu, out_dir)
    print("BBS> [STAGE4] DONE at %s." % time.asctime())
    return


##############################################################################
## STAGE5: Build the binpkg files.
##############################################################################

def prepare_STAGE5_job_queue(srcpkg_paths, out_dir):
    print("BBS> Preparing STAGE5 job queue ...", end=" ")
    sys.stdout.flush()
    stage = 'buildbin'
    jobs = []
    for srcpkg_path in srcpkg_paths:
        cmd = BBSbase.getSTAGE5cmd(srcpkg_path)
        pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
        version = bbs.parse.get_version_from_srcpkg_path(srcpkg_path)
        fileext = BBSutils.getNodeSpec(BBSvars.node_hostname, 'pkgFileExt')
        binpkg_file = "%s_%s.%s" % (pkg, version, fileext)
        pkgdumps_prefix = pkg + '.' + stage
        pkgdumps = BBSbase.PkgDumps(binpkg_file, pkgdumps_prefix)
        job = BBSbase.BuildPkg_Job(pkg, version, cmd, pkgdumps, out_dir)
        jobs.append(job)
    print("OK")
    sys.stdout.flush()
    job_queue = bbs.jobs.JobQueue(stage, jobs, None)
    job_queue._total = len(srcpkg_paths)
    return job_queue

def STAGE5_loop(job_queue, nb_cpu, out_dir):
    print("BBS> BEGIN STAGE5 loop.")
    t1 = time.time()
    if BBSvars.asynchronous_transmission:
        rdir = BBSvars.buildbin_rdir
        products_push_cmd = make_products_push_cmd(out_dir, rdir)
        products_push_log = os.path.join(products_out_buf, 'buildbin-push.log')
    else:
        products_push_cmd = products_push_log = None
    nb_products = bbs.jobs.processJobQueue(job_queue, nb_cpu,
                                           BBSvars.BUILDBIN_timeout,
                                           products_push_cmd,
                                           products_push_log,
                                           verbose=True)
    dt = time.time() - t1
    print("BBS> END STAGE5 loop.")
    nb_jobs = len(job_queue._jobs)
    total = job_queue._total
    print("BBS> -------------------------------------------------------------")
    print("BBS> STAGE5 SUMMARY:")
    print("BBS>   o Working dir: %s" % os.getcwd())
    print("BBS>   o %d srcpkg file(s) in working dir" % total)
    print("BBS>   o %d srcpkg file(s) queued and processed" % nb_jobs)
    print("BBS>   o %d binpkg file(s) produced" % nb_products)
    print("BBS>   o Total time: %.2f seconds" % dt)
    print("BBS> -------------------------------------------------------------")
    return

def STAGE5():
    print("BBS> [STAGE5] STARTING STAGE5 at %s" % time.asctime())
    if BBSvars.synchronous_transmission:
        out_dir = BBSvars.buildbin_rdir
        out_dir.RemakeMe(True)
    else:
        out_dir = make_stage_out_dir('buildbin')

    print("BBS> [STAGE5] cd BBS_MEAT_PATH")
    os.chdir(BBSvars.meat_path)
    srcpkg_paths = getSrcPkgFilesFromSuccessfulSTAGE3("BUILD BIN")
    job_queue = prepare_STAGE5_job_queue(srcpkg_paths, out_dir)
    STAGE5_loop(job_queue, BBSvars.nb_cpu, out_dir)
    print("BBS> [STAGE5] DONE at %s." % time.asctime())
    return


##############################################################################
## MAIN SECTION
##############################################################################

### Return the stages to run in one string.
### Can return special strings "all" o "all-no-bin".
def stages_to_run(argv):
    usage_msg = 'Usage:\n' + \
        '    BBS-run.py\n' + \
        'or:\n' + \
        '    BBS-run.py no-bin\n' + \
        'or:\n' + \
        '    BBS-run.py STAGEx STAGEy ...\n'
    argc = len(argv)
    if argc <= 1:
        return "all"
    arg1 = argv[1]
    if arg1 == "no-bin":
        if argc > 2:
            sys.exit(usage_msg)
        return "all-no-bin"
    stages = ""
    for stage in argv[1:]:
        if stage not in ['STAGE2', 'STAGE3', 'STAGE4', 'STAGE5']:
            print("ERROR: Invalid stage: %s" % stage)
            print()
            sys.exit(usage_msg)
        if len(stages) != 0:
            stages += " "
        stages += stage
    return stages

if __name__ == "__main__":
    stages = stages_to_run(sys.argv)
    print()
    print("BBS> ==============================================================")
    if stages in ["all", "all-no-bin"]:
        if not BBSvars.no_transmission:
            BBSvars.Node_rdir.RemakeMe(True)
        if not BBSvars.synchronous_transmission:
            bbs.fileutils.remake_dir(products_out_buf, ignore_errors=True)
    ticket = []
    ## STAGE2: preinstall dependencies
    if stages in ["all", "all-no-bin"] or "STAGE2" in stages:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE2()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE2', BBSvars.install_nb_cpu, started_at, ended_at, dt))
    ## STAGE3: build source packages
    if stages in ["all", "all-no-bin"] or "STAGE3" in stages:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE3()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE3', BBSvars.buildsrc_nb_cpu, started_at, ended_at, dt))
    ## STAGE4: check source packages
    if stages in ["all", "all-no-bin"] or "STAGE4" in stages:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE4()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE4', BBSvars.checksrc_nb_cpu, started_at, ended_at, dt))
    ## STAGE5: build bin packages
    if stages == "all" or "STAGE5" in stages:
        started_at = bbs.jobs.currentDateString()
        t1 = time.time()
        STAGE5()
        dt = time.time() - t1
        ended_at = bbs.jobs.currentDateString()
        ticket.append(('STAGE5', BBSvars.nb_cpu, started_at, ended_at, dt))
    write_BBS_EndOfRun_ticket(ticket)
