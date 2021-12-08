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
import tarfile

import bbs.fileutils
import bbs.parse
import bbs.jobs
import bbs.rdir
import BBSutils
import BBSvars


def Untar(tarball, dir=None, verbose=False):
    key = 'BBS_TAR_CMD'
    if key in os.environ and os.environ[key] != "":
        tar_cmd = os.environ[key]
        options = 'zxf'
        if verbose:
            options += 'v'
        cmd = tar_cmd + ' ' + options + ' ' + tarball
        if dir != None:
            cmd += ' -C %s' % dir
        bbs.jobs.doOrDie(cmd)
    else:
        ## This method doesn't restore the file permissions on Windows!
        if dir != None:
            sys.exit("ERROR in Untar(): dir != None is not supported")
        tar = tarfile.open(tarball, mode='r:gz')
        for tarinfo in tar:
            tar.extract(tarinfo)
        tar.close()
    return

# The R expression passed thru 'Rexpr' must NOT contain spaces or it will
# break on Windows!
def Rexpr2syscmd(Rexpr):
    if BBSvars.rscript_cmd == None:
        if sys.platform == 'win32':
            syscmd = 'echo %s | %s --no-echo' % (Rexpr, BBSvars.r_cmd)
        else:
            syscmd = 'echo "%s" | %s --no-echo' % (Rexpr, BBSvars.r_cmd)
    else:
        if sys.platform == 'win32':
            syscmd = '%s -e %s' % (BBSvars.rscript_cmd, Rexpr)
        else:
            syscmd = '%s -e "%s"' % (BBSvars.rscript_cmd, Rexpr)
    return syscmd

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


##############################################################################
### Generate the system commands used for installing (STAGE2), building
### (STAGE3 and STAGE5), and checking (STAGE4) each package.
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

### 'srcpkg_path' must be the path to a package source tarball.
def _get_BuildBinPkg_cmd(srcpkg_path, win_archs=None):
    pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
    pkg_instdir = "%s.buildbin-libdir" % pkg
    if sys.platform != 'darwin':
        ## Generate the command for Windows or Linux. Note that this command
        ## is never needed nor used on Linux.
        cmd0 = _get_RINSTALL_cmd0(win_archs)
        cmd = '%s --build --library=%s %s' % (cmd0, pkg_instdir, srcpkg_path)
    else:
        cmd0 = '%s/utils/build-universal.sh' % BBSvars.BBS_home
        cmd = '%s %s %s %s' % (cmd0, srcpkg_path, BBSvars.r_cmd, pkg_instdir)
    cmd = 'rm -rf %s && mkdir %s && %s' % (pkg_instdir, pkg_instdir, cmd)
    return cmd

## Crazy long command used on the Windows builders to install target packages.
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
    curl_cmd = BBSutils.getenv('BBS_CURL_CMD')
    srcpkg_file = '%s_%s.tar.gz' % (pkg, version)
    srcpkg_url = BBSvars.Central_rdir.url + '/src/contrib/' + srcpkg_file
    zip_file = srcpkg_file.replace(".tar.gz", ".zip")
    cmd = '%s -O %s' % (curl_cmd, srcpkg_url) + ' && ' + \
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
    cmd = BBSvars.r_cmd
    if win_archs != None and len(win_archs) == 1:
        cmd += ' --arch %s' % win_archs[0]
    cmd += ' CMD check'
    if win_archs != None:
        if len(win_archs) <= 1:
            cmd += ' --no-multiarch'
        else:
            cmd += ' --force-multiarch'
    return cmd

### During STAGE1, we need to build a "light" source tarball for each package.
### By "light" here we mean that we don't care about the vignette or \Sexpr
### directives in the man pages: trying to execute the code contained in the
### vignette and/or the \Sexpr directives is too expensive (it can take a long
### time) and, most importantly, it's too risky (it can fail).
### Using 'R CMD build --no-vignettes' for building a "light" source tarball
### isn't good enough: it will still try to install the package if the man
### pages contain \Sexpr directives. Unfortunately, at this time (R 2.14),
### there doesn't seem to be any option for turning off the evaluation of the
### \Sexpr. So, for now, we build the "light" source tarball "by hand" i.e.
### we just use 'tar zcf'.
def getSTAGE1cmd(pkgsrctree):
    #cmd = _get_Rbuild_cmd(pkgsrctree) + ' --no-build-vignettes ' + pkgsrctree
    key = 'BBS_TAR_CMD'
    tar_cmd = os.environ[key]
    srcpkg_file = bbs.parse.make_srcpkg_file_from_pkgsrctree(pkgsrctree)
    cmd = '%s zcf %s %s' % (tar_cmd, srcpkg_file, pkgsrctree)
    return cmd

