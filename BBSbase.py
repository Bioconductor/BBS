##############################################################################
##
## This file is part of the BBS software (Bioconductor Build System).
##
## Author: Hervé Pagès <hpages.on.github@gmail.com>
## Last modification: Nov 22, 2023
##

import sys
import os
import tarfile

import bbs.fileutils
import bbs.parse
import bbs.jobs
import bbs.rdir
import bbs.notify

import BBSutils
import BBSvars


def Untar(tarball, destdir=None, verbose=False):
    key = 'BBS_TAR_CMD'
    if key in os.environ and os.environ[key] != "":
        tar_cmd = os.environ[key]
        options = 'zxf'
        if verbose:
            options += 'v'
        cmd = tar_cmd + ' ' + options + ' ' + tarball
        if destdir != None:
            cmd += ' -C %s' % destdir
        bbs.jobs.doOrDie(cmd)
    else:
        ## This method doesn't restore the file permissions on Windows!
        if destdir != None:
            sys.exit("ERROR in Untar(): destdir != None is not supported")
        tar = tarfile.open(tarball, mode='r:gz')
        for tarinfo in tar:
            tar.extract(tarinfo)
        tar.close()
    return

def injectFieldsIntoMeat(meat_path, target_pkgs):
    print('BBS>   Injecting fields into',
          '%s/*/DESCRIPTION files ...' % meat_path, end=' ')
    for pkg in target_pkgs:
        desc_file = os.path.join(meat_path, pkg, 'DESCRIPTION')
        if not os.path.exists(desc_file):
            print('(%s not found --> skip)' % desc_file, end=' ')
            continue
        if BBSvars.MEAT0_type == 3:
            # Inject git fields.
            gitlog_path = BBSutils.getenv('BBS_GITLOG_PATH')
            gitlog_file = os.path.join(gitlog_path, 'git-log-%s.dcf' % pkg)
            if os.path.exists(gitlog_file):
                bbs.parse.injectGitFieldsIntoDESCRIPTION(desc_file, gitlog_file)
            else:
                print('(%s not found --> skip git fields)' % gitlog_file,
                      end=' ')
        if BBSvars.bioc_version != None:
            # Inject Repository field.
            fields = {'Repository': 'Bioconductor %s' % BBSvars.bioc_version}
            bbs.parse.inject_DCF_fields(desc_file, fields)
    print('OK')
    return

def cloneCRANstylePkgRepo(contrib_url, destdir, update_only=False):
    print('BBS>   Start cloning CRAN-style package repo %s/ to %s/ ...' % \
          (contrib_url, destdir))
    if not os.path.exists(destdir):
        os.mkdir(destdir)
    elif not update_only:
        bbs.fileutils.remake_dir(destdir, ignore_errors=True)
    print('BBS>     o', end=' ')
    sys.stdout.flush()
    PACKAGES_new_path = os.path.join(destdir, 'PACKAGES.new')
    BBSutils.downloadFile('PACKAGES', contrib_url, PACKAGES_new_path)
    PACKAGES_new = bbs.parse.parse_DCF(PACKAGES_new_path)
    PACKAGES_old_path = os.path.join(destdir, 'PACKAGES')
    if os.path.exists(PACKAGES_old_path):
        PACKAGES_old = bbs.parse.parse_DCF(PACKAGES_old_path)
        old_pkgs = {}
        for dcf_record in PACKAGES_old:
            old_pkgs[dcf_record['Package']] = dcf_record
    i = 0
    for dcf_record in PACKAGES_new:
        i += 1
        print('BBS>     o [%d/%d]' % (i, len(PACKAGES_new)), end=' ')
        sys.stdout.flush()
        pkgname = dcf_record['Package']
        if os.path.exists(PACKAGES_old_path):
            git_last_commit = dcf_record.get('git_last_commit')
            if git_last_commit != None:
                old_dcf_record = old_pkgs.get(pkgname)
                if old_dcf_record != None:
                    old_git_last_commit = old_dcf_record.get('git_last_commit')
                    if git_last_commit == old_git_last_commit:
                        print('git_last_commit (%s) for ' % git_last_commit +
                              'package %s has not changed --> skip' % pkgname)
                        continue
        version = dcf_record['Version']
        MD5sum = dcf_record['MD5sum']
        srcpkg_file = '%s_%s.tar.gz' % (pkgname, version)
        BBSutils.downloadFile(srcpkg_file, contrib_url, destdir, MD5sum)
    os.rename(PACKAGES_new_path, PACKAGES_old_path)
    print('BBS>   Done cloning CRAN-style package repo %s/ to %s/' % \
          (contrib_url, destdir))
    return PACKAGES_old_path

def extractLocalCRANstylePkgRepo(contrib_path, destdir):
    PACKAGES_path = os.path.join(contrib_path, 'PACKAGES')
    PACKAGES = bbs.parse.parse_DCF(PACKAGES_path)
    print('BBS>   Extracting the %d source tarballs in %s/' % \
          (len(PACKAGES), contrib_path))
    print('       to %s/ ...' % destdir, end=' ')
    sys.stdout.flush()
    for dcf_record in PACKAGES:
        pkgname = dcf_record['Package']
        version = dcf_record['Version']
        srcpkg_file = '%s_%s.tar.gz' % (pkgname, version)
        srcpkg_path = os.path.join(contrib_path, srcpkg_file)
        Untar(srcpkg_path, destdir)
    print('OK')
    return

# 'Rexpr' must be a single string containing an R expression. It should NOT
# contain spaces or it will break on Windows!
def Rexpr2syscmd(Rexpr):
    if sys.platform == 'win32':
        # We can't put quotes around Rexpr on Windows. This means that we
        # can't have spaces in Rexpr.
        if Rexpr.find(' ') >= 0:
            sys.exit("ERROR in Rexpr2syscmd(): 'Rexpr' contains spaces!")
        if BBSvars.rscript_cmd == None:
            syscmd = 'echo %s | %s --no-echo' % (Rexpr, BBSvars.r_cmd)
        else:
            syscmd = '%s -e %s' % (BBSvars.rscript_cmd, Rexpr)
    else:
        if BBSvars.rscript_cmd == None:
            syscmd = 'echo "%s" | %s --no-echo' % (Rexpr, BBSvars.r_cmd)
        else:
            syscmd = '%s -e "%s"' % (BBSvars.rscript_cmd, Rexpr)
    return syscmd

def get_install_cmd_for_non_target_pkg(pkg):
    Rscript_path = os.path.join(BBSvars.BBS_home, 'utils',
                                'installNonTargetPkg.R')
    # Backslahes in the path injected in 'Rexpr' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslahes.
    Rscript_path = Rscript_path.replace('\\', '/')
    if sys.platform == 'win32' and BBSvars.STAGE2_mode == 'multiarch':
        Rfuncall = "installNonTargetPkg('%s',multiArch=TRUE)" % pkg
    else:
        Rfuncall = "installNonTargetPkg('%s')" % pkg
    Rexpr = "source('%s');%s" % (Rscript_path, Rfuncall)
    return Rexpr2syscmd(Rexpr)

def get_update_cmd_for_non_target_pkgs():
    Rscript_path = os.path.join(BBSvars.BBS_home, 'utils',
                                'installNonTargetPkg.R')
    # Backslahes in the path injected in 'Rexpr' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslahes.
    Rscript_path = Rscript_path.replace('\\', '/')
    if sys.platform == 'win32' and BBSvars.STAGE2_mode == 'multiarch':
        Rfuncall = "updateNonTargetPkgs(multiArch=TRUE)"
    else:
        Rfuncall = "updateNonTargetPkgs()"
    Rexpr = "source('%s');%s" % (Rscript_path, Rfuncall)
    return Rexpr2syscmd(Rexpr)