def get_install_cmd_for_non_target_pkg(pkg):
    script_path = os.path.join(BBSvars.BBS_home,
                               "utils",
                               "installNonTargetPkg.R")
    # Backslahes in the path injected in 'Rexpr' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslahes.
    script_path = script_path.replace('\\', '/')
    Rexpr = "source('%s');" % script_path
    if sys.platform == 'win32' and BBSvars.STAGE2_mode == 'multiarch':
        Rexpr += "installNonTargetPkg('%s',multiArch=TRUE)" % pkg
    else:
        Rexpr += "installNonTargetPkg('%s')" % pkg
    return Rexpr2syscmd(Rexpr)

def get_update_cmd_for_non_target_pkgs():
    script_path = os.path.join(BBSvars.BBS_home,
                               "utils",
                               "installNonTargetPkg.R")
    # Backslahes in the path injected in 'Rexpr' will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslahes.
    script_path = script_path.replace('\\', '/')
    Rexpr = "source('%s');" % script_path
    if sys.platform == 'win32' and BBSvars.STAGE2_mode == 'multiarch':
        Rexpr += "updateNonTargetPkgs(multiArch=TRUE)"
    else:
        Rexpr += "updateNonTargetPkgs()"
    return Rexpr2syscmd(Rexpr)

def getSTAGE2cmd(pkg, version):
    if sys.platform == 'win32':
        if BBSvars.STAGE2_mode == 'multiarch':
            win_archs = _supportedWinArchs(pkg)
        else:
            win_archs = None
        # We use a crazy long command to install target packages on a Windows
        # builder. See _get_InstallPkgFromTargetRepo_cmd() above for more info.
        cmd = _get_InstallPkgFromTargetRepo_cmd(pkg, version, win_archs)
    else:
        # Install from local source tree.
        cmd = '%s %s' % (_get_RINSTALL_cmd0(), pkg)
    return cmd

def getSTAGE3cmd(pkgsrctree):
    cmd =  _get_Rbuild_cmd(pkgsrctree) + ' ' + pkgsrctree
    prepend = _get_prepend_from_BBSoptions(pkgsrctree, 'BUILD')
    if prepend != None and prepend != '':
        cmd = '%s %s' % (prepend, cmd)
    return cmd

### Note that 'R CMD check' installs the package in <pkg>.Rcheck. However,
### an undocumented 'R CMD check' feature allows one to avoid this installation
### if the package is already installed somewhere and if the output of the
### 'R CMD INSTALL' command that led to this installation was captured in a
### file. Typical use of this feature:
###   R CMD INSTALL toto_0.17.31.tar.gz >toto.install-out.txt 2>&1
###   R CMD check --install=check:toto.install-out.txt \
###               --library=path/to/R/library \
###               toto_0.17.31.tar.gz
### All there is about this is a comment in tools/R/check.R at the beginning
### of the check_install() function. Also this feature was mentioned once by
### Uwe Ligges on the R-devel mailing list:
###   https://stat.ethz.ch/pipermail/r-devel/2011-June/061377.html
### and, more recently, by Tomas Kalibera in an off-list discussion about
### 'packages writing to "library" directory during their tests' (Feb 2018).
### 'srcpkg_path' must be the path to a package source tarball.
def getSTAGE4cmd(srcpkg_path):
    pkg = bbs.parse.get_pkgname_from_srcpkg_path(srcpkg_path)
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
        common_opts += ["--no-vignettes", "--timings"]
        ## Note that sys.platform is set to 'win32' on 64-bit Windows. This
        ## means that _noExampleArchs() may not be returning useful results
        ## if the intent is to not run examples for a particular Windows
        ## sub-architecture.
        no_example_archs = _noExampleArchs(pkg)
        if sys.platform in no_example_archs:
            common_opts += ["--no-examples"]
    common_opts = ' '.join(common_opts)
    cmd = '%s %s %s' % (cmd0, common_opts, srcpkg_path)
    prepend = _get_prepend_from_BBSoptions(pkg, 'CHECK')
    if prepend != None and prepend != '':
        cmd = '%s %s' % (prepend, cmd)
    return cmd