# The <pkg>.Rcheck/ folder can be huge (several GB for some packages, even
# for some software packages!) but, fortunately, the things that we need to
# send to the central node are small.
# NOTE: Trying to remove some of the files in <pkg>.Rcheck/ with os.remove()
# can fail for some packages on Windows with an error like:
#     PermissionError: [WinError 32] The process cannot
#     access the file because it is being used by another
#     process: 'scTHI.Rcheck\\00check.log'
# Stuff to keep:
#   - '00check.log': Trying to remove this file could fail on Windows (see
#     NOTE above).
#   - '00install.out'
#   - '<pkg>-Ex.Rout'
#   - '<pkg>-Ex_i386.Rout', '<pkg>-Ex_x64.Rout': Trying to remove these files
#     could fail (see NOTE above).
#   - '<pkg>-Ex.timings'
#   - 'examples_i386/<pkg>-Ex.timings'
#   - 'examples_x64/<pkg>-Ex.timings'
#   - All the top-level files in 'tests/', 'tests_i386/', and 'tests_x64/',
#     except 'startup.Rs', and no subdirs (e.g. 'tests/testthat/' can be
#     big and is not needed).
#   - '<pkg>-manual.pdf'
def _clean_Rcheck_dir(Rcheck_dir, pkg):
    dangling_paths = []
    # Collect top-level stuff to remove.
    top_level_stuff_to_keep = ['00check.log',
                               '00install.out',
                               '%s-Ex.Rout' % pkg,
                               '%s-Ex_i386.Rout' % pkg,
                               '%s-Ex_x64.Rout' % pkg,
                               '%s-Ex.timings' % pkg,
                               'examples_i386',
                               'examples_x64',
                               'tests',
                               'tests_i386',
                               'tests_x64',
                               '%s-manual.pdf' % pkg]
    for filename in os.listdir(Rcheck_dir):
        if filename not in top_level_stuff_to_keep:
            path = os.path.join(Rcheck_dir, filename)
            dangling_paths.append(path)
    # Collect stuff to remove from 'examples_i386/' and 'examples_x64/'.
    file_to_keep = '%s-Ex.timings' % pkg
    for subdir in ['examples_i386', 'examples_x64']:
        path = os.path.join(Rcheck_dir, subdir)
        if os.path.isdir(path):
            for filename in os.listdir(path):
                if filename != file_to_keep:
                    path2 = os.path.join(path, filename)
                    dangling_paths.append(path2)
    # Collect stuff to remove from 'tests/', 'tests_i386/', and 'tests_x64/'.
    for subdir in ['tests', 'tests_i386', 'tests_x64']:
        path = os.path.join(Rcheck_dir, subdir)
        if os.path.isdir(path):
            for filename in os.listdir(path):
                path2 = os.path.join(path, filename)
                if os.path.isdir(path2) or filename == 'startup.Rs':
                    dangling_paths.append(path2)
    # Remove collected stuff.
    for path in dangling_paths:
        if os.path.isdir(path):
            bbs.fileutils.nuke_tree(path, ignore_errors=True)
        else:
            try:
                os.remove(path)
            except:
                pass
    return

def kindly_notify_us(what, e, to_addrs=None):
    if to_addrs == None:
        to_addrs = ['maintainer@bioconductor.org']
    subject = (f'[BBS] {what} failure '
               f'for {BBSvars.bioc_version} {BBSvars.buildtype} builds '
               f'on {BBSvars.node_hostname}')
    msg_body = f'{what} failed on {BBSvars.node_hostname} ' + \
               f'for the {BBSvars.bioc_version} builds ' + \
               f'with the following error:\n' + \
               f'\n' + \
               f'  -----------------------------------------------------\n' + \
               f'  {e}\n' + \
               f'  -----------------------------------------------------\n' + \
               f'\n' + \
               f'See logs in {BBSvars.work_topdir}/log/ ' + \
               f'on {BBSvars.node_hostname} for more information.'
    bbs.notify.mode = 'do-it'
    bbs.notify.sendtextmail('BBS-noreply@bioconductor.org',
                            to_addrs,
                            subject,
                            msg_body)
    return


##############################################################################
## Low-level helpers used by the getSTAGE[1-5]cmd() functions
##############################################################################

def _get_prepend_from_BBSoptions(pkgsrctree, key_prefix):
    key = key_prefix + 'prepend'
    prepend = bbs.parse.get_BBSoption_from_pkgsrctree(pkgsrctree, key)
    if sys.platform == 'win32':
        key2 = key + '.win'
        prepend_win = bbs.parse.get_BBSoption_from_pkgsrctree(pkgsrctree, key2)
        if prepend_win != None:
            prepend = prepend_win
    elif sys.platform == 'darwin':
        key2 = key + '.mac'
        prepend_mac = bbs.parse.get_BBSoption_from_pkgsrctree(pkgsrctree, key2)
        if prepend_mac != None:
            prepend = prepend_mac
    return prepend

## 2023/11/22: Not used at the moment!
def _BiocGreaterThanOrEqualTo(x, y):
    # If 'BBSvars.bioc_version' is not defined, then we assume it's the
    # latest version.
    if BBSvars.bioc_version == None:
        return True
    parts = BBSvars.bioc_version.split('.')
    x0 = int(parts[0])
    y0 = int(parts[1])
    return x0 > x or (x0 == x and y0 >= y)

def _noExampleArchs(pkgsrctree):
    archs = []
    no_examples = bbs.parse.get_BBSoption_from_pkgsrctree(
                                pkgsrctree,
                                'NoExamplesOnPlatforms')
    if no_examples == None:
        return archs
    no_examples = no_examples.replace(" ", "").split(",")
    clean = []
    for item in no_examples:
        clean.append(item.strip())
    no_examples = clean
    if 'mac' in no_examples:
        archs.append('darwin')
    if 'win' in no_examples:
        archs.append('win32')
        archs.append('win32')
    if 'win32' in no_examples:
        archs.append('win32')
    if 'win64' in no_examples:
        archs.append('win32')
    if 'linux2' in no_examples:
        archs.append('linux2')
# see
#http://stackoverflow.com/questions/2144748/is-it-safe-to-use-sys-platform-win32-check-on-64-bit-python
# to explain the above.
    return archs

def _supportedWinArchs(pkgsrctree):
    archs = []
    unsupported = bbs.parse.get_BBSoption_from_pkgsrctree(
                                pkgsrctree,
                                'UnsupportedPlatforms')
    if unsupported == None:
        unsupported = []
    else:
        unsupported = unsupported.replace(" ", "").split(",")
    if "win" in unsupported:
        return archs
    if 'win32' not in unsupported:
        archs.append("i386")
    if "win64" not in unsupported:
        archs.append("x64")
    return archs

def _get_RINSTALL_cmd0(win_archs=None):
    cmd0 = BBSvars.r_cmd
    if win_archs != None and len(win_archs) == 1:
        cmd0 += ' --arch %s' % win_archs[0]
    cmd0 += ' CMD INSTALL'
    if win_archs != None and len(win_archs) >= 1:
        if len(win_archs) == 1:
            cmd0 += ' --no-multiarch'
        else:
            cmd0 += ' --merge-multiarch'
    return cmd0

## 'srcpkg_path' must be the path to a package source tarball.
def _get_BuildBinPkg_cmd(srcpkg_path, win_archs=None):
    pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
    pkg_instdir = "%s.buildbin-libdir" % pkg
    if sys.platform != 'darwin':
        ## Generate the command for Windows or Linux. Note that this command
        ## is never needed nor used on Linux.
        cmd0 = _get_RINSTALL_cmd0(win_archs)
        cmd = '%s --build --library=%s %s' % (cmd0, pkg_instdir, srcpkg_path)
    else:
        cmd0 = os.path.join(BBSvars.BBS_home, 'utils', 'build-universal.sh')
        cmd = '%s %s %s %s' % (cmd0, srcpkg_path, BBSvars.r_cmd, pkg_instdir)
    cmd = 'rm -rf %s && mkdir %s && %s' % (pkg_instdir, pkg_instdir, cmd)
    return cmd

## Crazy long command used on the Windows builders to install "light" source
## tarballs from the target repo located on the central builder. It proceeds
## in 3 steps:
##   1. Download the "light" source tarball from the target repo.
##   2. Build the Windows binary (.zip) from the "light" source tarball.
##   3. Install the Windows binary with 'R CMD INSTALL'.
## With this approach, the multiarch installation is guaranteed to be
## atomic i.e. either the 2 archs get successfully installed or nothing
## gets installed.
## Here is what Dan's commit message says about why BBS uses this long and
## complicated compound command to install packages on Windows during STAGE2
## (commit 87822fb346e04b4301d0c2efd7ec1a2a8762e93a'):
##   Install STAGE2 target pkgs to zip+libdir first, then install
##   zip. This mitigates the problem where the INSTALL times out
##   after installing only one architecture. Now, if the install
##   times out, it has only failed to install a package to a
##   temporary libdir, and the previous installation is still
##   intact (or pkg is not installed at all), so dependent packages
##   will not complain about the timed-out package being only
##   available for one architecture.
##   We still need to figure out why mzR in particular times out
##   during INSTALL. When run manually (admittedly not during
##   peak load times) the install takes ~ 5-6 minutes, even when
##   done via the build system.
def _get_InstallPkgFromTargetRepo_cmd(pkg, version, win_archs=None):
    srcpkg_file = '%s_%s.tar.gz' % (pkg, version)
    srcpkg_url = BBSvars.Central_rdir.url + '/src/contrib/' + srcpkg_file
    zip_file = srcpkg_file.replace(".tar.gz", ".zip")
    cmd = '%s -O %s' % (BBSvars.curl_cmd, srcpkg_url) + ' && ' + \
          _get_BuildBinPkg_cmd(srcpkg_file, win_archs) + ' && ' + \
          '%s %s' % (_get_RINSTALL_cmd0(), zip_file) + ' && ' + \
          'rm %s %s' % (srcpkg_file, zip_file)
    return cmd