### On Windows we use 'R CMD INSTALL --build' on the source tarball produced
### at STAGE3. Note that zipping the package installation folder located in
### R_HOME\library would avoid an extra package installation/compilation
### but would also produce a .zip file with no vignettes in it.
### 'srcpkg_path' must be the path to a package source tarball.
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

## shutil.copy2() will fail on Windows if a process is sill holding on the
## file to copy. Similarly shutil.copytree() will fail if a process is still
## holding on a file located inside the directory to copy. This has been
## observed for example when calling shutil.copytree() on 'NetSAM.Rcheck'
## on a Windows build machine right after 'R CMD check' failed. Note that
## 'R CMD check' failed with:
##   ..
##   * checking files in 'vignettes' ... OK
##   * checking examples ... ERROR
##   Running examples in 'NetSAM-Ex.R' failed
##   Warning in file(con, "r") :
##     cannot open file 'NetSAM-Ex.Rout': Permission denied
##   Error in file(con, "r") : cannot open the connection
##   Execution halted
##
## So it failed exactly for the very reason that a process was holding on
## 'NetSAM.Rcheck\NetSAM-Ex.Rout' hence preventing 'R CMD check' from opening
## the file to parse its content for errors.
##
## Then, when almost immediately after that, BBS tried to copy 'NetSAM.Rcheck'
## with shutil.copytree(), it failed with:
##
##   [Errno 13] Permission denied: 'NetSAM.Rcheck\NetSAM-Ex.Rout'
##
## because the process holding on 'NetSAM.Rcheck\NetSAM-Ex.Rout' was still
## there!
## The magic wand is to use rsync to copy stuff. Seems to work no matter what.
def copy_the_damned_thing_no_matter_what(src, destdir):
    bbs.rdir.set_readable_flag(src)
    if sys.platform == 'win32':
        ## rsync should do it no matter what.
        src = bbs.fileutils.to_cygwin_style(src)
        destdir = bbs.fileutils.to_cygwin_style(destdir)
        cmd = '%s -rL %s %s' % (BBSvars.rsync_cmd, src, destdir)
        bbs.jobs.runJob(cmd, stdout=None, maxtime=120.0, verbose=True)
    else:
        print("BBS>   Copying %s to %s/ ..." % (src, destdir), end=" ")
        sys.stdout.flush()
        if os.path.isdir(src):
            dst = os.path.join(destdir, os.path.basename(src))
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, destdir)
        print("OK")
        sys.stdout.flush()
    return

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
                copy_the_damned_thing_no_matter_what(path, destdir)
        return


##############################################################################
### The Summary class is used by the _MakeSummary() method of the BuildPkg_Job
### and CheckSrc_Job classes to generate a summary.
##############################################################################

### Finally, I opted for the Append() solution to add extra stuff to the
### summary (and not for the "derive the Summary class and overwrite the
### Write() method" solution).
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
### CORE FUNCTIONS: Called by the STAGE<N>_loop() functions (N=2,3,4,5).
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
        self.pkgdumps.Push(self.out_dir, BBSvars.dont_push_srcpkgs)
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
        #NOT NEEDED. '00install.out' is under the '<pkg>.Rcheck' dir
        #and we already push this dir to self.out_dir as part of self.pkgdumps
        #self.install_out = os.path.join('%s.Rcheck' % pkg, '00install.out')
    def _MakeSummary(self):
        self.summary.started_at = self._started_at
        self.summary.ended_at = self._ended_at
        self.summary.dt = self._t2 - self._t1
        Rcheck_dir = self.pkgdumps.product_path
        if os.path.exists(Rcheck_dir):
            _clean_Rcheck_dir(Rcheck_dir, self.pkg)
        else:
            Rcheck_dir = 'None'
        self.summary.Append('CheckDir', Rcheck_dir)
        self.summary.Append('Warnings', self.warnings)
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.out_dir)
        ## Sometimes, '00install.out' is not generated (e.g. when some required
        ## packages are not available)
        #NOT NEEDED (see above).
        #if os.path.exists(self.install_out):
        #    self.out_dir.Put(self.install_out, True, True)
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