def _get_Rbuild_cmd(pkgsrctree):
    arch = ""
    if sys.platform == 'win32':
        win_archs = _supportedWinArchs(pkgsrctree)
        if len(win_archs) == 1:
            arch = " --arch %s" % win_archs[0]
    cmd = '%s%s CMD build' % (BBSvars.r_cmd, arch)
    if sys.platform == 'win32':
        ## Fix the permissions on Windows only.
        ## The real purpose of this is to try to work around a strange Cygwin
        ## tar problem ("file changed as we read it") observed so far on
        ## Windows Server 2008 R2 Enterprise (64-bit) only.
        ## Traversing the package source tree, with e.g. a call to
        ## 'chmod a+r <pkgsrctree> -R', just before we try to build the
        ## package seems to "fix" the state of the filesystem and to
        ## make 'tar' work again on it.
        cmd = 'chmod a+r ' + pkgsrctree + ' -R && ' + cmd
    common_opts = ["--keep-empty-dirs", "--no-resave-data"]
    if BBSvars.buildtype == "bioc-longtests":
        common_opts += ["--no-build-vignettes", "--no-manual"]
    cmd = "%s %s" % (cmd, ' '.join(common_opts))
    return cmd

def _get_Rcheck_cmd0(win_archs=None):
    cmd0 = BBSvars.r_cmd
    if win_archs != None and len(win_archs) == 1:
        cmd0 += ' --arch %s' % win_archs[0]
    cmd0 += ' CMD check'
    if win_archs != None:
        if len(win_archs) <= 1:
            cmd0 += ' --no-multiarch'
        else:
            cmd0 += ' --force-multiarch'
    return cmd0

## Note that 'R CMD check' installs the package in <pkg>.Rcheck. However,
## an undocumented 'R CMD check' feature allows one to avoid this installation
## if the package is already installed somewhere and if the output of the
## 'R CMD INSTALL' command that led to this installation was captured in a
## file. Typical use of this feature:
##   R CMD INSTALL toto_0.17.31.tar.gz >toto.install-out.txt 2>&1
##   R CMD check --install=check:toto.install-out.txt \
##               --library=path/to/R/library \
##               toto_0.17.31.tar.gz
## All there is about this is a comment in tools/R/check.R at the beginning
## of the check_install() function. Also this feature was mentioned once by
## Uwe Ligges on the R-devel mailing list:
##   https://stat.ethz.ch/pipermail/r-devel/2011-June/061377.html
## and, more recently, by Tomas Kalibera in an off-list discussion about
## 'packages writing to "library" directory during their tests' (Feb 2018).
def _get_Rcheck_cmd(pkg):
    if sys.platform != 'win32':
        win_archs = None
    else:
        if BBSvars.STAGE4_mode == 'multiarch':
            win_archs = _supportedWinArchs(pkg)
        else:
            win_archs = []
    cmd0 = _get_Rcheck_cmd0(win_archs)
    common_opts = []
    ## If the package was candidate for installation during STAGE2, there
    ## should be a <pkg>.install-out.txt file in the current working directory
    ## containing the log of the installation. In this case, we can avoid a
    ## costly re-installation by using the undocumented 'R CMD check' feature
    ## described above. This introduces 3 minor gotcha though:
    ##   1) We now rely on an documented feature.
    ##   2) The exact command used for CHECK is displayed on the build report.
    ##      Not only will this command now look cryptic to the developer but
    ##      s/he also won't be able to just copy/paste it into her/his terminal
    ##      in order to reproduce the 'R CMD check' results from the report.
    ##   3) This undocumented feature only works as expected if
    ##      <pkg>.install-out.txt and R_HOME/library/pkg match i.e. if the
    ##      latter actually contains the package installed by the command
    ##      whose output was captured in the former. This will generally be
    ##      the case unless the package got re-installed after its STAGE2
    ##      installation (which could happen e.g. if another package contains
    ##      code that calls BiocManager::install() to install a possibly
    ##      different version of the package). Unlikely but possible.
    install_out = pkg + '.install-out.txt'
    if os.path.exists(install_out):
        if BBSvars.r_libs != None:
            r_library = BBSvars.r_libs
        else:
            r_library = os.path.join(BBSvars.r_home, 'library')
        common_opts += ["--install=check:%s" % install_out,
                        "--library=%s" % r_library]
    if BBSvars.buildtype == "bioc-longtests":
        common_opts += ["--test-dir=longtests",
                        "--no-stop-on-test-error",
                        "--no-codoc",
                        "--no-examples",
                        "--no-manual",
                        "--ignore-vignettes",
                        "--check-subdirs=no"]
    else:
        ## Skip the vignette checks on Windows and Mac only, to reduce
        ## build times.
        if BBSvars.extra_check_options != None:
            common_opts += [BBSvars.extra_check_options]
        common_opts += ["--timings"]
        ## Note that sys.platform is set to 'win32' on 64-bit Windows. This
        ## means that _noExampleArchs() may not be returning useful results
        ## if the intent is to not run examples for a particular Windows
        ## sub-architecture.
        no_example_archs = _noExampleArchs(pkg)
        if sys.platform in no_example_archs:
            common_opts += ["--no-examples"]
    common_opts = ' '.join(common_opts)
    return '%s %s' % (cmd0, common_opts)

def _get_deploy_book_cmd0():
    return os.path.join(BBSvars.BBS_home, "utils", "deploy_book.py")


##############################################################################
## The getSTAGE[1-5]cmd() functions
##############################################################################
## All these functions return a single string containing a standalone command
## that could be run in a terminal. The command will be displayed on the build
## report.

## Generate the command used on each package to produce the "light" source
## tarballs.
## During STAGE1, we need to build a "light" source tarball for each package.
## By "light" here we mean that we don't care about the vignette or \Sexpr
## directives in the man pages: trying to execute the code contained in the
## vignette and/or the \Sexpr directives is too expensive (it can take a long
## time) and, most importantly, it's too risky (it can fail).
## Using 'R CMD build --no-vignettes' for building a "light" source tarball
## isn't good enough: it will still try to install the package if the man
## pages contain \Sexpr directives. Unfortunately, at this time (R 2.14),
## there doesn't seem to be any option for turning off the evaluation of the
## \Sexpr. So, for now, we build the "light" source tarball "by hand" i.e.
## we just use 'tar zcf'.
def getSTAGE1cmd(pkgsrctree):
    #cmd = _get_Rbuild_cmd(pkgsrctree) + ' --no-build-vignettes ' + pkgsrctree
    key = 'BBS_TAR_CMD'
    tar_cmd = os.environ[key]
    srcpkg_file = bbs.parse.make_srcpkg_file_from_pkgsrctree(pkgsrctree)
    cmd = '%s zcf %s %s' % (tar_cmd, srcpkg_file, pkgsrctree)
    return cmd

## Generate the command used on each package for the INSTALL stage.
def getSTAGE2cmd(pkg, version):
    if sys.platform == 'win32' and BBSvars.STAGE2_mode == 'multiarch':
        win_archs = _supportedWinArchs(pkg)
        if len(win_archs) == 2:
            # Use crazy long command for multiarch INSTALLs.
            # See _get_InstallPkgFromTargetRepo_cmd() above for more info.
            cmd = _get_InstallPkgFromTargetRepo_cmd(pkg, version, win_archs)
        else:
            # Use arch-specific INSTALL command:
            #   R --arch x64 CMD INSTALL --no-multiarch <pkg>
            # or:
            #   R --arch i386 CMD INSTALL --no-multiarch <pkg>
            cmd = '%s %s' % (_get_RINSTALL_cmd0(win_archs), pkg)
    else:
        # Use standard INSTALL command: R CMD INSTALL <pkg>
        cmd = '%s %s' % (_get_RINSTALL_cmd0(), pkg)
    prepend = _get_prepend_from_BBSoptions(pkg, 'INSTALL')
    if prepend != None and prepend != '':
        cmd = '%s %s' % (prepend, cmd)
    return cmd

## Generate the command used on each package for the BUILD stage.
def getSTAGE3cmd(pkgsrctree):
    cmd = _get_Rbuild_cmd(pkgsrctree) + ' ' + pkgsrctree
    prepend = _get_prepend_from_BBSoptions(pkgsrctree, 'BUILD')
    if prepend != None and prepend != '':
        cmd = '%s %s' % (prepend, cmd)
    return cmd

## Generate the command used on each package for the CHECK stage.
## 'srcpkg_path' must be the path to a package source tarball.
def getSTAGE4cmd(srcpkg_path):
    pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
    if BBSvars.buildtype == 'books':
        deploy_destdir = pkg + '.book'
        cmd0 = _get_deploy_book_cmd0()
        cmd = 'rm -rf %s && ' % deploy_destdir + \
              'mkdir %s && ' % deploy_destdir + \
              cmd0 + ' ' + srcpkg_path + ' ' + deploy_destdir
    else:
        cmd = _get_Rcheck_cmd(pkg) + ' ' + srcpkg_path
    prepend = _get_prepend_from_BBSoptions(pkg, 'CHECK')
    if prepend != None and prepend != '':
        cmd = '%s %s' % (prepend, cmd)
    return cmd

## Generate the command used on each package for the BUILD BIN stage.
## On Windows we use 'R CMD INSTALL --build' on the source tarball produced
## at STAGE3. Note that zipping the package installation folder located in
## R_HOME\library would avoid an extra package installation/compilation
## but would also produce a .zip file with no vignettes in it.
## 'srcpkg_path' must be the path to a package source tarball.
def getSTAGE5cmd(srcpkg_path):
    pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
    if sys.platform == 'win32' and BBSvars.STAGE5_mode == 'multiarch':
        win_archs = _supportedWinArchs(pkg)
    else:
        win_archs = None
    cmd = _get_BuildBinPkg_cmd(srcpkg_path, win_archs)
    prepend = _get_prepend_from_BBSoptions(pkg, 'BUILDBIN')
    if prepend != None and prepend != '':
        cmd = '%s %s' % (prepend, cmd)
    return cmd


##############################################################################
## Output files produced by 'R CMD build/check'.
##############################################################################

class PkgDumps:
    def __init__(self, product_path, prefix):
        self.product_path = product_path
        self.out_file = prefix + '-out.txt'
        self.MISSING_file = prefix + '-MISSING'
        self.summary_file = prefix + '-summary.dcf'
    def Push(self, destdir, exclude_product=False):
        if exclude_product or self.product_path == None:
            products_to_push = []
        else:
            if os.path.exists(self.product_path):
                if os.path.exists(self.MISSING_file):
                    os.remove(self.MISSING_file)
                products_to_push = [self.product_path]
            else:
                bbs.fileutils.touch(self.MISSING_file)
                products_to_push = [self.MISSING_file]
        products_to_push += [self.out_file, self.summary_file]
        if isinstance(destdir, bbs.rdir.RemoteDir):
            destdir.Mput(products_to_push, False, True)
        else:
            for path in products_to_push:
                BBSutils.copyTheDamnedThingNoMatterWhat(path, destdir)
        return


##############################################################################
## The Summary class is used by the _MakeSummary() method of the BuildPkg_Job
## and CheckSrc_Job classes to generate a summary.
##############################################################################

## Finally, I opted for the Append() solution to add extra stuff to the
## summary (and not for the "derive the Summary class and overwrite the
## Write() method" solution).
class Summary:
    def __init__(self, pkg, version, cmd):
        self.pkg = pkg
        self.version = version
        self.cmd = cmd
        self.tail = []
    def Append(self, field, val):
        pair = (field, val)
        self.tail.append(pair)
    def Write(self, file):
        f = open(file, 'w')
        f.write('Package: %s\n' % self.pkg)
        f.write('Version: %s\n' % self.version)
        f.write('Command: %s\n' % self.cmd)
        f.write('StartedAt: %s\n' % self.started_at)
        f.write('EndedAt: %s\n' % self.ended_at)
        f.write('EllapsedTime: %.1f seconds\n' % self.dt)
        if self.retcode == None:
            f.write('RetCode: None\n')
        else:
            f.write('RetCode: %d\n' % self.retcode)
        f.write('Status: %s\n' % self.status)
        for pair in self.tail:
            f.write('%s: %s\n' % pair)
        f.close()
        return


##############################################################################
## CORE FUNCTIONS: Called by the STAGE<N>_loop() functions (N=2,3,4,5).
##############################################################################

class InstallPkg_Job(bbs.jobs.QueuedJob):
    def __init__(self, pkg, version, cmd, pkgdumps, out_dir):
        ## Required fields
        self._name = pkg
        self._cmd = cmd
        if pkgdumps != None:
            self._output_file = pkgdumps.out_file
        else:
            self._output_file = None
        ## Additional fields
        self.pkg = pkg
        self.version = version
        self.pkgdumps = pkgdumps
        self.out_dir = out_dir
        self.summary = Summary(pkg, version, cmd)
    def RerunMe(self):
        locking_pkg = bbs.parse.extractLockingPackage(self._output_file)
        ## We re-run only if the lock was on one of the deps, but not on the
        ## package itself.
        rerun_me = locking_pkg != None and locking_pkg != self.pkg
        return rerun_me
    def _MakeSummary(self):
        self.summary.started_at = self._started_at
        self.summary.ended_at = self._ended_at
        self.summary.dt = self._t2 - self._t1
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.out_dir)
    def AfterRun(self):
        self.summary.retcode = self._retcode
        if self._retcode == 0 and \
           bbs.parse.installPkgWasOK(self._output_file, self.pkg):
            self.summary.status = 'OK'
            cumul_inc = 1
        else:
            self.summary.status = 'ERROR'
            cumul_inc = 0
        self._MakeSummary()
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        self.summary.retcode = None
        self.summary.status = 'TIMEOUT'
        self._MakeSummary()

class BuildPkg_Job(bbs.jobs.QueuedJob):
    def __init__(self, pkg, version, cmd, pkgdumps, out_dir, dont_push_product=False):
        ## Required fields
        self._name = pkg
        self._cmd = cmd
        self._output_file = pkgdumps.out_file
        ## Additional fields
        self.pkg = pkg
        self.version = version
        self.pkgdumps = pkgdumps
        self.out_dir = out_dir
        self.summary = Summary(pkg, version, cmd)
        self.dont_push_product = dont_push_product
    def _MakeSummary(self):
        self.summary.started_at = self._started_at
        self.summary.ended_at = self._ended_at
        self.summary.dt = self._t2 - self._t1
        pkg_file = self.pkgdumps.product_path
        if os.path.exists(pkg_file):
            pkg_file_size = bbs.fileutils.human_readable_size(bbs.fileutils.total_size(pkg_file), True)
        else:
            pkg_file = 'None'
            pkg_file_size = 'NA'
        self.summary.Append('PackageFile', pkg_file)
        self.summary.Append('PackageFileSize', pkg_file_size)
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.out_dir, exclude_product=self.dont_push_product)
    def AfterRun(self):
        # Avoid leaving rogue processes messing around on the build machine.
        # self._proc.pid should be already dead but some of its children might
        # still be alive. They need to die too. bbs.jobs.killProc() should work
        # on a non-existing pid and it should be able to kill all the processes
        # that were started directly or indirectly by pid.
        # This needs to happen before calling self._MakeSummary() because
        # these rogue processes can break the rsync command used by
        # self.pkgdumps.Push(self.out_dir) above by holding on some of the
        # files that need to be pushed to the central build node.
        bbs.jobs.killProc(self._proc.pid)
        self.summary.retcode = self._retcode
        pkg_file = self.pkgdumps.product_path
        if os.path.exists(pkg_file) and self._retcode == 0:
            self.summary.status = 'OK'
            cumul_inc = 1
        else:
            self.summary.status = 'ERROR'
            cumul_inc = 0
        self._MakeSummary()
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        self.summary.retcode = None
        self.summary.status = 'TIMEOUT'
        self._MakeSummary()

class CheckSrc_Job(bbs.jobs.QueuedJob):
    def __init__(self, pkg, version, cmd, pkgdumps, out_dir):
        ## Required fields
        self._name = pkg
        self._cmd = cmd
        self._output_file = pkgdumps.out_file
        ## Additional fields
        self.pkg = pkg
        self.version = version
        self.pkgdumps = pkgdumps
        self.out_dir = out_dir
        self.summary = Summary(pkg, version, cmd)
        self.warnings = 'NA'
    def _MakeSummary(self):
        self.summary.started_at = self._started_at
        self.summary.ended_at = self._ended_at
        self.summary.dt = self._t2 - self._t1
        if BBSvars.buildtype == 'books':
            deploy_destdir = self.pkgdumps.product_path
            if not os.path.exists(deploy_destdir):
                deploy_destdir = 'None'
            self.summary.Append('DeployDestDir', deploy_destdir)
        else:
            Rcheck_dir = self.pkgdumps.product_path
            if os.path.exists(Rcheck_dir):
                _clean_Rcheck_dir(Rcheck_dir, self.pkg)
            else:
                Rcheck_dir = 'None'
            self.summary.Append('CheckDir', Rcheck_dir)
        self.summary.Append('Warnings', self.warnings)
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.out_dir)
    def AfterRun(self):
        # Avoid leaving rogue processes messing around on the build machine.
        # self._proc.pid should be already dead but some of its children might
        # still be alive. They need to die too. bbs.jobs.killProc() should work
        # on a non-existing pid and it should be able to kill all the processes
        # that were started directly or indirectly by pid.
        # This needs to happen before calling self._MakeSummary() because
        # these rogue processes can break the rsync command used by
        # self.pkgdumps.Push(self.out_dir) above by holding on some of the
        # files that need to be pushed to the central build node.
        bbs.jobs.killProc(self._proc.pid)
        self.summary.retcode = self._retcode
        if self._retcode == 0:
            self.warnings = bbs.parse.countWARNINGs(self._output_file)
            if self.warnings == "0":
                self.summary.status = 'OK'
            else:
                self.summary.status = 'WARNINGS'
            cumul_inc = 1
        else:
            self.summary.status = 'ERROR'
            cumul_inc = 0
        self._MakeSummary()
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        self.summary.retcode = None
        self.summary.status = 'TIMEOUT'
        self._MakeSummary()
